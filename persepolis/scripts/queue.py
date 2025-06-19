# -*- coding: utf-8 -*-

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time
from time import sleep
from persepolis.scripts import logger
from persepolis.scripts import persepolis_lib_prime
from persepolis.scripts.video_finder import VideoFinder
from persepolis.scripts.download_link import DownloadLink

try:
    from PySide6.QtCore import QThread, Signal, QCoreApplication
except:
    from PyQt5.QtCore import QThread, QCoreApplication
    from PyQt5.QtCore import pyqtSignal as Signal
try:
    from persepolis.scripts import ytdlp_downloader
except ModuleNotFoundError:
    # if youtube_dl module is not installed:
    logger.sendToLog(
        "yt-dlp is not installed.", "ERROR")


# this thread is managing queue
class Queue(QThread):
    # this signal emitted when download status of queue changes to stop
    REFRESHTOOLBARSIGNAL = Signal(str)
    NOTIFYSENDSIGNAL = Signal(list)

    def __init__(self, category, start_time, end_time, parent):
        QThread.__init__(self)
        self.category = str(category)
        self.main_window = parent
        self.start_time = start_time
        self.end_time = end_time

    def run(self):
        self.start = True
        self.stop = False
        self.limit_changed = False
        self.after = False
        self.break_for_loop = False

        queue_counter = 0

        # this list contains gid_list of all active video finder in queue.
        video_finder_list = []

        # queue repeats 5 times!
        # and every time loads queue list again!
        # It is helps for checking new downloads in queue
        # and retrying for failed downloads.
        for counter in range(5):

            # read downloads information from data base
            download_table_dict = self.main_window.persepolis_db.returnItemsInDownloadTable(self.category)
            category_table_dict = self.main_window.persepolis_db.searchCategoryInCategoryTable(self.category)

            gid_list = category_table_dict['gid_list']

            # sort downloads top to the bottom of the list OR bottom to the top
            if not (self.main_window.reverse_checkBox.isChecked()):
                gid_list.reverse()

            # check that if user set start time
            if self.start_time and counter == 0:

                # find first download
                # set start time for first download in queue
                # status of first download must not be complete
                for gid in gid_list:

                    # get download information dictionary
                    dictionary = download_table_dict[gid]

                    # find status of download
                    status = dictionary['status']

                    if status != 'complete':
                        # We find first item! GREAT!
                        add_link_dict = {'gid': gid}

                        # set start_time for this download
                        add_link_dict['start_time'] = self.start_time

                        # write changes in data base
                        self.main_window.persepolis_db.updateAddLinkTable([add_link_dict])

                        # delete add_link_dict
                        del add_link_dict

                        # job is done! break the loop
                        break

            for gid in gid_list:
                # if gid is related to video finder, so start  Video Finder thread for checking status
                # check video_finder_threads_dict, perhaps a thread started before for this gid
                if (gid in self.main_window.all_video_finder_gid_list):
                    video_finder_link = True

                    video_finder_dictionary = self.main_window.persepolis_db.searchGidInVideoFinderTable(gid)

                    if video_finder_dictionary['video_gid'] not in self.main_window.video_finder_threads_dict.keys():

                        # start new video finder thread
                        video_finder_gid_list = [video_finder_dictionary['video_gid'],
                                                 video_finder_dictionary['audio_gid']]

                        new_video_finder = VideoFinder(video_finder_dictionary, self.main_window)
                        self.main_window.threadPool.append(new_video_finder)
                        self.main_window.threadPool[-1].start()
                        self.main_window.threadPool[-1].VIDEOFINDERCOMPLETED.connect(self.main_window.videoFinderCompleted)

                        # add thread to video_finder_threads_dict
                        self.main_window.video_finder_threads_dict[video_finder_dictionary['video_gid']] = new_video_finder

                        video_finder_list.append(video_finder_gid_list)
                else:
                    video_finder_link = False

                add_link_dict = {'gid': gid}

                # find download information
                dictionary = download_table_dict[gid]

                # if download was completed, continue the loop
                # with the next iteration of the loop!
                # We don't want to download it two times :)
                if dictionary['status'] == 'complete':
                    continue

                queue_counter = queue_counter + 1

                # change status of download to waiting
                status = 'waiting'
                dictionary['status'] = status

                if self.end_time:

                    # it means user was set end time for download
                    # set end_hour and end_minute
                    add_link_dict['end_time'] = self.end_time

                # user can set sleep time between download items in queue.
                # see preferences window!
                # find wait_queue value
                wait_queue_list = self.main_window.persepolis_setting.value('settings/wait-queue')
                wait_queue_hour = int(wait_queue_list[0])
                wait_queue_minute = int(wait_queue_list[1])

                # check if user set sleep time between downloads in queue in setting window.
                # if queue_counter is 1 , it means we are in the first download item in queue.
                # and no need to wait for first item.
                if (wait_queue_hour != 0 or wait_queue_minute != 0) and queue_counter != 1:
                    now_time_hour = int(time.strftime("%H"))
                    now_time_minute = int(time.strftime("%M"))
                    now_time_second = int(time.strftime("%S"))

                    # add extra minute if we are in second half of minute
                    if now_time_second > 30:
                        now_time_minute = now_time_minute + 1

                    # hour value can not be more than 23 and minute value can not be more than 59.
                    sigma_minute = wait_queue_minute + now_time_minute
                    sigma_hour = wait_queue_hour + now_time_hour
                    if sigma_minute > 59:
                        sigma_minute = sigma_minute - 60
                        sigma_hour = sigma_hour + 1

                    if sigma_hour > 23:
                        sigma_hour = sigma_hour - 24

                    # setting sigma_hour and sigma_minute for download's start time!
                    add_link_dict['start_time'] = str(sigma_hour) + ':' + str(sigma_minute)

                # write changes in data base
                self.main_window.persepolis_db.updateAddLinkTable([add_link_dict])
                add_link_dict = self.main_window.persepolis_db.searchGidInAddLinkTable(gid)

                if video_finder_link:
                    # create video download_session
                    download_session = ytdlp_downloader.Ytdp_Download(add_link_dict, self.main_window, gid)
                else:
                    # create download_session
                    download_session = persepolis_lib_prime.Download(add_link_dict, self.main_window, gid)

                    # check limit speed value
                    download_session.limitSpeed(self.main_window.limit_dial.value())

                # add download_session and gid to download_session_dict
                download_session_dict = {'gid': gid,
                                         'download_session': download_session}

                # append download_session_dict to download_sessions_list
                self.main_window.download_sessions_list.append(download_session_dict)

                # strat download in thread
                new_download = DownloadLink(gid, download_session, self.main_window)
                self.main_window.threadPool.append(new_download)
                self.main_window.threadPool[-1].start()

                # delete add_link_dict
                del add_link_dict
                sleep(3)

                # continue loop until download has finished
                while status == 'downloading' or status == 'waiting' or status == 'paused' or status == 'scheduled':

                    sleep(1)
                    dictionary = self.main_window.persepolis_db.searchGidInDownloadTable(gid)

                    status = dictionary['status']

                    if status == 'error':
                        error = 'error'
                        # write error_message in log file
                        error_message = 'Download failed - GID : '\
                            + str(gid)\
                            + '- Message : '\
                            + error

                        logger.sendToLog(error_message, 'DOWNLOAD ERROR')

                    elif status == 'complete':
                        complete_message = 'Download complete - GID : '\
                            + str(gid)

                        # write in log the complete_message
                        logger.sendToLog(complete_message, 'DOWNLOADS')

                        # check that is this related to video finder thread or not.
                        if gid in self.main_window.all_video_finder_gid_list:

                            # find related thread
                            for list in video_finder_list:

                                if gid in list:

                                    video_gid = list[0]

                                    if video_gid in self.main_window.video_finder_threads_dict:
                                        video_finder_thread = self.main_window.video_finder_threads_dict[video_gid]

                                        # check the video and audio and muxing_status
                                        if video_finder_thread.video_completed == 'yes' and video_finder_thread.audio_completed == 'yes':

                                            # wait until end of muxing
                                            while video_finder_thread.active == 'yes':

                                                sleep(0.5)

                                break

                    if self.stop:
                        # it means user stopped queue
                        # search gid in download_sessions_list
                        for download_session_dict in self.main_window.download_sessions_list:
                            if download_session_dict['gid'] == gid:
                                # stop download
                                download_session_dict['download_session'].downloadStop()
                                break

                    if status == 'downloading' and self.limit_changed:
                        # It means user want to limit download speed
                        # get limitation value
                        limit_value = self.main_window.limit_dial.value()

                        # apply limitation
                        for download_session_dict in self.main_window.download_sessions_list:
                            if download_session_dict['gid'] == gid:

                                download_session_dict['download_session'].limitSpeed(limit_value)
                                break

                        # done!
                        self.limit_changed = False

                # it means queue stopped at end time or user stopped queue
                if status == 'stopped':

                    for video_finder_gid_list in video_finder_list:

                        video_gid = video_finder_gid_list[0]

                        video_finder_dictionary = self.main_window.persepolis_db.searchGidInVideoFinderTable(video_gid)

                        if video_finder_dictionary:

                            # tell video finder thread to stop checking
                            if video_finder_dictionary['video_completed'] == 'no' or video_finder_dictionary['audio_completed'] == 'no':

                                video_finder_dictionary['checking'] = 'no'
                                self.main_window.persepolis_db.updateVideoFinderTable([video_finder_dictionary])

                                video_finder_thread = self.main_window.video_finder_threads_dict[video_gid]
                                video_finder_thread.checking = 'no'

                            elif not (self.stop) and self.after and video_finder_dictionary['muxing_status'] == 'started':
                                # downloads were completed and video finder started Muxing
                                # wait until the end of muxing
                                # don't turn of the computer.
                                # video finder will be deleted from data base when muxing ended.
                                # so check data base every second

                                video_finder_thread = self.main_window.video_finder_threads_dict[video_finder_dictionary['video_gid']]

                                while video_finder_thread.active == 'yes':
                                    sleep(1)

                    if self.stop and self.after:
                        # It means user activated shutdown before and now user
                        # stopped queue . so after download must be canceled
                        self.main_window.after_checkBox.setChecked(False)

                    self.stop = True
                    self.limit_changed = False

                    # it means that break outer "for" loop
                    self.break_for_loop = True

                    if str(self.main_window.category_tree.currentIndex().data()) == str(self.category):
                        self.REFRESHTOOLBARSIGNAL.emit(self.category)

                    # show notification
                    self.NOTIFYSENDSIGNAL.emit([QCoreApplication.translate("mainwindow_src_ui_tr", "Persepolis"),
                                                QCoreApplication.translate("mainwindow_src_ui_tr", "Queue Stopped!"),
                                                10000, 'no'])

                    # write message in log
                    logger.sendToLog('Queue stopped', 'DOWNLOADS')

                    break

            if self.break_for_loop:
                break

        if self.start:
            # if queue finished :
            self.start = False

            # this section is sending shutdown signal to the shutdown script(if user
            # select shutdown for after download)
            if self.after:
                # write 'shutdown' value for this category in temp_db
                shutdown_dict = {'category': self.category, 'shutdown': 'shutdown'}
                self.main_window.temp_db.updateQueueTable(shutdown_dict)

                # show a notification about system is shutting down now!
                self.NOTIFYSENDSIGNAL.emit([QCoreApplication.translate("mainwindow_src_ui_tr", 'Persepolis is shutting down'),
                                            QCoreApplication.translate("mainwindow_src_ui_tr", 'your system in 20 seconds'),
                                            15000, 'warning'])

            # show notification for queue completion
            self.NOTIFYSENDSIGNAL.emit([QCoreApplication.translate("mainwindow_src_ui_tr", "Persepolis"),
                                        QCoreApplication.translate("mainwindow_src_ui_tr", 'Queue completed!'),
                                        10000, 'queue'])

            # write a message in log
            logger.sendToLog('Queue completed', 'DOWNLOADS')

            self.stop = True
            self.limit_changed = False
            self.after = False

            if str(self.main_window.category_tree.currentIndex().data()) == str(self.category):
                self.REFRESHTOOLBARSIGNAL.emit(self.category)
