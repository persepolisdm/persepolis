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

import subprocess
import xmlrpc.client
import os
import time
import ast
import shutil
import platform
import sys
from persepolis.scripts import logger
from PyQt5.QtCore import QSettings
import urllib.parse
import traceback

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
def startAria():
    # in Linux and BSD
    if os_type == 'Linux' or os_type == 'FreeBSD' or os_type == 'OpenBSD':
        os.system("aria2c --version 1> /dev/null")
        os.system("aria2c --no-conf  --enable-rpc --rpc-listen-port '" +
                  str(port) + "' --rpc-max-request-size=2M --rpc-listen-all --quiet=true &")

    # in macintosh
    elif os_type == 'Darwin':
        if aria2_path == "" or aria2_path == None or os.path.isfile(str(aria2_path)) == False:
            cwd = sys.argv[0]
            cwd = os.path.dirname(cwd)
            aria2d = cwd + "/aria2c"
        else:
            aria2d = aria2_path

        os.system("'" + aria2d + "' --version 1> /dev/null")
        os.system("'" + aria2d + "' --no-conf  --enable-rpc --rpc-listen-port '" +
                  str(port) + "' --rpc-max-request-size=2M --rpc-listen-all --quiet=true &")

    # in Windows
    elif os_type == 'Windows':
        if aria2_path == "" or aria2_path == None or os.path.isfile(str(aria2_path)) == False:
            cwd = sys.argv[0]
            cwd = os.path.dirname(cwd)
            aria2d = os.path.join(cwd, "aria2c.exe")  # aria2c.exe path
        else:
            aria2d = aria2_path

        NO_WINDOW = 0x08000000


        # aria2 command in windows
        subprocess.Popen([aria2d, '--no-conf', '--enable-rpc', '--rpc-listen-port=' + str(port),
                          '--rpc-max-request-size=2M', '--rpc-listen-all', '--quiet=true'], shell=False, creationflags=NO_WINDOW)

    time.sleep(2)

    # check that starting is successful or not!
    answer = aria2Version()

    # return result
    return answer

# check aria2 release version . Persepolis uses this function to
# check that aria2 RPC conection is available or not. 
def aria2Version():
    try:
        answer = server.aria2.getVersion()
    except:
        # write ERROR messages in terminal and log
        print("aria2 did not respond!")
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
    ip = add_link_dictionary['ip']
    port = add_link_dictionary['port']
    proxy_user = add_link_dictionary['proxy_user']
    proxy_passwd = add_link_dictionary['proxy_passwd']
    download_user = add_link_dictionary['download_user']
    download_passwd = add_link_dictionary['download_passwd']
    connections = add_link_dictionary['connections']
    limit = str(add_link_dictionary['limit_value'])
    start_time = add_link_dictionary['start_time']
    end_time = add_link_dictionary['end_time']
    header = add_link_dictionary['header']
    out = add_link_dictionary['out']
    user_agent = add_link_dictionary['user_agent']
    cookies = add_link_dictionary['load_cookies']
    referer = add_link_dictionary['referer']



    # make header option
    header_list = []
    header_list.append("Cookie: " + str(cookies))

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
    if header != None:
        semicolon_split_header = header.split('; ')
        for i in semicolon_split_header:
            equal_split_header = i.split('=',1)
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
    dict = {'gid': gid, 'status': status, 'last_try_date': now_date}
    parent.persepolis_db.updateDownloadTable([dict])


    # create ip_port from ip and port in desired format. 
    # for example "127.0.0.1:8118"
    if ip:
        ip_port = str(ip) + ":" + str(port)
    else:
        ip_port = ""

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

# set start_time value to None in data_base!
        parent.persepolis_db.setDefaultGidInAddlinkTable(gid, start_time=True)

# find download_path_temp from persepolis_setting
    persepolis_setting.sync()
    download_path_temp = persepolis_setting.value('settings/download_path_temp')

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
            'all-proxy': ip_port,
            'max-download-limit': limit,
            'all-proxy-user': str(proxy_user),
            'all-proxy-passwd': str(proxy_passwd),
            'http-user': str(download_user),
            'http-passwd': str(download_passwd),
            'split': '16',
            'max-connection-per-server': str(connections),
            'min-split-size': '1M',
            'continue': 'true',
            'dir': str(download_path_temp)
        }

        if not link.startswith("https"):
            aria_dict ['http-user']= str(download_user)
            aria_dict ['http-passwd']= str(download_passwd)

        try:
            answer = server.aria2.addUri([link], aria_dict)

            print(answer + " Starts")
            logger.sendToLog(answer + " Starts", 'INFO')
            if end_time:
                endTime(end_time, gid, parent)

        except:

            # write error status in data_base
            dict = {'gid': gid, 'status': 'error'}
            parent.persepolis_db.updateDownloadTable([dict])

            # write ERROR messages in log
            print("Download did not start")
            logger.sendToLog("Download did not start", "ERROR")
            error_message = str(traceback.format_exc())
            logger.sendToLog(error_message, "ERROR")
            print(error_message)


            # return None!
            return None
    else:
        # if start_time_status is "stopped" it means download Canceled by user
        print("Download Canceled")
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
    for dict in downloads_status:
        converted_info_dict = convertDownloadInformation(dict)

        # add gid to gid_list
        gid_list.append(dict['gid'])

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
 
        # find download_path from addlink_db_table in data_base
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
        file_name = urllib.parse.unquote(os.path.basename(path))

        file_path = downloadCompleteAction(path, download_path, file_name)

        # update download_path in addlink_db_table
        add_link_dictionary['download_path'] = file_path
        parent.persepolis_db.updateAddLinkTable([add_link_dictionary])

# if an error occured!
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

    # convert file_size and downloaded_size to KB and MB and GB
    if (downloaded != None and file_size != None and file_size != 0):
        file_size_back = file_size
        if int(file_size/1073741824) != 0:
            file_size = file_size/1073741824
            size_str = str(round(file_size, 2)) + " GB"
        elif int(file_size/1048576) != 0:
            size_str = str(int(file_size/1048576)) + " MB"
        elif int(file_size/1024) != 0:
            size_str = str(int(file_size/1024)) + " KB"
        else:
            size_str = str(file_size)
        downloaded_back = downloaded
        if int(downloaded/1073741824) != 0:
            downloaded = downloaded/1073741824
            downloaded_str = str(round(downloaded, 2)) + " GB"
        elif int((downloaded/1048576)) != 0:
            downloaded_str = str(int(downloaded/1048576)) + " MB"
        elif int(downloaded/1024) != 0:
            downloaded_str = str(int(downloaded/1024)) + " KB"
        else:
            downloaded_str = str(downloaded)

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
        if int((download_speed/1073741824)) != 0:
            download_speed = download_speed/1073741824
            download_speed_str = str(round(download_speed, 2)) + " GB/S"
        elif int((download_speed/1048576)) != 0:
            download_speed_num = download_speed/1048576
            download_speed_str = str(round(download_speed_num, 2)) + " MB/S"
        elif int((download_speed/1024)) != 0:
            download_speed_str = str(int(download_speed/1024)) + " KB/S"
        else:
            download_speed_str = str(download_speed)

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
def downloadCompleteAction(path, download_path, file_name):
    i = 1
    file_path = os.path.join(download_path, file_name)

# rename file if file already existed
    while os.path.isfile(file_path):
        file_name_split = file_name.split('.')
        extension_length = len(file_name_split[-1]) + 1

        new_name = file_name[0:-extension_length] + \
            '_' + str(i) + file_name[-extension_length:]
        file_path = os.path.join(download_path, new_name)
        i = i + 1

# move the file to the download folder
    try:
        shutil.copy(str(path) ,str(file_path) )
        os.remove(path)

    except:
        print('Persepolis can not move file')
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

        elif file_extension in video:
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
        print("Aria2 Shutdown : " + str(answer))
        logger.sendToLog("Aria2 Shutdown : " + str(answer), "INFO")
        return True 
    except:
        print("Aria2 Shutdown Error")
        logger.sendToLog("Aria2 Shutdown Error", "ERROR")
        return False

# downloadStop stops download completely
# this function sends remove request to aria2
# and changes status of download to "stopped" in data_base
def downloadStop(gid, parent):
    # get download status from data_base
    dict = parent.persepolis_db.searchGidInDownloadTable(gid)
    status = dict['status']

    # if status is "scheduled", then download request has not been sended to aria2!
    # so no need to send stop request to aria2. 
    # if status in not "scheduled" so stop request must be sended to aria2. 
    if status != 'scheduled':
        try:
            # send remove download request to aira2. 
            # see aria2 documentation for more informations.
            answer = server.aria2.remove(gid)
            if status == 'downloading':
                server.aria2.removeDownloadResult(gid)
        except:
            answer = "None"

        # write a messages in log and terminal
        print(answer + " stopped")
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
        dict = {'gid': gid, 'status': 'stopped'}        
        parent.persepolis_db.updateDownloadTable([dict])

    return answer


# downloadPause pauses download
def downloadPause(gid):
# see aria2 documentation for more information

# send pause request to aira2 .
    try:
        answer = server.aria2.pause(gid)
    except:
        answer = None

    print(str(answer) + " paused")
    logger.sendToLog(str(answer) + " paused", "INFO")
    return answer


# downloadUnpause unpauses download
def downloadUnpause(gid):
    try:
        # send unpause request to aria2
        answer = server.aria2.unpause(gid)
    except:
        answer = None

    print(str(answer) + " unpaused")
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
        print("Download speed limit value is changed")
        logger.sendToLog("Download speed limit  value is changed", "INFO")

    except:
        print("speed limitation operation was unsuccessful")
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
        dict = i
        gid = dict['gid']

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
    print("Download starts at " + start_time)
    logger.sendToLog("Download starts at " + start_time, "INFO")

    # start_time that specified by user
    sigma_start = sigmaTime(start_time) 

    # get current time
    sigma_now = nowTime()  

    status = 'scheduled'

  # this loop is countinuing until download time arrival!
    while sigma_start != sigma_now:
        time.sleep(2.1)
        sigma_now = nowTime()

        # check download status from data_base
        dict = parent.persepolis_db.searchGidInDownloadTable(gid)
        data_base_download_status = dict['status']
        
        # if data_base_download_status = stopped >> it means that user
        # canceled download , and loop must be breaked!
        if data_base_download_status == 'stopped':
            status = 'stopped'
            break
        else:
            status = 'scheduled'

# if user canceled download , then return 'stopped' and if download time arrived then return 'scheduled'!
    return status  


def endTime(end_time, gid, parent):
    print("end time is actived " + gid)
    logger.sendToLog("End time is activated " + gid, "INFO")
    sigma_end = sigmaTime(end_time)

    # get current time
    sigma_now = nowTime()

    # while current time is not equal to end_time, continue the loop
    while sigma_end != sigma_now:

        # get download status from data_base
        dict = parent.persepolis_db.searchGidInDownloadTable(gid) 
        status = dict['status']

        # check download status
        if status == 'downloading' or status == 'paused' or status == 'waiting':
            # download continues!
            answer = 'continue'
        else:
            # Download completed or stopped by user
            # so break the loop
            answer = 'end'
            print("Download ended before! " + str(gid))
            logger.sendToLog("Download has been finished! " + str(gid), "INFO")
            break

        # get current time
        sigma_now = nowTime()
        time.sleep(2.1)

    # Time is up!
    if answer != 'end':
        print("Time is Up")
        logger.sendToLog("Time is up!", "INFO")
        answer = downloadStop(gid, parent)
        i = 0
        # try to stop download 10 times
        while answer == 'None' and (i <= 9):
            time.sleep(1)
            answer = downloadStop(gid, parent)
            i = i + 1

        # If aria2c not respond, so kill it. R.I.P :)) 
        if (answer == 'None') and (os_type != 'Windows'):
            os.system("killall aria2c")

        # change end_time value to None in data_base
        parent.persepolis_db.setDefaultGidInAddlinkTable(gid, end_time=True)
