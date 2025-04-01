# -*- coding: utf-8 -*-
"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import os
from time import sleep
from persepolis.scripts import logger
from persepolis.scripts.download_link import DownloadLink
from persepolis.scripts.useful_tools import muxer
try:
    from PySide6.QtCore import QThread, Signal
except:
    from PyQt5.QtCore import QThread
    from PyQt5.QtCore import pyqtSignal as Signal

try:
    from persepolis.scripts import ytdlp_downloader
except ModuleNotFoundError:
    # if youtube_dl module is not installed:
    logger.sendToLog(
        "yt-dlp is not installed.", "ERROR")


# Persepolis download audio and video separately and the muxing them :)
# VideoFinder do this job for Persepolis.
# see data_base.py for understanding the code
# we have video_finder_db_table in data base. it's contains some items that helps
# VideoFinder for managing the situation.
# video_gid >> GID of video link
# audio_gid >> GID of audio link
# video_completed >> Is video downloaded completely?
# audio_completed >> Is audio downloaded completely?
# checking >> VideoFinder must checking or not!


class VideoFinder(QThread):
    VIDEOFINDERCOMPLETED = Signal(dict)

    def __init__(self, video_finder_dictionary, main_window):
        QThread.__init__(self)
        self.main_window = main_window
        self.video_finder_dictionary = video_finder_dictionary

    # First: Download video
    # Second: Download audio
    # Third: Mux video and audio
    def run(self):
        self.video_completed = self.video_finder_dictionary['video_completed']
        self.audio_completed = self.video_finder_dictionary['audio_completed']
        self.muxing = 'no'
        self.checking = 'no'
        self.active = 'yes'

        video_gid = self.video_finder_dictionary['video_gid']
        audio_gid = self.video_finder_dictionary['audio_gid']

        # find category
        dictionary = self.main_window.persepolis_db.searchGidInDownloadTable(video_gid)
        category = dictionary['category']

        # VideoFinder handles downloads by itself, if category is "Single Downloads"
        if category == 'Single Downloads':

            # create an item for this thread in temp_db if not exists!
            try:
                video_finder_plus_gid = 'video_finder_' + str(video_gid)
                self.main_window.temp_db.insertInQueueTable(video_finder_plus_gid)
            except:
                # release lock
                self.main_window.temp_db.lock = False

            # check start time and end time
            add_link_dictionary = self.main_window.persepolis_db.searchGidInAddLinkTable(video_gid)
            start_time = add_link_dictionary['start_time']

            if self.video_completed == 'no' and start_time:

                # set start time only for video and cancel start time for audio.
                # because video will downloaded first and start time must be set for first link! not second one
                self.main_window.persepolis_db.setDefaultGidInAddlinkTable(audio_gid, start_time=True)

        # update checking status in data base for starting the job!
        self.checking = 'yes'
        self.video_finder_dictionary['checking'] = 'yes'

        self.main_window.persepolis_db.updateVideoFinderTable([self.video_finder_dictionary])

        # if category "Single Downloads" >> manage download yourself.
        # if category is not "Single Download" >> just check the status time to time and wait until download ends!
        if self.video_completed == 'no':
            if category == "Single Downloads":

                # start video downloading
                # get add_link_dictionary for video
                add_link_dictionary = self.main_window.persepolis_db.searchGidInAddLinkTable(video_gid)
                # create download_session
                video_download_session = ytdlp_downloader.Ytdp_Download(add_link_dictionary, self.main_window, video_gid)

                # add download_session and gid to download_session_dict
                download_session_dict = {'gid': video_gid,
                                         'download_session': video_download_session}

                # append download_session_dict to download_sessions_list
                self.main_window.download_sessions_list.append(download_session_dict)

                # strat download in thread
                new_download = DownloadLink(video_gid, video_download_session, self.main_window)
                self.main_window.threadPool.append(new_download)
                self.main_window.threadPool[-1].start()

            # check the download status
            # continue loop and check the download status
            # if checking == 'no' >> problem has been occurred and download has been canceled.
            while self.video_completed != 'yes' and self.checking == 'yes':

                sleep(1)

        if self.video_completed == 'yes':

            if self.video_finder_dictionary['video_completed'] == 'no':

                # update data base
                self.video_finder_dictionary['video_completed'] = 'yes'

                self.main_window.persepolis_db.updateVideoFinderTable([self.video_finder_dictionary])

            # video is downloaded completely!
            # let's start audio downloading
            if self.audio_completed == 'no':

                # if category "Single Downloads" >> start download yourself.
                # if category is not "Single Download" >> just check the status time to time
                if category == "Single Downloads":
                    # get add_link_dictionary for video
                    add_link_dictionary = self.main_window.persepolis_db.searchGidInAddLinkTable(audio_gid)
                    # create download_session
                    audio_download_session = ytdlp_downloader.Ytdp_Download(add_link_dictionary, self.main_window, audio_gid)

                    # add download_session and gid to download_session_dict
                    download_session_dict = {'gid': audio_gid,
                                             'download_session': audio_download_session}

                    # append download_session_dict to download_sessions_list
                    self.main_window.download_sessions_list.append(download_session_dict)

                    # set speed limitation of video_download_session for audio_download_session
                    # audio_download_session.sleep_for_speed_limiting = video_download_session.sleep_for_speed_limiting
                    # strat download in thread
                    new_download = DownloadLink(audio_gid, audio_download_session, self.main_window)
                    self.main_window.threadPool.append(new_download)
                    self.main_window.threadPool[-1].start()

                # check the download status
                # continue loop and check the download status
                # if checking == 'no' >> problem occurred and downloading canceled.
                while self.audio_completed != 'yes' and self.checking == 'yes':
                    sleep(1)

        self.checking = 'no'

        # lets start muxing!
        if self.video_completed == 'yes' and self.audio_completed == 'yes':

            audio_file_exists = False
            video_file_exists = False
            # wait until the data_base is updated
            while not (audio_file_exists) or not (video_file_exists):
                sleep(0.5)
                # checking for file existance
                # find file path
                video_file_dictionary = self.main_window.persepolis_db.searchGidInAddLinkTable(video_gid)
                audio_file_dictionary = self.main_window.persepolis_db.searchGidInAddLinkTable(audio_gid)

                # find inputs and output file path for ffmpeg
                video_file_path = video_file_dictionary['download_path']
                audio_file_path = audio_file_dictionary['download_path']
                video_file_exists = os.path.isfile(video_file_path)
                audio_file_exists = os.path.isfile(audio_file_path)

            self.video_finder_dictionary['audio_completed'] = 'yes'
            self.video_finder_dictionary['checking'] = 'no'
            self.video_finder_dictionary['muxing_status'] = 'started'

            self.muxing = 'started'

            # update data base
            self.main_window.persepolis_db.updateVideoFinderTable([self.video_finder_dictionary])

            # audio and video files are downloaded completely.
            # lets start muxing
            result_dictionary = muxer(self.main_window, self.video_finder_dictionary)
            error_message = result_dictionary['error']
            ffmpeg_error_message = result_dictionary['ffmpeg_error_message']

            if ffmpeg_error_message:
                logger.sendToLog('ffmpeg error: ' + str(ffmpeg_error_message), 'DOWNLOAD ERROR')

            if error_message == 'no error':
                self.video_finder_dictionary['muxing_status'] = 'complete'
                self.muxing = 'complete'
            else:
                self.video_finder_dictionary['muxing_status'] = 'error'
                self.muxing = 'error'

            # update data base
            self.main_window.persepolis_db.updateVideoFinderTable([self.video_finder_dictionary])

            complete_dictionary = {'error': error_message,
                                   'final_path': result_dictionary['final_path'],
                                   'final_size': result_dictionary['final_size'],
                                   'video_gid': self.video_finder_dictionary['video_gid'],
                                   'audio_gid': self.video_finder_dictionary['audio_gid'],
                                   'download_path': self.video_finder_dictionary['download_path'],
                                   'category': category}

            # emit error_message
            self.VIDEOFINDERCOMPLETED.emit(complete_dictionary)

        self.active = 'no'

        if category == 'Single Downloads':

            # check if user selected shutdown after download in progress window.
            shutdown_dict = self.main_window.temp_db.returnCategory(video_finder_plus_gid)
            shutdown_status = shutdown_dict['shutdown']

            if shutdown_status == 'wait':

                # it means user want to persepolis shutdown system after download.
                # write 'shutdown' value for this category in temp_db
                shutdown_dict = {'category': video_finder_plus_gid,
                                 'shutdown': 'shutdown'}
                self.main_window.temp_db.updateQueueTable(shutdown_dict)
