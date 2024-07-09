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
from requests.cookies import cookiejar_from_dict
from http.cookies import SimpleCookie
from persepolis_lib.useful_tools import convertTime, humanReadableSize
from persepolis.scripts import logger
import json
from urllib.parse import urlparse, unquote
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class Download():
    def __init__(self, add_link_dictionary, python_request_chunk_size=1, timeout=15, retry=5):
        self.python_request_chunk_size = python_request_chunk_size
        self.downloaded_size = 0
        self.finished_threads = 0
        self.eta = "0"
        self.resume = False
        self.download_speed_str = "0"
        self.__Version__ = "0.0.1"

        # download_status can be in Pending, Downloading, Stop, Error
        # All download_status start with a capital letter.
        self.download_status = 'Pending'
        self.exit_event = threading.Event()

        self.link = add_link_dictionary['link']
        self.name = add_link_dictionary['out']
        self.download_path = add_link_dictionary['download_path']
        self.ip = add_link_dictionary['ip']
        self.port = add_link_dictionary['port']
        self.proxy_user = add_link_dictionary['proxy_user']
        self.proxy_passwd = add_link_dictionary['proxy_passwd']
        self.download_user = add_link_dictionary['download_user']
        self.download_passwd = add_link_dictionary['download_passwd']
        self.header = add_link_dictionary['header']
        self.user_agent = add_link_dictionary['user_agent']
        self.raw_cookies = add_link_dictionary['load_cookies']
        self.referer = add_link_dictionary['referer']
        self.timeout = timeout
        self.retry = retry
        self.lock = False
        self.speed_limit = 0
        self.sleep_for_speed_limiting = 0
        self.not_converted_download_speed = 0

        # number_of_threads can't be more that 64
        self.number_of_threads = int(add_link_dictionary['connections'])

    # create requests session
    def createSession(self):
        # define a requests session
        self.requests_session = requests.Session()

        # check if user set proxy
        if self.ip:
            ip_port = 'http://' + str(self.ip) + ":" + str(self.port)
            if self.proxy_user:
                ip_port = ('http://' + self.proxy_user + ':'
                           + self.proxy_passwd + '@' + ip_port)
            # set proxy to the session
            self.requests_session.proxies = {'http': ip_port}

        # check if download session needs authenthication
        if self.download_user:
            # set download user pass to the session
            self.requests_session.auth = (self.download_user,
                                          self.download_passwd)

        # set cookies
        if self.raw_cookies:
            cookie = SimpleCookie()
            cookie.load(self.raw_cookies)

            cookies = {key: morsel.value for key, morsel in cookie.items()}
            self.requests_session.cookies = cookiejar_from_dict(cookies)

        # set referer
        if self.referer:
            # setting referer to the session
            self.requests_session.headers.update({'referer': self.referer})

        # set user_agent
        if self.user_agent:
            # setting user_agent to the session
            self.requests_session.headers.update(
                {'user-agent': self.user_agent})

        # set retry numbers.
        # backoff_factor will help to apply delays between attempts to avoid failing again
        retry = Retry(connect=self.retry, backoff_factor=1)
        adapter = HTTPAdapter(max_retries=retry)
        self.requests_session.mount('http://', adapter)
        self.requests_session.mount('https://', adapter)

    # get file size
    # if file size is not available, then download link is invalid
    def getFileSize(self):
        response = self.requests_session.head(self.link, allow_redirects=True, timeout=5)
        self.file_header = response.headers

        # find file size
        try:
            self.file_size = int(self.file_header['content-length'])
        except Exception as error:
            logger.sendToLog("Invalid URL: " + str(error), 'ERROR')
            self.file_size = None

        return self.file_size

    # get file name if available
    # if file name is not available, then set a file name
    def getFileName(self):
        # set default file name
        parsed_linkd = urlparse(self.link)
        self.file_name = Path(parsed_linkd.path).name

        # URL might contain percent-encoded characters
        # for example farsi characters in link
        if self.file_name.find('%'):
            self.file_name = unquote(self.file_name)

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

    # Check if server supports multi threading or not
    def multiThreadSupport(self):
        if 'Accept-Ranges' in self.file_header.keys():
            if self.file_header['Accept-Ranges'] == 'bytes':
                logger.sendToLog('Server supports multi thread downloading!')
                return True
            else:
                logger.sendToLog('Server dosn\'t support multi thread downloading!', 'ERROR')
                return False

    def createControlFile(self):
        # find file_path and control_json_file_path
        # If the file is partially downloaded, the download information is available in the control file.
        # The format of this file is Jason. the control file extension is .persepolis.
        # the control file name is same as download file name.
        # control file path is same as download file path.
        control_json_file = self.file_name + '.persepolis'

        # if user set download path
        if self.download_path:

            self.file_path = os.path.join(self.download_path, self.file_name)
            self.control_json_file_path = os.path.join(
                self.download_path, control_json_file)
        else:
            self.file_path = self.file_name
            self.control_json_file_path = control_json_file

        # create json control file if not created before
        try:
            with open(self.control_json_file_path, 'x') as f:
                f.write("")
        except Exception:
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

        # create empty file
        if create_download_file:
            fp = open(self.file_path, "wb")
            fp.write(b'\0' * self.file_size)
            fp.close()

    def definePartSizes(self):
        # download_infromation_list contains 64 slists.
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

            # set pending status for uncomplete parts
            for i in range(0, 64):
                if self.download_infromation_list[i][2] != 'complete':
                    self.download_infromation_list[i] = [self.download_infromation_list[i][0], self.download_infromation_list[i][1], 'pending', -1]

                self.downloaded_size = self.downloaded_size + self.download_infromation_list[i][1]
        else:
            part_size = int(self.file_size // 64)
            # create new list.
            self.download_infromation_list = [[]] * 64

            # if part_size greater than 1 MiB
            if part_size >= 1024**2:
                for i in range(0, 64):
                    self.download_infromation_list[i] = [i * part_size, 0, 'pending', -1]

            else:
                # Calculate how many parts of one MiB we need.
                number_of_parts = int(self.file_size // (1024**2)) + 1
                for i in range(0, number_of_parts):
                    self.download_infromation_list[i] = [i * 1024 * 1024, 0, 'pending', -1]

                # Set the starting byte number of the remaining parts equal to the size of the file.
                # The size of the file is equal to the last byte of the file.
                # The status of these parts is complete. Because we have nothing to download.
                for i in range(number_of_parts, 64):
                    self.download_infromation_list[i] = [self.file_size, 0, 'complete', -1]

    # this method calculates download rate and ETA every second
    # and alculates sleep between data reception for limiting download rate.
    def downloadSpeed(self):
        # Calculate the difference between downloaded volume and elapsed time
        # and divide them to get the download speed.
        last_download_value = self.downloaded_size
        end_time = time.perf_counter()
        # this loop repeated every 5 second.
        while self.download_status == 'Downloading':
            diffrence_time = time.perf_counter() - end_time
            diffrence_size = self.downloaded_size - last_download_value
            diffrence_size_converted, speed_unit = humanReadableSize(
                diffrence_size, 'speed')
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

            # downloadrate limitation
            # "Speed limit" is whole number. The more it is, the more sleep time is given to the data
            # receiving loop, which reduces the download speed.
            self.sleep_for_speed_limiting = (self.speed_limit * 1) / self.number_of_threads

            end_time = time.perf_counter()
            last_download_value = self.downloaded_size

            time.sleep(5)

    # this method runs progress bar and speed calculator
    def runProgressBar(self):
        # run  a thread for calculating download speed.
        calculate_speed_thread = threading.Thread(
            target=self.downloadSpeed)
        calculate_speed_thread.setDaemon(True)
        calculate_speed_thread.start()

    # threadHandler asks new part for download from this method.
    def askForNewPart(self):
        self.lock = True
        for i in range(0, 64):
            # Check that this part is not being downloaded or its download is not complete.
            # Check that the number of retries of this part has not reached the set limit.
            if (self.download_infromation_list[i][2] not in ['complete', 'downloading']) and (self.download_infromation_list[i][3] != self.retry):
                # set 'downloding' status for this part
                self.download_infromation_list[i][2] = 'downloading'
                # add 1 to retry number for this part
                self.download_infromation_list[i][3] += 1
                break

            # no part found
            if i == 63:
                i = None

        self.lock = False
        return i

    # The below code is used for each chunk of file handled
    # by each thread for downloading the content from specified
    # location to storage
    def threadHandler(self, thread_number):
        while self.download_status == 'Downloading':

            # Wait for the lock to be released.
            while self.lock is True:
                # Random sleep prevents two threads from downloading the same part at the same time.
                # sleep random time
                time.sleep(random.uniform(0, 0.5))
            part_number = self.askForNewPart()

            # If part_number is None, no part is available for download. So exit the loop.
            if part_number is None:
                break
            try:
                # calculate part size
                if part_number != 63:
                    part_size = self.download_infromation_list[part_number + 1][0] - self.download_infromation_list[part_number][0]
                else:
                    part_size = self.file_size - self.download_infromation_list[part_number][0]

                # get start byte number of this part and add it to downloaded size. download resume from this byte number
                downloaded_part = self.download_infromation_list[part_number][1]
                start = self.download_infromation_list[part_number][0] + downloaded_part

                # end of part is equal to start of the next part
                if part_number != 63:
                    end = self.download_infromation_list[part_number + 1][0]
                else:
                    end = self.file_size

                # specify the start and end of the part for request header.
                chunk_headers = {'Range': 'bytes=%d-%d' % (start, end)}

                # request the specified part and get into variable
                self.requests_session.headers.update(chunk_headers)
                response = self.requests_session.get(
                    self.link, allow_redirects=True, stream=True,
                    timeout=self.timeout)

                # open the file and write the content of the html page
                # into file.
                # r+b mode is open the binary file in read or write mode.
                with open(self.file_path, "r+b") as fp:

                    fp.seek(start)
                    fp.tell()

                    # why we use iter_content
                    # Iterates over the response data. When stream=True is set on
                    # the request, this avoids reading the content at once into
                    # memory for large responses. The chunk size is the number
                    # of bytes it should read into memory. This is not necessarily
                    # the length of each item returned as decoding can take place.
                    # so we divide our chunk to smaller chunks. default is 1 Mib
                    python_request_chunk_size = (1024
                                                 * self.python_request_chunk_size)
                    for data in response.iter_content(
                            chunk_size=python_request_chunk_size):
                        if self.download_status == 'Downloading':
                            fp.write(data)

                            # maybe the last chunk is less than 1MiB(default chunk size)
                            if downloaded_part <= (part_size
                                                   - python_request_chunk_size):
                                update_size = python_request_chunk_size
                            else:
                                # so the last small chunk is equal to :
                                update_size = (part_size - downloaded_part)

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
                            time.sleep(self.sleep_for_speed_limiting)

                        else:
                            self.download_infromation_list[part_number][2] = 'stopped'
                            break

            except:
                self.download_infromation_list[part_number][2] = 'error'

            # so it's complete successfully.
            if (downloaded_part == part_size):
                self.download_infromation_list[part_number][2] = 'complete'
            else:
                self.download_infromation_list[part_number][2] = 'error'

        # This thread is finished.
        self.finished_threads = self.finished_threads + 1

    # this method save download information in json format every 1 second
    def saveInfo(self):
        while (self.finished_threads != self.number_of_threads) and\
                (not (self.exit_event.wait(timeout=1))):
            control_dict = {
                'ETag': self.etag,
                'file_name': self.file_name,
                'file_size': self.file_size,
                'download_infromation_list': self.download_infromation_list}

            # write control_dict in json file
            with open(self.control_json_file_path, "w") as outfile:
                json.dump(control_dict, outfile, indent=2)

    # this method runs download threads
    def runDownloadThreads(self):

        # check if server supports multithread downloading or not!
        if self.multiThreadSupport() is False:
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

        # run saveInfo thread for updating control file
        save_control_thread = threading.Thread(
            target=self.saveInfo)
        save_control_thread.setDaemon(True)
        save_control_thread.start()

    # this method checks and manages download progress.
    def checkDownloadProgress(self):
        # Run this loop until the download is finished.
        while (self.file_size != self.downloaded_size) and (self.download_status == 'Downloading') and (self.finished_threads != self.number_of_threads):

            time.sleep(1)

        # If the downloaded size is the same as the file size, then the download has been completed successfully.
        if self.file_size == self.downloaded_size:

            self.download_status = 'Complete'
            logger.sendToLog('Download complete.')

        # If the download is not complete and the user has not stopped the download, then the download has encountered an error.
        elif self.download_status != 'Stopped':

            self.download_status = 'Error'
            logger.sendToLog('Download Error')

        elif self.download_status == 'Stopped':

            logger.sendToLog('Download stopped.')

        # Return the current Thread object
        main_thread = threading.current_thread()

        # Return a list of all Thread objects currently alive
        for t in threading.enumerate():
            if t is main_thread:
                continue
            t.join()

        # close requests session
        self.requests_session.close()

    # this method starts download
    def start(self):
        self.createSession()
        file_size = self.getFileSize()
        if file_size:
            self.download_status = 'Downloading'
            self.getFileName()

            self.getFileTag()

            self.createControlFile()
            self.definePartSizes()

            self.runProgressBar()

            self.runDownloadThreads()

            self.checkDownloadProgress()
        else:
            self.download_status = 'Error'
        self.close()

    def stop(self, signum, frame):
        self.download_status = 'Stopped'
        self.exit_event.set()

    def close(self):
        # if download complete, so delete control file
        if self.download_status == 'Complete':
            os.remove(self.control_json_file_path)

        logger.sendToLog("persepolis_lib is closed!")
