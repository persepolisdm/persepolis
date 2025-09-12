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
import libtorrent
import ast
import threading
from persepolis.scripts.useful_tools import readCookieJar
from persepolis.scripts.osCommands import makeDirs, moveFileOrFolder
from pathlib import Path
from persepolis.scripts.useful_tools import convertTime, humanReadableSize, freeSpace, returnNewFileName
import time
import os
from persepolis.scripts import logger


class TorrentFile():
    def __init__(self, torrent_file_path):
        self.torrent_file_path = Path(torrent_file_path)

    def info(self):
        try:
            info = libtorrent.torrent_info(self.torrent_file_path.__fspath__())
            error = ''
        except Exception as e:
            info = None
            error = str(e)

        return info, error

    def name(self, info):
        torrent_name = info.name()
        if torrent_name:
            return torrent_name
        else:
            return self.filesList(info)[0]

    def filesList(self, info):
        files_list = []
        files = info.files()
        for idx in range(files.num_files()):
            file_path = files.file_path(idx)
            file_size = files.file_size(idx)
            files_list.append([file_path, file_size, idx])

        # Check if we have a file or a folder
        is_in_folder = False
        for i in range(files.num_files()):
            rel = files.file_path(i)
            is_in_folder = bool(os.path.dirname(rel))
            if is_in_folder:
                break

        return files.name(), files_list, is_in_folder

    # Calculate total size of selected files.
    def totalDownloadSize(self, files_list, selected_files_index):
        total_size = 0
        for file in files_list:
            if file[2] in selected_files_index:
                total_size = total_size + file[1]

        return total_size


class TorrentDownload():
    def __init__(self, add_link_dictionary, main_window, gid):
        self.add_link_dictionary = add_link_dictionary
        self.main_window = main_window
        self.gid = gid
        # torrent file path has been saved as link key in add_link_dictionary
        self.torrent_file_path = add_link_dictionary['link']
        self.name = add_link_dictionary['out']
        self.download_path = add_link_dictionary['download_path']
        self.ip = add_link_dictionary['ip']
        self.port = add_link_dictionary['port']
        self.proxy_user = add_link_dictionary['proxy_user']
        self.proxy_passwd = add_link_dictionary['proxy_passwd']
        self.proxy_type = add_link_dictionary['proxy_type']
        self.download_user = add_link_dictionary['download_user']
        self.download_passwd = add_link_dictionary['download_passwd']
        self.header = add_link_dictionary['header']
        self.user_agent = add_link_dictionary['user_agent']
        self.load_cookies = add_link_dictionary['load_cookies']
        self.referer = add_link_dictionary['referer']
        self.start_time = add_link_dictionary['start_time']
        self.end_time = add_link_dictionary['end_time']
        self.listening_interface = '0.0.0.0:6890'
        # download_status can be in waiting, downloading, stop, error, paused
        self.download_status = 'waiting'
        # this flag notify that download finished(stopped, complete or error)
        # in this situation download status must be written to the database
        # None means, Download not finished yet.
        # False meanse, Download has been finished, but download status must be written to the database
        # True meanse, Download status has been written to the database
        self.write_it_to_the_database = None
        self.handler = None
        self.thread_list = []
        self.download_percent = 0
        self.number_of_peers = 0
        self.error_message = ''
        self.downloaded_size = 0
        self.total_size = 0
        self.eta = '0'
        self.download_speed_str = '0'
        self.is_dir = False
        # current file or folder path of downloaded torrent.
        self.f_path = os.path.join(self.download_path, self.name)
        self.download_progress_per_file_list = []

    # Initialize session
    def createSession(self):
        # Create a session and add settings
        session_settings = {'listen_interfaces': self.listening_interface}
        self.libtorrent_session = libtorrent.session(session_settings)

        torrent_file = TorrentFile(self.torrent_file_path)
        info, error = torrent_file.info()

        # Create a dictionary for session parameters.
        # This dictionary will be passe to torrent handle.
        session_parameters = {'ti': info}

        # check if user set proxy
        if self.ip:

            if self.proxy_type == 'socks5':
                proxy_type = libtorrent.proxy_type_t.socks5
            elif self.proxy_type == 'http':
                proxy_type = libtorrent.proxy_type_t.http

            # set proxy to the session
            self.libtorrent_session.set_proxy(proxy_type, self.ip, self.port, self.proxy_user, self.proxy_passwd)

        # set user_agent
        if self.user_agent:
            # setting user_agent to the session
            session_parameters['user_agent'] = self.user_agent

        # set cookies
        if self.load_cookies:
            jar = readCookieJar(self.load_cookies)
            if jar:
                session_parameters['cookies'] = jar

        # Create download_path if not existed
        try:
            makeDirs(self.download_path)
        except:
            pass

        # set storage mode
        session_parameters['storage_mode'] = libtorrent.storage_mode_t.storage_mode_allocate

        # Get files index that must be downloaded from data base
        parameters_dict_srt = self.main_window.persepolis_db.searchGidInTorrentTable(self.gid)['parameters_dict']
        parameters_dict = ast.literal_eval(parameters_dict_srt)
        self.files_index_list = parameters_dict['files']

        # Set priorities: 0 = do not download, 1 = normal priority
        number_of_files = info.num_files()
        priority_list = [0] * number_of_files
        for index in self.files_index_list:
            priority_list[index] = 1

        session_parameters['file_priorities'] = priority_list

        # get files list
        name, self.files_list, self.is_dir = torrent_file.filesList(info)
        self.total_size = torrent_file.totalDownloadSize(self.files_list, self.files_index_list)

        # If torrent is a folder, and user selected default download path
        # change download path to ~/Downloads/Persepols/Torrent folders
        if self.is_dir and self.main_window.persepolis_setting.value('settings/download_path') == self.download_path:
            self.download_path = os.path.join(self.download_path, 'Torrent folders')
            self.f_path = os.path.join(self.download_path, self.name)

            # update download_path in addlink_db_table
            add_link_dictionary = self.main_window.persepolis_db.searchGidInAddLinkTable(self.gid)
            add_link_dictionary['download_path'] = self.download_path
            self.main_window.persepolis_db.updateAddLinkTable([add_link_dictionary])

        # set download path
        session_parameters['save_path'] = self.download_path

        return session_parameters

    # Check if enough free space is available or not
    def checkFreeSpace(self, total_size):
        free_space = freeSpace(self.download_path)
        enough_free_space = False
        if free_space:
            if free_space >= total_size:
                enough_free_space = True
            else:
                enough_free_space = False

        return enough_free_space

    # This method returns data and time in string format
    # for example >> 2017/09/09 , 13:12:26
    def nowDate(self):
        date = time.strftime("%Y/%m/%d , %H:%M:%S")
        return date

    def sigmaTime(self, time):
        hour, minute = time.split(":")
        return (int(hour) * 60 + int(minute))

    # nowTime returns now time in HH:MM format!
    def nowTime(self):
        now_time = time.strftime("%H:%M")
        return self.sigmaTime(now_time)

    # this method creates sleep time,if user sets "start time" for download.
    def startTime(self):
        # write some messages
        logger.sendToLog("Download starts at " + self.start_time + ' - GID: ' + self.gid, "DOWNLOADS")

        # start_time that specified by user
        sigma_start = self.sigmaTime(self.start_time)

        # get current time
        sigma_now = self.nowTime()

        # this loop is continuing until download time arrival!
        while sigma_start != sigma_now and self.download_status == 'scheduled':
            time.sleep(2.1)
            sigma_now = self.nowTime()

    # This method will stop the download when the end_time is reached.
    def endTime(self):
        logger.sendToLog("End time is activated: " + self.end_time + ' - GID: ' + self.gid, "DOWNLOADS")
        sigma_end = self.sigmaTime(self.end_time)

        # get current time
        sigma_now = self.nowTime()

        # while current time is not equal to end_time, continue the loop
        while sigma_end != sigma_now and (self.download_status not in ['stopped', 'error']):
            # get current time
            sigma_now = self.nowTime()
            time.sleep(2.1)

        # Time is up!
        if self.download_status not in ['stopped', 'error']:
            logger.sendToLog("Time is up! - GID:" + self.gid, "DOWNLOADS")

            # stop download
            self.downloadStop()

            # job is done so change end_time value to None in data_base
            self.main_window.persepolis_db.setDefaultGidInAddlinkTable(self.gid, end_time=True)

    # this method runs endTime in a thread.
    def runEndTimeThread(self):
        end_time_thread = threading.Thread(
            target=self.endTime)
        end_time_thread.setDaemon(True)
        end_time_thread.start()
        self.thread_list.append(end_time_thread)

    def createHandler(self, parameters):
        self.handler = self.libtorrent_session.add_torrent(parameters)

    # this method checks and manages download progress.
    def checkDownloadProgress(self):
        logger.sendToLog("Download starts! - GID:" + self.gid, "DOWNLOADS")
        stalled = False
        # Run this loop until the download is finished.
        while (self.download_status == 'downloading' or self.download_status == 'paused'):
            # get download status
            status = self.handler.status()
            download_status = status.state

            # Calculate download percent
            self.download_percent = int(status.progress * 100)

            # downloded size
            self.downloaded_size = status.total_wanted_done

            # get number of peers
            self.number_of_peers = status.num_peers

            # get download path
            self.f_path = status.save_path
            # ETA
            # remaining bytes for wanted data
            left = max(0, status.total_wanted - status.total_wanted_done)

            # download_rate is bytes/sec
            dl = max(0.0001, status.download_rate)   # avoid division by zero

            eta_seconds = left / dl
            self.eta = convertTime(eta_seconds)

            download_speed, speed_unit = humanReadableSize(dl, 'speed')
            self.download_speed_str = (str(download_speed) + " " + speed_unit + "/s")

            # get downloaded size for every file.
            file_progress = self.handler.file_progress()
            _list = []
            for file_list in self.files_list:
                index = file_list[2]

                # get download information JUST for file in priority_list
                if index in self.files_index_list:
                    downloaded_from_file = file_progress[index]
                    file_size = file_list[1]

                    # file_name
                    file_path = Path(file_list[0])
                    file_name = file_path.name
                    _list.append([file_name, downloaded_from_file, file_size])

            self.download_progress_per_file_list = _list

            time.sleep(1)

            # Check if download complete.
            # consider seeding when state == seeding or progress == 1.0
            if download_status == libtorrent.torrent_status.seeding or status.progress >= 1.0:
                # Download complete!
                self.download_status = 'complete'

            # if download_status == libtorrent.torrent_status.paused:
            #     self.download_status = 'paused'
            #
            # if download_status == libtorrent.torrent_status.downloading and status.download_rate > 0:
            #     self.download_status = 'downloading'
            #
            # Handle alerts (async messages, including errors)
            alerts = self.libtorrent_session.pop_alerts()
            for a in alerts:
                # error-category alerts
                msg = None
                if a.category() & libtorrent.alert.category_t.error_notification:
                    try:
                        msg = a.message()
                    except Exception:
                        msg = str(a)
                    # specific torrent errors may be torrent_error_alert
                    if isinstance(a, libtorrent.torrent_error_alert):
                        try:
                            msg = "  torrent: " + a.handle.name() + " what: " + a.what()
                        except Exception:
                            pass

                if msg:
                    logger.sendToLog(msg, 'INFO')
            # Immediate per-torrent error check (preferred)
            has_err = getattr(status, "has_error", False)
            err_msg = None
            if has_err:
                err_msg = getattr(status, "error", None) or "unknown torrent error"
            else:
                # treat errc non-zero as error
                if hasattr(status, "errc"):
                    try:
                        val = status.errc.value()
                    except Exception:
                        try:
                            val = int(status.errc)
                        except Exception:
                            val = 0
                    if val != 0:
                        try:
                            err_msg = status.errc.message()
                        except Exception:
                            err_msg = str(status.errc)

            if err_msg:
                logger.sendToLog(err_msg, 'DOWNLOAD ERROR')
                self.download_status = 'error'
                self.error_message = err_msg

        self.number_of_peers = 0
        if self.download_status == 'complete':

            logger.sendToLog('Download complete. - GID: ' + self.gid, 'DOWNLOADS')
            self.download_percent = 100
            self.eta = '0s'

        elif self.download_status == 'error':
            if stalled:
                self.error_message = "download stalled (no peers or no rate)"

            logger.sendToLog('Download Error - GID: ' + self.gid, 'DOWNLOADS')

        elif self.download_status == 'stopped':

            logger.sendToLog('Download stopped. - GID: ' + self.gid, 'DOWNLOADS')

    # this method starts download
    def start(self):
        # create new download session.
        session_parameters = self.createSession()

        # update status and last_try_date in data_base
        if self.start_time:
            self.download_status = "scheduled"
        else:
            self.download_status = "waiting"

        # get last_try_date
        now_date = self.nowDate()

        # update data_base
        dict_ = {'gid': self.gid, 'status': self.download_status, 'last_try_date': now_date}
        self.main_window.persepolis_db.updateDownloadTable([dict_])

        # call startTime if start_time is available
        # startTime creates sleep loop if user set start_time
        # see startTime method for more information.
        if self.start_time:
            self.startTime()

            # now startTime work is done! update data_base
            # if download stopped by user don't update data_base
            if self.download_status == "scheduled":
                # set start_time value to None in data_base!
                self.main_window.persepolis_db.setDefaultGidInAddlinkTable(self.gid, start_time=True)

        if self.download_status != 'stopped':
            # if user set end_time
            if self.end_time:
                self.runEndTimeThread()

            enough_free_space = self.checkFreeSpace(self.total_size)
            if self.download_status != 'stopped':
                self.download_status = 'downloading'

                if enough_free_space:
                    self.createHandler(session_parameters)
                    self.checkDownloadProgress()
                else:
                    self.download_status = 'error'

            self.close()

        else:
            # if start_time_status is "stopped" it means download Canceled by user
            logger.sendToLog("Download Canceled", "DOWNLOADS")

    # Pause download
    def downloadPause(self):
        self.handler.pause()
        self.download_status = 'paused'

    # Stop download
    def downloadStop(self):
        self.libtorrent_session.remove_torrent(self.handler)
        self.download_status = 'stopped'

    def downloadUnpause(self):
        self.handler.resume()
        self.download_status = 'downloading'

    # This method returns download status
    def tellStatus(self):
        downloaded_size, downloaded_size_unit = humanReadableSize(self.downloaded_size)
        total_size, total_size_unit = humanReadableSize(self.total_size)

        if self.eta == '0s':
            self.eta = ''

        # return information in dictionary format
        download_info = {
            'gid': self.gid,
            'file_name': self.name,
            'status': self.download_status,
            'size': str(total_size) + ' ' + total_size_unit,
            'downloaded_size': str(downloaded_size) + ' ' + downloaded_size_unit,
            'percent': str(self.download_percent) + '%',
            'connections': str(self.number_of_peers),
            'rate': self.download_speed_str,
            'estimate_time_left': self.eta,
            'link': self.torrent_file_path,
            'error': self.error_message,
            'download_progress_per_file_list': self.download_progress_per_file_list
        }

        return download_info

    def close(self):
        # if download complete
        if self.download_status == 'complete':

            # if user specified download_path is equal to persepolis_setting download_path,
            # then subfolder must added to download path.
            if not (self.is_dir) and self.main_window.persepolis_setting.value('settings/download_path') == self.download_path:

                # return new download_path according to file extension.
                self.f_path = os.path.join(self.download_path, self.name)
                new_download_path = self.findDownloadPath(
                    self.f_path, self.download_path, self.main_window.persepolis_setting.value('settings/subfolder'))

                self.f_path = self.downloadCompleteAction(new_download_path)
            elif self.is_dir:
                self.f_path = os.path.join(self.download_path, self.name)

            # update download_path in addlink_db_table
            add_link_dictionary = self.main_window.persepolis_db.searchGidInAddLinkTable(self.gid)

            add_link_dictionary['download_path'] = self.f_path
            self.main_window.persepolis_db.updateAddLinkTable([add_link_dictionary])

        # ask threads for exiting.
        for thread in self.thread_list:
            thread.join()

        self.write_it_to_the_database = False
        logger.sendToLog("libtorrent_downloader is closed!", 'DOWNLOADS')

        # remove it from download_sessions_list when download status has been written to the database.
        for download_session_dict in self.main_window.download_sessions_list:
            if download_session_dict['gid'] == self.gid:

                # Wait until the information is written to the database.
                while self.write_it_to_the_database is False:
                    time.sleep(0.1)

                # remove item
                self.main_window.download_sessions_list.remove(download_session_dict)

        # remove gid from single_video_link_gid_list
        if self.gid in self.main_window.torrent_gid_list:
            self.main_window.torrent_gid_list.remove(self.gid)

        try:
            self.libtorrent_session.remove_torrent(self.handler)
        except Exception as e:
            print(str(e))

    # download complete actions!
    # this method is returning file_path of file in the user's download folder
    # and move downloaded file after download completion.
    def downloadCompleteAction(self, new_download_path):

        # rename file if file already existed
        self.name = returnNewFileName(new_download_path, self.name)
        new_file_path = os.path.join(new_download_path, self.name)

        # move the file to the download folder
        move_answer = moveFileOrFolder(str(self.f_path), str(new_file_path), new_path_type='file')

        if not (move_answer):
            # write error message in log
            logger.sendToLog('Persepolis can not move file' + ' - GID: ' + self.gid, "ERROR")
            new_file_path = self.f_path

        return str(new_file_path)

    # this function returns folder of download according to file extension
    def findDownloadPath(self, file_name, download_path, subfolder):

        file_name_split = file_name.split('.')
        file_extension = file_name_split[-1]

        # convert extension letters to lower case
        # for example "JPG" will be converted in "jpg"
        file_extension = file_extension.lower()

        # remove query from file_extension if existed
        # if '?' in file_extension, then file_name contains query components.
        if '?' in file_extension:
            file_extension = file_extension.split('?')[0]

        # audio formats
        audio = ['act', 'aiff', 'aac', 'amr', 'ape', 'au', 'awb', 'dct', 'dss', 'dvf', 'flac', 'gsm', 'iklax', 'ivs', 'm4a',
                 'm4p', 'mmf', 'mp3', 'mpc', 'msv', 'ogg', 'oga', 'opus', 'ra', 'raw', 'sln', 'tta', 'vox', 'wav', 'wma', 'wv']

        # video formats
        video = ['3g2', '3gp', 'asf', 'avi', 'drc', 'flv', 'm4v', 'mkv', 'mng', 'mov', 'qt', 'mp4', 'm4p', 'mpg', 'mp2',
                 'mpeg', 'mpe', 'mpv', 'm2v', 'mxf', 'nsv', 'ogv', 'rmvb', 'roq', 'svi', 'vob', 'webm', 'wmv', 'yuv', 'rm']

        # document formats
        document = ['doc', 'docx', 'html', 'htm', 'fb2', 'odt', 'sxw', 'pdf', 'ps', 'rtf', 'tex', 'txt', 'epub', 'pub'
                    'mobi', 'azw', 'azw3', 'azw4', 'kf8', 'chm', 'cbt', 'cbr', 'cbz', 'cb7', 'cba', 'ibooks', 'djvu', 'md']

        # compressed formats
        compressed = ['a', 'ar', 'cpio', 'shar', 'LBR', 'iso', 'lbr', 'mar', 'tar', 'bz2', 'F', 'gz', 'lz', 'lzma', 'lzo',
                      'rz', 'sfark', 'sz', 'xz', 'Z', 'z', 'infl', '7z', 's7z', 'ace', 'afa', 'alz', 'apk', 'arc', 'arj', 'b1',
                      'ba', 'bh', 'cab', 'cfs', 'cpt', 'dar', 'dd', 'dgc', 'dmg', 'ear', 'gca', 'ha', 'hki', 'ice', 'jar', 'kgb',
                      'lzh', 'lha', 'lzx', 'pac', 'partimg', 'paq6', 'paq7', 'paq8', 'pea', 'pim', 'pit', 'qda', 'rar', 'rk', 'sda',
                      'sea', 'sen', 'sfx', 'sit', 'sitx', 'sqx', 'tar.gz', 'tgz', 'tar.Z', 'tar.bz2', 'tbz2', 'tar.lzma', 'tlz', 'uc',
                      'uc0', 'uc2', 'ucn', 'ur2', 'ue2', 'uca', 'uha', 'war', 'wim', 'xar', 'xp3', 'yz1', 'zip', 'zipx', 'zoo', 'zpaq',
                      'zz', 'ecc', 'par', 'par2']

        # return download_path
        if str(subfolder) == 'yes':
            if file_extension in audio:
                return os.path.join(download_path, 'Audios')

            # aria2c downloads youtube links file_name with 'videoplayback' name?!
            elif (file_extension in video) or (file_name == 'videoplayback'):
                return os.path.join(download_path, 'Videos')

            elif file_extension in document:
                return os.path.join(download_path, 'Documents')

            elif file_extension in compressed:
                return os.path.join(download_path, 'Compressed')

            else:
                return os.path.join(download_path, 'Others')
        else:
            return download_path

    # This method limits download speed
    def limitSpeed(self, limit_value):
        pass
