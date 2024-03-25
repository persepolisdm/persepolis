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

from persepolis.scripts.useful_tools import freeSpace, humanReadableSize, findExternalAppPath, runApplication
from persepolis.scripts.socks5_to_http_convertor import Socks5ToHttpConvertor
from persepolis.scripts.osCommands import moveFile, makeTempDownloadDir
from persepolis.scripts.bubble import notifySend
from persepolis.scripts import logger
from persepolis.constants import OS
import xmlrpc.client
import urllib.parse
import subprocess
import traceback
import platform
import time
import ast
import sys
import os

try:
    from PySide6.QtCore import QSettings
except:
    from PyQt5.QtCore import QSettings

# Before reading this file, please read this link!
# this link helps you to understand this codes:
# https://aria2.github.io/manual/en/html/aria2c.html#rpc-interface


home_address = os.path.expanduser("~")

os_type = platform.system()

# persepolis setting
persepolis_setting = QSettings('persepolis_download_manager', 'persepolis')

# host is localhost
host = 'localhost'

# get port from persepolis_setting
port = int(persepolis_setting.value('settings/rpc-port'))

# get aria2_path
aria2_path = persepolis_setting.value('settings/aria2_path')

# xml rpc
SERVER_URI_FORMAT = 'http://{}:{:d}/rpc'
server_uri = SERVER_URI_FORMAT.format(host, port)
server = xmlrpc.client.ServerProxy(server_uri, allow_none=True)

# start aria2 with RPC


def startAria(parent):

    # find aria2c path
    aria2c_command, log_list = findExternalAppPath('aria2c')
    
    logger.sendToLog(log_list[0], log_list[1])

    # Run aria2c
    command_argument = [aria2c_command, '--no-conf',
                          '--enable-rpc', '--rpc-listen-port=' + str(port),
                          '--rpc-max-request-size=2M',
                          '--rpc-listen-all', '--quiet=true']

    pipe = runApplication(command_argument)

    time.sleep(2)

    # check that starting is successful or not!
    answer = aria2Version()

    # return result
    return answer

# check aria2 release version . Persepolis uses this function to
# check that aria2 RPC connection is available or not.


def aria2Version():
    try:
        answer = server.aria2.getVersion()
    except:
        # write ERROR messages in terminal and log
        logger.sendToLog("Aria2 didn't respond!", "ERROR")
        answer = "did not respond"

    return answer

# this function sends download request to aria2


def downloadAria(gid, parent):
    # add_link_dictionary is a dictionary that contains user download request
    # information.

    # get information from data_base
    add_link_dictionary = parent.persepolis_db.searchGidInAddLinkTable(gid)

    link = add_link_dictionary['link']
    proxy_host = add_link_dictionary['ip']
    proxy_port = add_link_dictionary['port']
    proxy_user = add_link_dictionary['proxy_user']
    proxy_passwd = add_link_dictionary['proxy_passwd']
    download_user = add_link_dictionary['download_user']
    download_passwd = add_link_dictionary['download_passwd']
    proxy_type = add_link_dictionary['proxy_type']
    connections = add_link_dictionary['connections']
    limit = str(add_link_dictionary['limit_value'])
    start_time = add_link_dictionary['start_time']
    end_time = add_link_dictionary['end_time']
    header = add_link_dictionary['header']
    out = add_link_dictionary['out']
    user_agent = add_link_dictionary['user_agent']
    cookies = add_link_dictionary['load_cookies']
    referer = add_link_dictionary['referer']



    # make download options and send them to aria2c

    # convert Mega to Kilo, RPC does not Support floating point numbers.
    if limit != '0':
        limit_number = limit[:-1]
        limit_number = float(limit_number)
        limit_unit = limit[-1]
        if limit_unit == 'K':
            limit_number = round(limit_number)
        else:
            limit_number = round(1024*limit_number)
            limit_unit = 'K'
        limit = str(limit_number) + limit_unit

    # create header list
    header_list = []
    if cookies:
        # in xmlrpc cookies must be passed as header
        cookies_list = cookies.split(';')

        for i in cookies_list:
            header_list.append(i)


    if header != None:
        semicolon_split_header = header.split('; ')
        for i in semicolon_split_header:
            equal_split_header = i.split('=', 1)
            join_header = ':'.join(equal_split_header)
            if i != '':
                header_list.append(join_header)

    if len(header_list) == 0:
        header_list = None

    # update status and last_try_date in data_base
    if start_time:
        status = "scheduled"
    else:
        status = "waiting"

    # get last_try_date
    now_date = nowDate()

    # update data_base
    dict_ = {'gid': gid, 'status': status, 'last_try_date': now_date}
    parent.persepolis_db.updateDownloadTable([dict_])


    # call startTime if start_time is available
    # startTime creates sleep loop if user set start_time
    # see startTime function for more information.
    if start_time:
        start_time_status = startTime(start_time, gid, parent)
    else:
        start_time_status = "downloading"

    if start_time_status == "scheduled":
        # read limit value again from data_base before starting download!
        # perhaps user changed this in progress bar window
        add_link_dictionary = parent.persepolis_db.searchGidInAddLinkTable(gid)
        limit = add_link_dictionary['limit_value']

        # convert Mega to Kilo, RPC does not Support floating point numbers.
        if limit != '0':
            limit_number = limit[:-1]
            limit_number = float(limit_number)
            limit_unit = limit[-1]
            if limit_unit == 'K':
                limit_number = round(limit_number)
            else:
                limit_number = round(1024*limit_number)
                limit_unit = 'K'
            limit = str(limit_number) + limit_unit


        # set start_time value to None in data_base!
        parent.persepolis_db.setDefaultGidInAddlinkTable(gid, start_time=True)

    # Find download_path_temp from persepolis_setting
    # if download_path_temp and download_path aren't in same partition on hard disk,
    # then create new temp folder in that partition.
    # Why? when download is completed, file must be moved to download_path from temp folder.
    # It helps moving speed :)
    persepolis_setting.sync()

    # Find default download_path_temp
    download_path_temp = persepolis_setting.value('settings/download_path_temp')

    # Find user's selected download_path
    download_path = add_link_dictionary['download_path'] 

    # check is download_path is existed
    if os.path.isdir(download_path):

        if os.lstat(download_path).st_dev != os.lstat(download_path_temp).st_dev:

            # Create folder and give new temp address from makeTempDownloadDir function.
            # Please checkout osCommands.py for more information.
            download_path_temp = makeTempDownloadDir(download_path) 
    else:
        # write an error in logger
        logger.sendToLog("download_path is not found!", "ERROR")

    if start_time_status != 'stopped':
        # send download request to aria2
        aria_dict = {
            'gid': gid,
            'max-tries': str(persepolis_setting.value('settings/max-tries')),
            'retry-wait': int(persepolis_setting.value('settings/retry-wait')),
            'timeout': int(persepolis_setting.value('settings/timeout')),
            'header': header_list,
            'out': out,
            'user-agent': user_agent,
            'referer': referer,
            'max-download-limit': limit,
            'split': '16',
            'max-connection-per-server': str(connections),
            'min-split-size': '1M',
            'continue': 'true',
            'dir': str(download_path_temp)
        }

        if str(persepolis_setting.value('settings/dont-check-certificate')) == 'yes':
            aria_dict['check-certificate'] = 'false'


        # Persepolis supports 3 type of proxy: http, https, socks5
        # aria2c can't use socks5. so persepolis converts socks to http and send it to aria2c.

        # create ip_port in desired format.
        # for example "127.0.0.1:8118"
        if proxy_host:

            # if user checked socks5 proxy then run converter of socks5 to http
            # don't run new instance, if it's still running
            # write http_host and http_port to aria_dict
            create_new_socks5_to_http_convertor = True
            if proxy_type == 'socks5':
                for instance in parent.socks5_to_http_convertor_list:

                    try:
                        if instance.isRunning() == True:
                            if instance.socks5_host == proxy_host and instance.socks5_port == int(proxy_port) and instance.socks5_username == proxy_user:

                                # so we don't need new stance. get instance information.
                                # "socks5 to http convertor" creates local http server.
                                create_new_socks5_to_http_convertor = False
                                ip_port = instance.http_host + ":" + str(instance.http_port)
                                aria_dict['all-proxy'] = ip_port

                                break
                        else:
                            create_new_socks5_to_http_convertor = True
                    except:
                        create_new_socks5_to_http_convertor = True

                # no instance finded. so create new instance.
                if create_new_socks5_to_http_convertor:

                    new_socks5_to_http_convertor = Socks5ToHttpConvertor(proxy_host, int(proxy_port), proxy_user, proxy_passwd, parent)
                    parent.socks5_to_http_convertor_list.append(new_socks5_to_http_convertor)
                    parent.socks5_to_http_convertor_list[-1].run()
                    
                    # wait until new_socks5_to_http_convertor starts
                    time.sleep(2)
                    # get instance information
                    ip_port = new_socks5_to_http_convertor.http_host + ":" + str(new_socks5_to_http_convertor.http_port)
                    aria_dict['all-proxy'] = ip_port

            # http and https proxy
            else: 
                ip_port = proxy_host + ":" + str(proxy_port)
                aria_dict['all-proxy'] = ip_port
                aria_dict['all-proxy-user'] = proxy_user
                aria_dict['all-proxy-passwd'] = proxy_passwd


        aria_dict_copy = aria_dict.copy()
        # remove empty key[value] from aria_dict
        for aria_dict_key in aria_dict_copy.keys():
            if aria_dict_copy[aria_dict_key] in [None, 'None', '']:
                del aria_dict[aria_dict_key]

        try:
            answer = server.aria2.addUri([link], aria_dict)

            logger.sendToLog(answer + " Starts", 'INFO')
            if end_time:
                endTime(end_time, gid, parent)

        except:

            # write error status in data_base
            dict_ = {'gid': gid, 'status': 'error'}
            parent.persepolis_db.updateDownloadTable([dict_])

            # write ERROR messages in log
            logger.sendToLog("Download did not start", "ERROR")
            error_message = str(traceback.format_exc())
            logger.sendToLog(error_message, "ERROR")

            # return False!
            return False
    else:
        # if start_time_status is "stopped" it means download Canceled by user
        logger.sendToLog("Download Canceled", "INFO")

# this function returns list of download information
def tellActive():
    # get download information from aria2
    try:
        downloads_status = server.aria2.tellActive(
            ['gid', 'status', 'connections', 'errorCode', 'errorMessage', 'downloadSpeed', 'connections', 'dir', 'totalLength', 'completedLength', 'files'])
    except:
        return None, None

    download_status_list = []
    gid_list = []

    # convert download information in desired format.
    for dict_ in downloads_status:
        converted_info_dict = convertDownloadInformation(dict_)

        # add gid to gid_list
        gid_list.append(dict_['gid'])

        # add converted information to download_status_list
        download_status_list.append(converted_info_dict)

    # return results
    return gid_list, download_status_list

# this function returns download status that specified by gid!


def tellStatus(gid, parent):
    # get download status from aria2
    try:
        download_status = server.aria2.tellStatus(
            gid, ['status', 'connections', 'errorCode', 'errorMessage', 'downloadSpeed', 'connections', 'dir', 'totalLength', 'completedLength', 'files'])
        download_status['gid'] = str(gid)
    except:
        return None

    # convert download_status in desired format
    converted_info_dict = convertDownloadInformation(download_status)


# if download has completed , then move file to the download folder
    if (converted_info_dict['status'] == "complete"):
        file_name = converted_info_dict['file_name']

        # find user preferred download_path from addlink_db_table in data_base
        add_link_dictionary = parent.persepolis_db.searchGidInAddLinkTable(gid)

        persepolis_setting.sync()

        download_path = add_link_dictionary['download_path']

        # if user specified download_path is equal to persepolis_setting download_path,
        # then subfolder must added to download path.
        if persepolis_setting.value('settings/download_path') == download_path:
            download_path = findDownloadPath(
                file_name, download_path, persepolis_setting.value('settings/subfolder'))

        # find temp download path
        file_status = str(download_status['files'])
        file_status = file_status[1:-1]
        file_status = ast.literal_eval(file_status)

        path = str(file_status['path'])

        # file_name
        file_name = urllib.parse.unquote(os.path.basename(path))

        # find file_size
        try:
            file_size = int(download_status['totalLength'])
        except:
            file_size = None

        # if file is related to VideoFinder thread, don't move it from temp folder...
        video_finder_dictionary = parent.persepolis_db.searchGidInVideoFinderTable(gid)
        if video_finder_dictionary:
            file_path = path
        else:
            file_path = downloadCompleteAction(parent, path, download_path, file_name, file_size)

        # update download_path in addlink_db_table
        add_link_dictionary['download_path'] = file_path
        parent.persepolis_db.updateAddLinkTable([add_link_dictionary])

# if an error occurred!
    if (converted_info_dict['status'] == "error"):
        # add errorMessage to converted_info_dict
        converted_info_dict['error'] = str(download_status['errorMessage'])

        # remove download from aria2
        server.aria2.removeDownloadResult(gid)

    # return results in dictionary format
    return converted_info_dict

# this function converts download information that received from aria2 in desired format.
# input format must be a dictionary.


def convertDownloadInformation(download_status):
    # find file_name
    try:
        # file_status contains name of download file and link of download file
        file_status = str(download_status['files'])
        file_status = file_status[1:-1]
        file_status = ast.literal_eval(file_status)
        path = str(file_status['path'])
        file_name = urllib.parse.unquote(os.path.basename(path))
        if not(file_name):
            file_name = None

        uris = file_status['uris']
        uri = uris[0]
        link = uri['uri']

    except:

        file_name = None
        link = None

    for i in download_status.keys():
        if not(download_status[i]):
            download_status[i] = None

    # find file_size
    try:
        file_size = float(download_status['totalLength'])
    except:
        file_size = None

    # find downloaded size
    try:
        downloaded = float(download_status['completedLength'])
    except:
        downloaded = None

    # convert file_size and downloaded_size to KiB and MiB and GiB
    if (downloaded != None and file_size != None and file_size != 0):
        file_size_back = file_size

        # converting file_size to KiB or MiB or GiB
        size_str = humanReadableSize(file_size)
        downloaded_back = downloaded

        downloaded_str = humanReadableSize(downloaded)

        # find download percent from file_size and downloaded_size
        file_size = file_size_back
        downloaded = downloaded_back
        percent = int(downloaded * 100 / file_size)
        percent_str = str(percent) + "%"
    else:
        percent_str = None
        size_str = None
        downloaded_str = None

    # find download_speed
    try:
        download_speed = int(download_status['downloadSpeed'])
    except:
        download_speed = 0

    # convert download_speed to desired units.
    # and find estimate_time_left
    if (downloaded != None and download_speed != 0):
        estimate_time_left = int((file_size - downloaded)/download_speed)

        # converting file_size to KiB or MiB or GiB
        download_speed_str = humanReadableSize(download_speed, 'speed') + '/s'

        eta = ""
        if estimate_time_left >= 3600:
            eta = eta + str(int(estimate_time_left/3600)) + "h"
            estimate_time_left = estimate_time_left % 3600
            eta = eta + str(int(estimate_time_left/60)) + "m"
            estimate_time_left = estimate_time_left % 60
            eta = eta + str(estimate_time_left) + "s"
        elif estimate_time_left >= 60:
            eta = eta + str(int(estimate_time_left/60)) + "m"
            estimate_time_left = estimate_time_left % 60
            eta = eta + str(estimate_time_left) + "s"
        else:
            eta = eta + str(estimate_time_left) + "s"
        estimate_time_left_str = eta

    else:
        download_speed_str = "0"
        estimate_time_left_str = None

    # find number of connections
    try:
        connections_str = str(download_status['connections'])
    except:
        connections_str = None

    # find status of download
    try:
        status_str = str(download_status['status'])
    except:
        status_str = None

    # rename active status to downloading
    if (status_str == "active"):
        status_str = "downloading"

    # rename removed status to stopped
    if (status_str == "removed"):
        status_str = "stopped"

    if (status_str == "None"):
        status_str = None

    # set 0 second for estimate_time_left_str if download is completed.
    if status_str == 'complete':
        estimate_time_left_str = '0s'

# return information in dictionary format
    download_info = {
        'gid': download_status['gid'],
        'file_name': file_name,
        'status': status_str,
        'size': size_str,
        'downloaded_size': downloaded_str,
        'percent': percent_str,
        'connections': connections_str,
        'rate': download_speed_str,
        'estimate_time_left': estimate_time_left_str,
        'link': link
    }

    return download_info

# download complete actions!
# this method is returning file_path of file in the user's download folder
# and move downloaded file after download completion.


def downloadCompleteAction(parent, path, download_path, file_name, file_size):

    # remove query from name, If file_name contains query components.
    # check if query existed.
    # query form is 1.mp3?foo=bar 2.mp3?blatz=pow 3.mp3?fizz=buzz
    file_name_split = file_name.split('.')
    file_extension = file_name_split[-1]
    file_name_without_extension = file_name_split[0]

    # if '?' in file_extension, then file_name contains query components.
    if '?' in file_extension:
        file_extension = file_extension.split('?')[0]
        file_name = '.'.join([file_name_without_extension, file_extension])

    # rename file if file already existed
    i = 1
    file_path = os.path.join(download_path, file_name)

    while os.path.isfile(file_path):
        file_name_split = file_name.split('.')
        extension_length = len(file_name_split[-1]) + 1

        new_name = file_name[0:-extension_length] + \
            '_' + str(i) + file_name[-extension_length:]
        file_path = os.path.join(download_path, new_name)
        i = i + 1

    free_space = freeSpace(download_path)

    if free_space != None and file_size != None:

        # compare free disk space and file_size
        if free_space >= file_size:

            # move the file to the download folder
            move_answer = moveFile(str(path), str(file_path), 'file')

            if not(move_answer):
                # write error message in log
                logger.sendToLog('Persepolis can not move file', "ERROR")
                file_path = path

        else:
            # notify user if we have insufficient disk space
            # and do not move file from temp download folder to download folder
            file_path = path
            logger.sendToLog('Insufficient disk space in download folder', "ERROR")

            # show notification
            notifySend("Insufficient disk space!", 'Please change download folder',
                       10000, 'fail', parent=parent)

    else:
        # move the file to the download folder
        move_answer = moveFile(str(path), str(file_path), 'file')

        if not(move_answer):
            logger.sendToLog('Persepolis can not move file', "ERROR")
            file_path = path

    return str(file_path)


# this function returns folder of download according to file extension
def findDownloadPath(file_name, download_path, subfolder):

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


# shutdown aria2
def shutDown():
    try:
        answer = server.aria2.shutdown()
        logger.sendToLog("Aria2 Shutdown : " + str(answer), "INFO")
        return True
    except:
        logger.sendToLog("Aria2 Shutdown Error", "ERROR")
        return False

# downloadStop stops download completely
# this function sends remove request to aria2
# and changes status of download to "stopped" in data_base


def downloadStop(gid, parent):
    # get download status from data_base
    dict_ = parent.persepolis_db.searchGidInDownloadTable(gid)
    status = dict_['status']

    # if status is "scheduled", then download request has not been sended to aria2!
    # so no need to send stop request to aria2.
    # if status in not "scheduled" so stop request must be sended to aria2.
    if status != 'scheduled':
        try:
            # send remove download request to aria2.
            # see aria2 documentation for more information.
            answer = server.aria2.remove(gid)
            if status == 'downloading':
                server.aria2.removeDownloadResult(gid)
        except:
            answer = "None"

        # write a messages in log and terminal
        logger.sendToLog(answer + " stopped", "INFO")

    # if download has not been completed yet,
    # so just chang status of download to "stopped" in data base.
    else:
        answer = 'stopped'

    if status != 'complete':
        # change start_time end_time and after_download value to None in date base
        parent.persepolis_db.setDefaultGidInAddlinkTable(gid,
                                                         start_time=True, end_time=True, after_download=True)

        # change status of download to "stopped" in data base
        dict_ = {'gid': gid, 'status': 'stopped'}
        parent.persepolis_db.updateDownloadTable([dict_])

    return answer


# downloadPause pauses download
def downloadPause(gid):
    # see aria2 documentation for more information

    # send pause request to aria2 .
    try:
        answer = server.aria2.pause(gid)
    except:
        answer = None

    logger.sendToLog(str(answer) + " paused", "INFO")
    return answer


# downloadUnpause unpauses download
def downloadUnpause(gid):
    try:
        # send unpause request to aria2
        answer = server.aria2.unpause(gid)
    except:
        answer = None

    logger.sendToLog(str(answer) + " unpaused", "INFO")

    return answer

#  limitSpeed limits download speed


def limitSpeed(gid, limit):
    limit = str(limit)
# convert Mega to Kilo, RPC does not Support floating point numbers.
    if limit != '0':
        limit_number = limit[:-1]
        limit_number = float(limit_number)
        limit_unit = limit[-1]
        if limit_unit == 'K':
            limit_number = round(limit_number)
        else:
            limit_number = round(1024*limit_number)
            limit_unit = 'K'
        limit = str(limit_number) + limit_unit

    try:
        server.aria2.changeOption(gid, {'max-download-limit': limit})
        logger.sendToLog("Download speed limit  value is changed", "INFO")

    except:
        logger.sendToLog("Speed limitation was unsuccessful", "ERROR")


# this function returns GID of active downloads in list format.
def activeDownloads():
    try:
        answer = server.aria2.tellActive(['gid'])
    except:
        answer = []

    active_gids = []
    for i in answer:
        # extract gid from dictionary
        dict_ = i
        gid = dict_['gid']

        # add gid to list
        active_gids.append(gid)

    # return results
    return active_gids


# This function returns data and time in string format
# for example >> 2017/09/09 , 13:12:26
def nowDate():
    date = time.strftime("%Y/%m/%d , %H:%M:%S")
    return date

# sigmaTime gets hours and minutes for input.
# and converts hours to minutes and returns summation in minutes
# input format is HH:MM


def sigmaTime(time):
    hour, minute = time.split(":")
    return (int(hour)*60 + int(minute))

# nowTime returns now time in HH:MM format!


def nowTime():
    now_time = time.strftime("%H:%M")
    return sigmaTime(now_time)

# this function creates sleep time,if user sets "start time" for download.


def startTime(start_time, gid, parent):
    # write some messages
    logger.sendToLog("Download starts at " + start_time, "INFO")

    # start_time that specified by user
    sigma_start = sigmaTime(start_time)

    # get current time
    sigma_now = nowTime()

    status = 'scheduled'

  # this loop is continuing until download time arrival!
    while sigma_start != sigma_now:
        time.sleep(2.1)
        sigma_now = nowTime()

        # check download status from data_base
        dict_ = parent.persepolis_db.searchGidInDownloadTable(gid)
        data_base_download_status = dict_['status']

        # if data_base_download_status = stopped >> it means that user
        # canceled download and loop must break!
        if data_base_download_status == 'stopped':
            status = 'stopped'
            break
        else:
            status = 'scheduled'

# if user canceled download , then return 'stopped' and if download time arrived then return 'scheduled'!
    return status


def endTime(end_time, gid, parent):
    logger.sendToLog("End time is activated " + gid, "INFO")
    sigma_end = sigmaTime(end_time)

    # get current time
    sigma_now = nowTime()

    answer = 'end'
    # while current time is not equal to end_time, continue the loop
    while sigma_end != sigma_now:

        # get download status from data_base
        dict_ = parent.persepolis_db.searchGidInDownloadTable(gid)
        status = dict_['status']

        # check download status
        if status == 'scheduled' or status == 'downloading' or status == 'paused' or status == 'waiting':

            # download continues!
            answer = 'continue'

        else:

            # Download completed or stopped by user
            # so break the loop
            answer = 'end'
            logger.sendToLog("Download has been finished! " + str(gid), "INFO")
            break

        # get current time
        sigma_now = nowTime()
        time.sleep(2.1)

    # Time is up!
    if answer != 'end':
        logger.sendToLog("Time is up!", "INFO")
        answer = downloadStop(gid, parent)
        i = 0
        # try to stop download 10 times
        while answer == 'None' and (i <= 9):
            time.sleep(1)
            answer = downloadStop(gid, parent)
            i = i + 1

        # If aria2c not respond, so kill it. R.I.P :))
        if (answer == 'None') and (os_type != OS.WINDOWS):

            subprocess.Popen(['killall', 'aria2c'],
                             stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stdin=subprocess.PIPE,
                             shell=False)

        # change end_time value to None in data_base
        parent.persepolis_db.setDefaultGidInAddlinkTable(gid, end_time=True)
