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


import requests
import time
import random
import threading
import os
import errno
from persepolis.scripts.useful_tools import convertTime, humanReadableSize, freeSpace, headerToDict, readCookieJar, getFileNameFromLink
from persepolis.scripts.osCommands import makeDirs, moveFile
from persepolis.scripts import logger
from persepolis.scripts.bubble import notifySend
from persepolis.constants import VERSION
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class Download():
    def __init__(self, add_link_dictionary, main_window, gid):
        self.downloaded_size = 0
        self.finished_threads = 0
        self.eta = "0"
        self.resume = False
        self.main_window = main_window
        self.download_speed_str = "0"
        self.gid = gid

        # download_status can be in waiting, downloading, stop, error, paused
        self.download_status = 'waiting'

        self.link = add_link_dictionary['link']
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
        self.number_of_parts = 0
        self.file_name = None
        self.file_size = None
        self.timeout = int(main_window.persepolis_setting.value('settings/timeout'))
        self.retry = int(main_window.persepolis_setting.value('settings/max-tries'))
        self.retry_wait = int(main_window.persepolis_setting.value('settings/retry-wait'))
        self.python_request_chunk_size = int(main_window.persepolis_setting.value('settings/chunk-size'))
        self.lock = False
        self.sleep_for_speed_limiting = 0
        self.not_converted_download_speed = 0
        self.download_percent = 0
        self.error_message = ''
        self.close_status = False
        # check certificate
        if str(main_window.persepolis_setting.value('settings/dont-check-certificate')) == 'yes':
            self.check_certificate = False
        else:
            self.check_certificate = True

        # number_of_threads can't be more that 64
        self.number_of_threads = int(add_link_dictionary['connections'])
        self.number_of_active_connections = self.number_of_threads

        self.thread_list = []
        # this dictionary contains information about each part is downloaded by which thread.
        self.part_thread_dict = {}

    # create requests session
    def createSession(self):
        # define a requests session
        self.requests_session = requests.Session()

        # check if user set proxy
        if self.ip:
            ip_port = '://' + str(self.ip) + ":" + str(self.port)
            if self.proxy_user:
                ip_port = ('://' + self.proxy_user + ':'
                           + self.proxy_passwd + '@' + ip_port)
            if self.proxy_type == 'socks5':
                ip_port = 'socks5' + ip_port
            else:
                ip_port = 'http' + ip_port

            proxies = {'http': ip_port,
                       'https': ip_port}

            # set proxy to the session
            self.requests_session.proxies.update(proxies)

        # check if download session needs authenthication
        if self.download_user:
            # set download user pass to the session
            self.requests_session.auth = (self.download_user,
                                          self.download_passwd)

        # set cookies
        if self.load_cookies:
            jar = readCookieJar(self.load_cookies)
            if jar:
                self.requests_session.cookies = jar

        # set referer
        if self.referer:
            # setting referer to the session
            self.requests_session.headers.update({'referer': self.referer})

        # set user_agent
        if self.user_agent:
            # setting user_agent to the session
            self.requests_session.headers.update(
                {'user-agent': self.user_agent})
        else:
            self.user_agent = 'PersepolisDM/' + str(VERSION.version_str)
            # setting user_agent to the session
            self.requests_session.headers.update(
                {'user-agent': self.user_agent})

        if self.header is not None:
            # convert header to dictionary
            dict_ = headerToDict(self.header)
            # update headers
            self.requests_session.headers.update(dict_)

    def setRetry(self):
        # set retry numbers.
        # backoff_factor will help to apply delays between attempts to avoid failing again
        retry = Retry(connect=self.retry, backoff_factor=self.retry_wait)
        adapter = HTTPAdapter(max_retries=retry)
        self.requests_session.mount('http://', adapter)
        self.requests_session.mount('https://', adapter)

    # get file size
    # if file size is not available, then download link is invalid
    def getFileSize(self):
        error_message = None
        error_message2 = None
        # find file size
        try:
            response = self.requests_session.head(self.link, allow_redirects=True, timeout=self.timeout, verify=self.check_certificate)
#             response.raise_for_status()
            self.file_header = response.headers

            self.file_size = int(self.file_header['content-length'])
        except requests.exceptions.HTTPError as error:
            error_message = 'HTTP error'
            error_message2 = str(error)
        except requests.exceptions.ConnectionError as error:
            error_message = 'Connection error'
            error_message2 = str(error)
        except requests.exceptions.Timeout as error:
            error_message = 'Timeout error'
            error_message2 = str(error)
        except requests.exceptions.RequestException as error:
            error_message = 'Request error'
            error_message2 = str(error)
        except Exception as error:
            error_message = 'Error'
            error_message2 = str(error)

        if error_message:
            logger.sendToLog(error_message + ' - ' + error_message2, 'DOWNLOAD ERROR')
            self.error_message = error_message
            self.file_size = None

        return self.file_size

    # get file name if available
    # if file name is not available, then set a file name
    def getFileName(self):
        # set default file name
        # get file_name from link
        self.file_name = getFileNameFromLink(self.link)

        # check if user set file name or not
        if self.name:
            self.file_name = self.name

        # check if filename is available in header
        elif 'Content-Disposition' in self.file_header.keys():
            content_disposition = self.file_header['Content-Disposition']

            if content_disposition.find('filename') != -1:

                # so file name is available in header
                filename_splited = content_disposition.split('filename=')
                filename_splited = filename_splited[-1]

                # getting file name in desired format
                self.file_name = filename_splited.strip()

    # this method gives etag from header
    # ETag is an HTTP response header field that helps with caching behavior by making
    # it easy to check whether a resource has changed, without having to re-download it.
    def getFileTag(self):
        if 'ETag' in self.file_header.keys():
            self.etag = self.file_header['ETag']
        else:
            self.etag = None

    # Check if server supports multi threading and resuming or not
    def resumingSupport(self):
        self.resuming_suppurt = False
        if 'Accept-Ranges' in self.file_header.keys():
            if self.file_header['Accept-Ranges'] == 'bytes':
                logger.sendToLog('Server supports multi thread downloading and resuming download!', 'DOWNLOADS')
                self.resuming_suppurt = True
            else:
                logger.sendToLog('Server dosn\'t support multi thread downloading and resuming download!', 'DOWNLOAD ERROR')
        else:
            logger.sendToLog('Server dosn\'t support multi thread downloading and resuming download!', 'DOWNLOAD ERROR')

    def createControlFile(self):
        # find file_path and control_json_file_path
        # If the file is partially downloaded, the download information is available in the control file.
        # The format of this file is Jason. the control file extension is .persepolis.
        # the control file name is same as download file name.
        # control file path is same as download file path.
        # If the file_path is set to default path, the the control file path will be created in "Download" directory.
        control_json_file = self.file_name + '.persepolis'

        # Create download_path if not existed
        makeDirs(self.download_path)

        # if user set download path
        self.file_path = os.path.join(self.download_path, self.file_name)

        self.control_json_file_path = os.path.join(
            self.download_path, control_json_file)

        # create json control file if not created before
        try:
            with open(self.control_json_file_path, 'x') as f:
                f.write("")
        except OSError as e:
            # it means control_json_file_path characters is more than 256 byte
            if e.errno == errno.ENAMETOOLONG:
                # reduce  file_name lenght
                reduce_bytes = len(self.control_json_file_path.encode('utf-8')) - 255

                # seperate extension from file_name
                split_file_name = self.file_name.split('.')

                # check we have extension or not
                extension = ""
                if len(split_file_name) > 1:
                    # remove extension
                    extension = split_file_name.pop(-1)

                # join file_name without extension
                file_name_without_extension = ''.join(split_file_name)

                if len(file_name_without_extension.encode('utf-8')) > reduce_bytes:

                    # Calculate how many characters must be removed
                    for i in range(len(file_name_without_extension)):
                        string_ = file_name_without_extension[(-1 * i):]
                        string_size = len(string_.encode('utf-8'))
                        if string_size >= reduce_bytes:
                            # reduce characters
                            file_name_without_extension = file_name_without_extension[:(-1 * i)]
                            break

                    # create new file_name and file_path and control_json_file
                    self.file_name = file_name_without_extension + extension
                    self.file_path = os.path.join(self.download_path, self.file_name)
                    control_json_file = self.file_name + '.persepolis'
                    self.control_json_file_path = os.path.join(
                        self.download_path, control_json_file)

                # try again
                with open(self.control_json_file_path, 'x') as f:
                    f.write("")

            else:
                # so the control file is already exists
                # read control file
                with open(self.control_json_file_path, "r") as f:

                    try:
                        # save json file information in dictionary format
                        data_dict = json.load(f)

                        # check if the download is duplicated
                        # If download item is duplicated, so resume download
                        # check ETag
                        if 'ETag' in data_dict:

                            if data_dict['ETag'] == self.etag:
                                self.resume = True
                            else:
                                self.resume = False

                        # if ETag is not available, then check file size
                        elif 'file_size' in data_dict:

                            if data_dict['file_size'] == self.file_size:
                                self.resume = True
                            else:
                                self.resume = False
                        else:
                            self.resume = False

                    # control file is corrupted.
                    except Exception:
                        self.resume = False

        if self.resuming_suppurt is False:
            self.resume = False

        # check if uncomplete download file exists
        if os.path.isfile(self.file_path):
            download_file_existance = True
        else:
            download_file_existance = False

        if self.resume and not (download_file_existance):
            self.resume = False
            create_download_file = True
        elif self.resume and download_file_existance:
            create_download_file = False
        else:
            create_download_file = True

        # create an empty file
        if create_download_file:
            fp = open(self.file_path, "wb")

            # if file_size is specified, create an empty file with file_size
            if self.file_size:
                fp.write(b'\0' * self.file_size)

            fp.close()

    def definePartSizes(self):
        # download_infromation_list contains 64 lists.
        # Every list contains:
        # [start byte number for this part, downloaded size, download status for this part, number of retryingfor this part]
        # Status can be stopped, pending, downloading, error, complete
        # All part statuses start with a lowercase letter.
        # Retry number is -1, because askForNewPart method add 1 to it in the first call.
        if self.resume:
            # read control file
            with open(self.control_json_file_path, "r") as f:
                data_dict = json.load(f)

            # read number of threads
            self.download_infromation_list = data_dict['download_infromation_list']

            # number_of_parts
            self.number_of_parts = data_dict['number_of_parts']

            # set pending status for uncomplete parts
            for i in range(0, self.number_of_parts):
                if self.download_infromation_list[i][2] != 'complete':
                    self.download_infromation_list[i] = [self.download_infromation_list[i][0], self.download_infromation_list[i][1], 'pending', -1]

                # Calculate downloded size
                self.downloaded_size = self.downloaded_size + self.download_infromation_list[i][1]
        else:
            if self.file_size:
                part_size = int(self.file_size // 64)
                # create new list.
                self.download_infromation_list = [[]] * 64

                # if part_size greater than 1 MiB
                if part_size >= 1024**2:
                    self.number_of_parts = 64
                    for i in range(0, 64):
                        self.download_infromation_list[i] = [i * part_size, 0, 'pending', -1]

                else:
                    # Calculate how many parts of one MiB we need.
                    self.number_of_parts = int(self.file_size // (1024**2)) + 1
                    self.number_of_threads = self.number_of_parts
                    for i in range(0, self.number_of_parts):
                        self.download_infromation_list[i] = [i * 1024 * 1024, 0, 'pending', -1]

                    # Set the starting byte number of the remaining parts equal to the size of the file.
                    # The size of the file is equal to the last byte of the file.
                    # The status of these parts is complete. Because we have nothing to download.
                    for i in range(self.number_of_parts, 64):
                        self.download_infromation_list[i] = [self.file_size, 0, 'complete', -1]
            else:
                # create new list.
                self.download_infromation_list = [[]] * 64

                self.number_of_parts = 1
                self.number_of_threads = 1
                self.download_infromation_list[0] = [0, 0, 'pending', -1]
                # Set the starting byte number of the remaining parts equal to the size of the file.
                # The size of the file is equal to the last byte of the file.
                # The status of these parts is complete. Because we have nothing to download.
                for i in range(self.number_of_parts, 64):
                    self.download_infromation_list[i] = [0, 0, 'complete', -1]

        for i in range(0, self.number_of_parts):
            # self.part_thread_dict[part_number] = thread_number
            self.part_thread_dict[i] = None

    # this method calculates download rate and ETA every second
    def downloadSpeed(self):
        # Calculate the difference between downloaded volume and elapsed time
        # and divide them to get the download speed.
        last_download_value = self.downloaded_size
        end_time = time.perf_counter()
        # this loop repeated every 0.5 second.
        while self.download_status == 'downloading' or self.download_status == 'paused':
            diffrence_time = time.perf_counter() - end_time
            diffrence_size = self.downloaded_size - last_download_value
            diffrence_size_converted, speed_unit = humanReadableSize(diffrence_size, 'speed')
            download_speed = round(float(diffrence_size_converted) / diffrence_time,
                                   2)
            self.download_speed_str = (str(download_speed)
                                       + " " + speed_unit + "/s")
            not_converted_download_speed = diffrence_size / diffrence_time
            try:
                # estimated time the download will be completed.
                eta_second = (self.file_size
                              - self.downloaded_size) /\
                    not_converted_download_speed
            except Exception:
                eta_second = 0

            self.eta = convertTime(eta_second)

            end_time = time.perf_counter()
            last_download_value = self.downloaded_size

            time.sleep(2)

    # this method runs progress bar and speed calculator
    def runProgressBar(self):
        # run  a thread for calculating download speed.
        calculate_speed_thread = threading.Thread(
            target=self.downloadSpeed)
        calculate_speed_thread.setDaemon(True)
        calculate_speed_thread.start()
        self.thread_list.append(calculate_speed_thread)

    # threadHandler asks new part for download from this method.
    def askForNewPart(self):
        self.lock = True
        for i in range(0, self.number_of_parts):
            # Check that this part is not being downloaded or it is not complete.
            # Check that the number of retries of this part has not reached the set limit.
            if (self.download_infromation_list[i][2] not in ['complete', 'downloading']) and (self.download_infromation_list[i][3] != self.retry):
                # set 'downloding' status for this part
                self.download_infromation_list[i][2] = 'downloading'
                # add 1 to retry number for this part
                self.download_infromation_list[i][3] += 1
                break

            # no part found
            if i == (self.number_of_parts - 1):
                i = None

        self.lock = False
        return i

    # The below code is used for each chunk of file handled
    # by each thread for downloading the content from specified
    # location to storage
    def threadHandler(self, thread_number):
        while self.download_status in ['downloading', 'paused']:

            # Wait for the lock to be released.
            while self.lock is True:
                # Random sleep prevents two threads from downloading the same part at the same time.
                # sleep random time
                time.sleep(random.uniform(1, 3))
            part_number = self.askForNewPart()

            # If part_number is None, no part is available for download. So exit the loop.
            if part_number is None:
                break
            error_message = None
            error_message2 = None
            self.part_thread_dict[part_number] = thread_number
            try:
                if self.file_size:
                    # Calculate part size
                    # If it's not the last part:
                    if part_number != (self.number_of_parts - 1):
                        part_size = self.download_infromation_list[part_number + 1][0] - self.download_infromation_list[part_number][0]
                    else:
                        # for last part
                        part_size = self.file_size - self.download_infromation_list[part_number][0]

                    # get start byte number of this part and add it to downloaded size. download resume from this byte number
                    downloaded_part = self.download_infromation_list[part_number][1]

                    start = self.download_infromation_list[part_number][0] + downloaded_part

                    # end of part is equal to start of the next part
                    if part_number != (self.number_of_parts - 1):
                        end = self.download_infromation_list[part_number + 1][0]
                    else:
                        end = self.file_size

                    # download from begining!
                    if self.resuming_suppurt is False:
                        start = 0

                    # specify the start and end of the part for request header.
                    chunk_headers = {'Range': 'bytes=%d-%d' % (start, end)}

                    # request the specified part and get into variable
                    # When stream=True is set on the request, this avoids
                    # reading the content at once into memory for large responses
                    self.requests_session.headers.update(chunk_headers)
                    response = self.requests_session.get(
                        self.link, allow_redirects=True, stream=True,
                        timeout=self.timeout, verify=self.check_certificate)

                    # open the file and write the content of the html page
                    # into file.
                    # r+b mode is open the binary file in read or write mode.
                    with open(self.file_path, "r+b") as fp:

                        # The seek() method sets the current file position in a file stream.
                        fp.seek(start)

                        # The Python File tell() method is used to find the current position of
                        # the file cursor (or pointer) within the file.
                        fp.tell()

                        # why we use iter_content
                        # Iterates over the response data. When stream=True is set on
                        # the request, this avoids reading the content at once into
                        # memory for large responses. The chunk size is the number
                        # of bytes it should read into memory. This is not necessarily
                        # the length of each item returned as decoding can take place.
                        # so we divide our chunk to smaller chunks. default is 100 Kib
                        python_request_chunk_size = (1024
                                                     * self.python_request_chunk_size)
                        for data in response.iter_content(
                                chunk_size=python_request_chunk_size):
                            if self.download_status in ['downloading', 'paused']:
                                fp.write(data)

                                # if this part is downloaded by another thread then exit thread
                                if self.part_thread_dict[part_number] != thread_number:
                                    # This loop does not end due to an error in the request.
                                    # Therefore, no number should be added to the number of retries.
                                    self.download_infromation_list[part_number][3] -= 1
                                    break

                                # maybe the last chunk is less than default chunk size
                                if (part_size - downloaded_part) >= python_request_chunk_size:
                                    update_size = python_request_chunk_size
                                    # if update_size is not equal with actual data length,
                                    # then redownload this chunk.
                                    # exit this "for loop" for redownloading this chunk.
                                    if update_size != len(data):
                                        # This loop does not end due to an error in the request.
                                        # Therefore, no number should be added to the number of retries.
                                        self.download_infromation_list[part_number][3] -= 1
                                        break
                                else:
                                    # so the last small chunk is equal to :
                                    update_size = (part_size - downloaded_part)
                                    # some times last chunks are smaller
                                    if len(data) < update_size:
                                        update_size = len(data)

                                # update downloaded_part
                                downloaded_part = (downloaded_part
                                                   + update_size)
                                # save value to downloaded_size_list
                                self.download_infromation_list[part_number][1] = downloaded_part

                                # this variable saves amount of total downloaded size
                                # update downloaded_size
                                self.downloaded_size = (self.downloaded_size
                                                        + update_size)
                                # perhaps user set limitation for download rate.
                                # downloadrate limitation
                                # "Speed limit" is whole number. The more it is, the more sleep time is given to the data
                                # receiving loop, which reduces the download speed.
                                time.sleep(self.sleep_for_speed_limiting)

                                if self.download_status == 'paused':
                                    # wait for unpausing
                                    while self.download_status == 'paused':
                                        time.sleep(0.2)

                            else:
                                self.download_infromation_list[part_number][2] = 'stopped'
                                break
                # If file_size is unspecified.
                else:
                    download_finished_successfully = False

                    # get start byte number of this part and add it to downloaded size. download resume from this byte number
                    start = self.download_infromation_list[part_number][1]
                    downloaded_part = start

                    # download from begining!
                    if self.resuming_suppurt is False:
                        start = 0

                    # specify the start and end of the part for request header.
                    chunk_headers = {'Range': 'bytes=%d-' % (start)}

                    # request the specified part and get into variable
                    # When stream=True is set on the request, this avoids
                    # reading the content at once into memory for large responses
                    self.requests_session.headers.update(chunk_headers)
                    response = self.requests_session.get(
                        self.link, allow_redirects=True, stream=True,
                        timeout=self.timeout, verify=self.check_certificate)

                    # open the file and write the content of the html page
                    # into file.
                    # r+b mode is open the binary file in read or write mode.
                    with open(self.file_path, "r+b") as fp:

                        # The seek() method sets the current file position in a file stream.
                        fp.seek(start)

                        # The Python File tell() method is used to find the current position of
                        # the file cursor (or pointer) within the file.
                        fp.tell()

                        # why we use iter_content
                        # Iterates over the response data. When stream=True is set on
                        # the request, this avoids reading the content at once into
                        # memory for large responses. The chunk size is the number
                        # of bytes it should read into memory. This is not necessarily
                        # the length of each item returned as decoding can take place.
                        # so we divide our chunk to smaller chunks. default is 100 Kib
                        python_request_chunk_size = (1024
                                                     * self.python_request_chunk_size)
                        for data in response.iter_content(
                                chunk_size=python_request_chunk_size):
                            if self.download_status in ['downloading', 'paused']:
                                fp.write(data)
                                update_size = len(data)

                                # update downloaded_part
                                downloaded_part = (downloaded_part
                                                   + update_size)
                                # save value to downloaded_size_list
                                self.download_infromation_list[part_number][1] = downloaded_part

                                # this variable saves amount of total downloaded size
                                # update downloaded_size
                                self.downloaded_size = (self.downloaded_size
                                                        + update_size)
                                # perhaps user set limitation for download rate.
                                # downloadrate limitation
                                # "Speed limit" is whole number. The more it is, the more sleep time is given to the data
                                # receiving loop, which reduces the download speed.
                                time.sleep(self.sleep_for_speed_limiting)

                                if self.download_status == 'paused':
                                    # wait for unpausing
                                    while self.download_status == 'paused':
                                        time.sleep(0.2)

                            else:
                                self.download_infromation_list[part_number][2] = 'stopped'
                                break
                    download_finished_successfully = True

            except requests.exceptions.HTTPError as error:
                error_message = 'HTTP error'
                error_message2 = str(error)
                self.download_infromation_list[part_number][2] = 'error'

            except requests.exceptions.ConnectionError as error:
                error_message = 'Connection error'
                error_message2 = str(error)
                self.download_infromation_list[part_number][2] = 'error'

            except requests.exceptions.Timeout as error:
                error_message = 'Timeout error'
                error_message2 = str(error)
                self.download_infromation_list[part_number][2] = 'error'

            except requests.exceptions.RequestException as error:
                error_message = 'Request error'
                error_message2 = str(error)
                self.download_infromation_list[part_number][2] = 'error'

            except Exception as error:
                error_message = 'Error'
                error_message2 = str(error)
                self.download_infromation_list[part_number][2] = 'error'

            if error_message:
                self.error_message = error_message
                logger.sendToLog(error_message + ' - ' + error_message2, 'ERROR')

            # so it's complete successfully.
            if self.file_size:
                if (downloaded_part == part_size):
                    self.download_infromation_list[part_number][2] = 'complete'
                    self.part_thread_dict[part_number] = None
                else:
                    self.download_infromation_list[part_number][2] = 'error'
                    self.part_thread_dict[part_number] = None
            else:
                if download_finished_successfully:
                    self.file_size = self.downloaded_size
                    self.download_infromation_list[part_number][2] = 'complete'
                    self.part_thread_dict[part_number] = None
                else:
                    self.download_infromation_list[part_number][2] = 'error'
                    self.part_thread_dict[part_number] = None
        # This thread is finished.
        self.finished_threads = self.finished_threads + 1

    # this method save download information in json format every 1 second
    def saveInfo(self):
        while self.download_status == 'downloading' or self.download_status == 'paused':
            control_dict = {
                'ETag': self.etag,
                'file_name': self.file_name,
                'file_size': self.file_size,
                'number_of_parts': self.number_of_parts,
                'download_infromation_list': self.download_infromation_list}

            # write control_dict in json file
            with open(self.control_json_file_path, "w") as outfile:
                json.dump(control_dict, outfile, indent=2)
            time.sleep(1)

    # this method runs download threads
    def runDownloadThreads(self):

        # check if server supports multithread downloading or not!
        if self.resuming_suppurt is False:
            self.thread_number = 1

        for i in range(0, self.number_of_threads):

            # sleep between starting new thread.
            # it solves "Connection refused" error.
            time.sleep(0.1)

            # create threads
            t = threading.Thread(
                target=self.threadHandler,
                kwargs={'thread_number': i})
            t.setDaemon(True)
            t.start()
            self.thread_list.append(t)

        # run saveInfo thread for updating control file
        save_control_thread = threading.Thread(
            target=self.saveInfo)
        save_control_thread.setDaemon(True)
        save_control_thread.start()
        self.thread_list.append(save_control_thread)

    # this method checks and manages download progress.
    def checkDownloadProgress(self):
        logger.sendToLog("Download starts! - GID:" + self.gid, "DOWNLOADS")

        # Run this loop until the download is finished.
        while (self.file_size != self.downloaded_size) and (self.download_status == 'downloading' or self.download_status == 'paused') and \
              (self.finished_threads != self.number_of_threads):

            # Calculate download percent
            if self.file_size:
                self.download_percent = int((self.downloaded_size / self.file_size) * 100)
            else:
                self.download_percent = 0

            # Calculate number of active threads
            self.number_of_active_connections = self.number_of_threads - self.finished_threads
            time.sleep(1)

        # Calculate download percent
        if self.file_size:
            self.download_percent = int((self.downloaded_size / self.file_size) * 100)
        else:
            self.download_percent = 0

        self.number_of_active_connections = 0
        # If the downloaded size is the same as the file size, then the download has been completed successfully.
        if self.file_size == self.downloaded_size:

            self.download_status = 'complete'
            logger.sendToLog('Download complete. - GID: ' + self.gid, 'DOWNLOADS')

        # If the download is not complete and the user has not stopped the download, then the download has encountered an error.
        elif self.download_status != 'stopped':

            self.download_status = 'error'
            logger.sendToLog('Download Error - GID: ' + self.gid, 'DOWNLOADS')

        elif self.download_status == 'stopped':

            logger.sendToLog('Download stopped. - GID: ' + self.gid, 'DOWNLOADS')

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
        while sigma_end != sigma_now and (self.download_status == 'downloading' or self.download_status == 'paused'):

            # get current time
            sigma_now = self.nowTime()
            time.sleep(2.1)

        # Time is up!
        if (self.download_status == 'downloading' or self.download_status == 'paused'):
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

    # this method starts download
    def start(self):
        # create new download session.
        self.createSession()
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
            # start download
            self.getFileSize()

            self.setRetry()

            self.download_status = 'downloading'

            # if user set end_time
            if self.end_time:
                self.runEndTimeThread()

            self.resumingSupport()

            self.getFileName()

            self.getFileTag()

            self.createControlFile()

            self.definePartSizes()

            self.runProgressBar()

            self.runDownloadThreads()

            self.checkDownloadProgress()

            self.close()
        else:
            # if start_time_status is "stopped" it means download Canceled by user
            logger.sendToLog("Download Canceled", "DOWNLOADS")

    def downloadPause(self):
        self.download_status = 'paused'

    def downloadUnpause(self):
        self.download_status = 'downloading'

    def downloadStop(self):
        self.download_status = 'stopped'
#         self.exit_event.set()

    def close(self):
        # if download complete, so delete control file
        if self.download_status == 'complete':
            os.remove(self.control_json_file_path)

            # move file to download folder
            self.main_window.persepolis_setting.sync()

            # if user specified download_path is equal to persepolis_setting download_path,
            # then subfolder must added to download path.
            if self.main_window.persepolis_setting.value('settings/download_path') == self.download_path:

                # return new download_path according to file extension.
                new_download_path = self.findDownloadPath(
                    self.file_name, self.download_path, self.main_window.persepolis_setting.value('settings/subfolder'))

                file_path = self.downloadCompleteAction(new_download_path)
            else:
                # keep user specified download_path
                file_path = self.file_path

            # update download_path in addlink_db_table
            # find user preferred download_path from addlink_db_table in data_base
            add_link_dictionary = self.main_window.persepolis_db.searchGidInAddLinkTable(self.gid)

            add_link_dictionary['download_path'] = file_path
            self.main_window.persepolis_db.updateAddLinkTable([add_link_dictionary])

        # close requests session
        self.requests_session.close()

        # ask threads for exiting.
        for thread in self.thread_list:
            thread.join()

        logger.sendToLog("persepolis_lib is closed!", 'DOWNLOADS')
        self.close_status = True

    # This method returns download status
    def tellStatus(self):
        downloaded_size, downloaded_size_unit = humanReadableSize(self.downloaded_size)
        if self.file_size:
            file_size, file_size_unit = humanReadableSize(self.file_size)
        else:
            file_size = ''
            file_size_unit = ''

        if self.eta == '0s':
            self.eta = ''

        # return information in dictionary format
        download_info = {
            'gid': self.gid,
            'file_name': self.file_name,
            'status': self.download_status,
            'size': str(file_size) + ' ' + file_size_unit,
            'downloaded_size': str(downloaded_size) + ' ' + downloaded_size_unit,
            'percent': str(self.download_percent) + '%',
            'connections': str(self.number_of_active_connections),
            'rate': self.download_speed_str,
            'estimate_time_left': self.eta,
            'link': self.link,
            'error': self.error_message
        }

        return download_info

    # This method limits download speed
    def limitSpeed(self, limit_value):
        # Calculate sleep time between data receiving. It's reduce download speed.
        self.sleep_for_speed_limiting = (10 - limit_value) * 0.005 * (self.number_of_active_connections)

    # download complete actions!
    # this method is returning file_path of file in the user's download folder
    # and move downloaded file after download completion.
    def downloadCompleteAction(self, new_download_path):

        # rename file if file already existed
        i = 1
        new_file_path = os.path.join(new_download_path, self.file_name)

        while os.path.isfile(new_file_path):
            file_name_split = self.file_name.split('.')
            extension_length = len(file_name_split[-1]) + 1

            new_name = self.file_name[0:-extension_length] + \
                '_' + str(i) + self.file_name[-extension_length:]
            new_file_path = os.path.join(new_download_path, new_name)
            i = i + 1

        free_space = freeSpace(new_download_path)

        if free_space is not None and self.file_size is not None:

            # compare free disk space and file_size
            if free_space >= self.file_size:

                # move the file to the download folder
                move_answer = moveFile(str(self.file_path), str(new_file_path), 'file')

                if not (move_answer):
                    # write error message in log
                    logger.sendToLog('Persepolis can not move file', "ERROR")
                    new_file_path = self.file_path

            else:
                # notify user if we have insufficient disk space
                # and do not move file from temp download folder to download folder
                new_file_path = self.file_path
                logger.sendToLog('Insufficient disk space in download folder', "ERROR")

                # show notification
                notifySend("Insufficient disk space!", 'Please change download folder',
                           10000, 'fail', parent=self.main_window)

        else:
            # move the file to the download folder
            move_answer = moveFile(str(self.file_path), str(new_file_path), 'file')

            if not (move_answer):
                logger.sendToLog('Persepolis can not move file', "ERROR")
                new_file_path = self.file_path

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
