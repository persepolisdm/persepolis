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

import string
import subprocess
import xmlrpc.client
import os
import time
import ast
import shutil
from newopen import Open , readList , writeList
import platform , sys



home_address = os.path.expanduser("~")
config_folder = str(home_address) + "/.config/persepolis_download_manager"
download_info_folder = config_folder +  "/download_info"
download_list_file = config_folder + "/download_list_file"
download_list_file_active = config_folder + "/download_list_file_active"
config_folder = str(home_address) + "/.config/persepolis_download_manager"

#setting
setting_file = config_folder + '/setting'
f = Open(setting_file)
setting_file_lines = f.readlines()
f.close()
setting_dict_str = str(setting_file_lines[0].strip())
setting_dict = ast.literal_eval(setting_dict_str) 


host = 'localhost'
port = int(setting_dict['rpc-port'])

#RPC
SERVER_URI_FORMAT = 'http://{}:{:d}/rpc'
server_uri = SERVER_URI_FORMAT.format(host, port)
server = xmlrpc.client.ServerProxy(server_uri, allow_none=True)

#starting aria2 with RPC
def startAria():
    if platform.system() == 'Linux':
        os.system("aria2c --version 1> /dev/null")
        os.system("aria2c --no-conf  --enable-rpc --rpc-listen-port '" + str(port) + "' --rpc-max-request-size '10M' --rpc-listen-all --quiet=true &")
    else:
        cwd = sys.argv[0]
        cwd = os.path.dirname(cwd)
        aria2d = cwd + "/aria2c"
        os.system("'" + aria2d + "' --version 1> /dev/null")
        os.system("'" + aria2d + "' --no-conf  --enable-rpc --rpc-listen-port '" + str(port) + "' --rpc-max-request-size '10M' --rpc-listen-all --quiet=true &")

    time.sleep(2)
    answer = aria2Version()
    return answer

#checking aria2 release version . Persepolis is usig this function to check that aria2 RPC conection is available or not
def aria2Version():
    try : 
        answer = server.aria2.getVersion()
    except :
        print("aria2 not respond!")
        answer = "did not respond"
    return answer
 
#this function is sending download request to aria2        
def downloadAria(gid):
#add_link_dictionary is a dictionary that contains user download request information
    download_info_file = download_info_folder + "/" + gid
    download_info_file_list = readList(download_info_file)
    add_link_dictionary = download_info_file_list[9]

    link = add_link_dictionary ['link']
    ip = add_link_dictionary['ip']
    port = add_link_dictionary['port']
    proxy_user = add_link_dictionary['proxy_user']
    proxy_passwd = add_link_dictionary['proxy_passwd']
    download_user = add_link_dictionary['download_user']
    download_passwd = add_link_dictionary['download_passwd']
    connections = add_link_dictionary['connections']
    limit= add_link_dictionary['limit']
    start_hour = add_link_dictionary['start_hour']
    start_minute = add_link_dictionary['start_minute']
    end_hour = add_link_dictionary['end_hour']
    end_minute = add_link_dictionary['end_minute']
    header = add_link_dictionary['header']
    out = add_link_dictionary['out']
    user_agent = add_link_dictionary['user-agent']
    cookies = add_link_dictionary['load-cookies']
    referer = add_link_dictionary['referer']
     
    #setting time and date for last_try_date
    now_date_list = nowDate()
    add_link_dictionary [ 'last_try_date'] = now_date_list 

    #making header option
    header_list = []
    if cookies != None :
        semicolon_split_cookies = cookies.split('; ')
        for i in semicolon_split_cookies:
            equal_split_cookie = i.split('=')
            join_cookie = ':'.join(equal_split_cookie)
            if i != '':
                header_list.append(join_cookie)

    if header != None :
        semicolon_split_header = header.split('; ')
        for i in semicolon_split_header:
            equal_split_header = i.split('=')
            join_header = ':'.join(equal_split_header)
            if i != '':
                header_list.append(join_header)
    
    if len(header_list) == 0 :
        header_list = None

    if start_hour != None :
        download_info_file_list[1] = "scheduled"

    #writing new informations on download_info_file
    download_info_file_list[9] = add_link_dictionary 
    writeList(download_info_file,download_info_file_list)

    if ip :
        ip_port = str(ip) + ":" + str(port)
    else:
        ip_port = "" 

    if start_hour != None :
        start_time_status = startTime(start_hour , start_minute , gid)
    else : 
        start_time_status = "downloading"


    if start_time_status == "scheduled":
#reading new limit option before starting download! perhaps user changed this in progress bar window
        download_info_file_list = readList(download_info_file) 
        add_link_dictionary = download_info_file_list[9]
        
        limit = add_link_dictionary['limit']

#eliminating start_hour and start_minute!         
        add_link_dictionary['start_hour'] = None
        add_link_dictionary['start_minute'] = None
        download_info_file_list [9] = add_link_dictionary
        writeList(download_info_file , download_info_file_list)



#finding download_path_temp from setting_file
    f = Open(setting_file)
    setting_file_lines = f.readlines()
    f.close()
    setting_dict_str = str(setting_file_lines[0].strip())
    setting_dict = ast.literal_eval(setting_dict_str) 

    download_path_temp = setting_dict ['download_path_temp' ] 


    if start_time_status != 'stopped':
#sending download request to aria2
        if link[0:5] != "https":
            aria_dict = {'gid':gid ,'max-tries' : str(setting_dict['max-tries']) , 'retry-wait': int(setting_dict['retry-wait']) , 'timeout' : int(setting_dict['timeout']) , 'header': header_list ,'out': out , 'user-agent': user_agent ,  'referer': referer ,  'all-proxy': ip_port , 'max-download-limit': limit , 'all-proxy-user':str(proxy_user), 'all-proxy-passwd':str(proxy_passwd), 'http-user':str(download_user), 'http-passwd':str(download_passwd) , 'split':'16', 'max-connection-per-server':str(connections) , 'min-split-size':'1M', 'continue':'true', 'dir':str(download_path_temp) } 
        else:
            aria_dict = {'gid':gid ,'max-tries' : str(setting_dict['max-tries']) , 'retry-wait': int(setting_dict['retry-wait']) , 'timeout' : int(setting_dict['timeout']) , 'header': header_list ,'out': out , 'user-agent': user_agent ,  'referer': referer ,  'all-proxy': ip_port , 'max-download-limit': limit , 'all-proxy-user':str(proxy_user), 'all-proxy-passwd':str(proxy_passwd), 'split':'16', 'max-connection-per-server':str(connections) , 'min-split-size':'1M', 'continue':'true', 'dir':str(download_path_temp) } 


        try:
            if ("http" in link[0:5]): 
                answer = server.aria2.addUri([link],aria_dict)
            else:
                answer = server.aria2.addUri([link],aria_dict)

            print(answer + " Starts")
            if end_hour != None:
                endTime(end_hour , end_minute , gid)

        except:
            print("None Starts")
#if request was unsuccessful return None!
            return 'None'
    else :
#if start_time_status is "stopped" it means download Canceled by user
        print("Download Canceled")

def downloadStatus(gid):
    try :
        download_status = server.aria2.tellStatus(gid ,['status' ,'connections' ,'errorCode' , 'errorMessage' ,'downloadSpeed' , 'connections' , 'dir' , 'totalLength' , 'completedLength','files']  )
    except:
        download_status = {'status': None ,'connections' : None ,'errorCode' : None , 'errorMessage' : None ,'downloadSpeed' : None , 'connections' : None , 'dir' : None , 'totalLength' : None , 'completedLength': None ,'files': None } 
#file_status contains name of download file 
    try:    
        file_status = str(download_status['files'])
        file_status = file_status[1:-1]
        file_status = ast.literal_eval(file_status)
        path = file_status['path']
        file_name = str(path.split("/")[-1])
        if not(file_name):
            file_name = None
    except :
            file_name = None

    for i in download_status.keys():
        if not(download_status[i]):
            download_status[i] = None
    try:
        file_size = float (download_status['totalLength'])
    except:
        file_size = None
    try:    
        downloaded = float (download_status['completedLength'])
    except:
        downloaded = None
           
    if (downloaded != None and file_size != None and file_size != 0):
        file_size_back = file_size
        if int(file_size/1073741824) != 0 :
            file_size = file_size/1073741824
            size_str = str(round(file_size , 2)) + " GB"
        elif int(file_size/1048576) != 0:
            size_str = str(int(file_size/1048576)) + " MB"
        elif int(file_size/1024) != 0:
            size_str = str(int(file_size/1024)) + " KB"
        else:
            size_str = str(file_size)
        downloaded_back = downloaded 
        if int(downloaded/1073741824) != 0:
            downloaded = downloaded/1073741824
            downloaded_str = str(round(downloaded , 2)) + " GB"
        elif int((downloaded/1048576)) != 0:
            downloaded_str = str(int(downloaded/1048576)) + " MB"
        elif int(downloaded/1024) != 0:
            downloaded_str = str(int(downloaded/1024)) + " KB"
        else:
            downloaded_str = str(downloaded)
        file_size = file_size_back
        downloaded = downloaded_back
        percent =  int(downloaded * 100 / file_size)
        percent_str = str(percent) + " %"
    else:
        percent_str = None 
        size_str = None
        downloaded_str = None

    try:
        download_speed = int(download_status['downloadSpeed'])
    except:
        download_speed = 0 

    if (downloaded != None and  download_speed != 0):
        estimate_time_left = int((file_size - downloaded)/download_speed)
        if int((download_speed/1073741824)) != 0:
            download_speed = download_speed/1073741824 
            download_speed_str = str(round(download_speed , 2))+ " GB/S"
        elif int((download_speed/1048576)) != 0:
            download_speed_num = download_speed/1048576
            download_speed_str = str(round(download_speed_num , 2)) + " MB/S"
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
        else :
            eta = eta + str(estimate_time_left) + "s" 
        estimate_time_left_str = eta

    else:
        download_speed_str = "0" 
        estimate_time_left_str = None


    try:
        connections_str = str(download_status['connections'])
    except:
        connections_str = None

    try :
        status_str = str(download_status['status'])
    except :
        status_str = None


    download_info_file = download_info_folder + "/" + gid
    download_info_file_list = readList(download_info_file)

    add_link_dictionary = download_info_file_list[9]

    download_path = add_link_dictionary['download_path']
    final_download_path = add_link_dictionary ['final_download_path']


#if final_download_path did not defined and download_path equaled to user default download folder then this section is finding final_download_path according to file extension
    if final_download_path == None :
        if file_name != None :
#finding default download_path
            f = Open(setting_file)
            setting_file_lines = f.readlines()
            f.close()
            setting_dict_str = str(setting_file_lines[0].strip())
            setting_dict = ast.literal_eval(setting_dict_str) 

            if setting_dict['download_path'] == download_path :
                final_download_path = findDownloadPath(file_name , download_path)
                add_link_dictionary ['final_download_path'] = final_download_path
            else :
                final_download_path = download_path 
                add_link_dictionary['final_download_path'] = final_download_path
#if download completed move file to the download folder
    if (status_str == "complete"):
        if final_download_path != None :
            download_path = final_download_path
        file_path = downloadCompleteAction(path , download_path ,file_name)
        add_link_dictionary [ 'file_path'] = file_path
        file_path_split = file_path.split('/')
        file_name = str(file_path_split[-1])
#rename active status to downloading
    if (status_str == "active"):
        status_str = "downloading"
#rename removed status to stopped
    if (status_str == "removed" ):
        status_str = "stopped"

    if (status_str == "error"):
        add_link_dictionary["error"] = str(download_status['errorMessage'])

        

    if (status_str == "None"):
        status_str = None

#setting firs_try_date and last_try_date
    date_list = add_link_dictionary ['firs_try_date']
    firs_try_date = str(date_list[0]) + '/' + str(date_list[1]) + '/' + str(date_list[2]) + ' , ' + str(date_list[3]) + ':' +  str(date_list[4]) + ':' + str(date_list[5])

    date_list = add_link_dictionary ['last_try_date']
    last_try_date = str(date_list[0]) + '/' + str(date_list[1]) + '/' + str(date_list[2]) + ' , ' + str(date_list[3]) + ':' +  str(date_list[4]) + ':' + str(date_list[5])

    download_info = [file_name , status_str , size_str , downloaded_str ,  percent_str , connections_str , download_speed_str ,estimate_time_left_str , None , add_link_dictionary , firs_try_date , last_try_date ]

   
    for i in range(12):
        if download_info[i] != None:
            download_info_file_list[i] = download_info[i]
 
        
    writeList(download_info_file , download_info_file_list)

    return 'ready'


#download complete actions!
def downloadCompleteAction( path ,download_path , file_name):
    i = 1
    file_path = download_path + '/' + file_name
#rename file if file already existed
    while  os.path.isfile(file_path):
        file_name_split = file_name.split('.')
        extension_length = len(file_name_split[-1]) + 1
        file_path = download_path + '/' + file_name[0:-extension_length] + '_' + str(i) + file_name[-extension_length:]
        i = i + 1

#move the file to the download folder
    try:
        shutil.move(str(path) ,str(file_path) )
    except:
        print('Persepolis can not move file')

    return str(file_path)


#this function is returning folder of download according to file extension    
def findDownloadPath(file_name , download_path):

    file_name_split = file_name.split('.')
    file_extension = file_name_split[-1]
    file_extension = file_extension.lower() #converting extension letters to lower case
    audio = ['act','aiff','aac','amr','ape','au','awb','dct','dss','dvf','flac','gsm','iklax','ivs','m4a','m4p','mmf','mp3','mpc','msv','ogg','oga','opus','ra','raw','sln','tta','vox','wav','wma','wv']
    video = ['3g2','3gp','asf','avi','drc','flv','m4v','mkv','mng','mov','qt','mp4','m4p','mpg','mp2','mpeg','mpe','mpv','m2v','mxf','nsv','ogv','rmvb','roq','svi','vob','webm','wmv','yuv','rm']
    document = ['doc','docx','html','htm','fb2','odt','sxw','pdf','ps','rtf','tex','txt']
    compressed = ['a','ar','cpio','shar','LBR','iso','lbr','mar','tar','bz2','F','gz','lz','lzma','lzo','rz','sfark','sz','xz','Z','z','infl','7z','s7z','ace','afa','alz','apk','arc','arj','b1','ba','bh','cab','cfs','cpt','dar','dd','dgc','dmg','ear','gca','ha','hki','ice','jar','kgb','lzh','lha','lzx','pac','partimg','paq6','paq7','paq8','pea','pim','pit','qda','rar','rk','sda','sea','sen','sfx','sit','sitx','sqx','tar.gz','tgz','tar.Z','tar.bz2','tbz2','tar.lzma','tlz','uc','uc0','uc2','ucn','ur2','ue2','uca','uha','war','wim','xar','xp3','yz1','zip','zipx','zoo','zpaq','zz','ecc','par','par2']
    if file_extension in audio :
        return download_path + '/Audios'
    elif file_extension in video :
        return download_path + '/Videos'
    elif file_extension in document :
        return download_path + '/Documents'
    elif file_extension in compressed :
        return download_path + '/Compressed'
    else:
        return download_path + '/Others'



        
#shutdown aria2
def shutDown():
    try:
        answer = server.aria2.shutdown()
        print("Aria2 Shutdown : " + str(answer))
        return 'ok'
    except:
        print("Aria2 Shutdown Error")
        return 'error'


#downloadStop stops download completely
def downloadStop(gid):
    download_info_file = download_info_folder + "/" + gid
    download_info_file_list = readList(download_info_file)
    version_answer = 'ok'
#if status is scheduled so download request is not sended to aria2 yet!
    status = download_info_file_list[1] 
    if status != 'scheduled':
        try :
        #this section is sending request to aria2 to removing download. see aria2 documentation for more informations 
            answer = server.aria2.remove(gid)
            if status == 'downloading':
                server.aria2.removeDownloadResult(gid)
        except :
            answer = str ("None")
        print(answer + " stopped")
    else :
        answer = 'stopped'

    if status != 'complete':
        add_link_dictionary = download_info_file_list[9]
        add_link_dictionary['start_hour'] = None
        add_link_dictionary['start_minute'] = None
        add_link_dictionary['end_hour'] = None
        add_link_dictionary['end_minute'] = None
        add_link_dictionary['after_download'] = 'None'

        download_info_file_list[1] = "stopped"
        download_info_file_list[9] = add_link_dictionary
        writeList(download_info_file , download_info_file_list)
    return answer
 

#downloadPause pauses download
def downloadPause(gid):
    download_info_file = download_info_folder + "/" + gid
    download_info_file_list = readList(download_info_file)
#this section is sending pause request to aira2 . see aria2 documentation for more informations
    try :
        answer = server.aria2.pause(gid)
        version_answer = 'ok'
    except :
        answer = str("None")
        
    print(answer + " paused")

    return answer



#downloadUnpause unpauses download
def downloadUnpause(gid):
    download_info_file = download_info_folder + "/" + gid
    download_info_file_list = readList(download_info_file)
#this section is sending unpause request to aria2 . see aria2 documentation for more informations.
    try :
        answer = server.aria2.unpause(gid)
        version_answer = 'ok'
    except :
        answer = str("None")

    return answer

#limiting download speed
def limitSpeed(gid ,limit):
    try :
        answer = server.aria2.changeOption(gid, {'max-download-limit': limit })
    except:
        answer = str("None")
    print(answer)

#this function returning  GID of active downloads
def activeDownloads():
    try:
        answer = server.aria2.tellActive(['gid'])
    except:
        answer = [] 
    active_gids = []
    for i in answer :
        dict = i 
        gid = dict['gid']
        active_gids.append(gid)

    return active_gids


def nowDate():
    date_list = []
    for i in ['%Y' , '%m' , '%d' , '%H' , '%M' , '%S' ] :
        date_list.append(time.strftime(i))
    return date_list
#sigmaTime get hours and minutes for input . convert hours to minutes and return summation in minutes        
def sigmaTime(hour,minute):
    return (int(hour)*60 + int(minute))

#nowTime returns now time!
def nowTime():
    now_time_hour = time.strftime("%H")
    now_time_minute = time.strftime("%M")
    return sigmaTime(now_time_hour,now_time_minute)

def startTime(start_hour , start_minute , gid):
    print("Download starts at " + start_hour + ":" + start_minute )
    sigma_start = sigmaTime(start_hour , start_minute) #getting sima time
    sigma_now = nowTime() #getting sigma now time
    download_info_file = download_info_folder + "/" + gid #getting download_info_file path
    status = 'scheduled' #defining status
    while sigma_start != sigma_now : #this loop is countinuing until download time arrival!
        time.sleep(2.1)
        sigma_now = nowTime()
        try: #this part is reading download informations for finding download status , perhaps user canceled download! try command used for avoiding some problems when readList reading files
            download_info_file_list = readList(download_info_file)
        except:
            download_info_file_list = [ 'some_name' , 'scheduled' ]
        
        if download_info_file_list[1] == 'stopped' : #if download_info_file_list[1] = stopped >> it means that user canceled download , and loop is breaking!
            status = 'stopped'
            break
        else :
            status = 'scheduled'
    return status #if user canceled download , then 'stopped' returns and if download time arrived then 'scheduled' returns!

def endTime(end_hour , end_minute , gid):
    time.sleep(1)
    print("end time actived " + gid)
    sigma_end = sigmaTime(end_hour , end_minute) 
    sigma_now = nowTime()
    download_info_file = download_info_folder + "/" + gid

    while sigma_end != sigma_now : 
        status_file = 'no'
#waiting for start downloading :
        while status_file == 'no':
            time.sleep(0.5)
            try :
                download_info_file_list = readList(download_info_file)
                status_file = 'yes'
                status = download_info_file_list[1]
            except:
                status_file = 'no'
#checking download's status
        if status == 'downloading' or status == 'paused' or status == 'waiting' :
            answer = 'continue'
        else:
            answer = 'end'
            print("Download ended before! " + str(gid))
            break

        sigma_now = nowTime()
        time.sleep(2.1)

    if  answer != 'end':
        print("Time is Up")
        answer = downloadStop(gid)
        i = 0
        while answer == 'None' and (i <= 9): #trying to stop download 10 times
            time.sleep(1)
            answer = downloadStop(gid)
            i = i + 1
        if answer == 'None':
            os.system("killall aria2c")

        download_info_file_list = readList(download_info_file) 
        add_link_dictionary = download_info_file_list[9]
        add_link_dictionary['end_hour'] = None
        add_link_dictionary['end_minute'] = None
        download_info_file_list[9] = add_link_dictionary
        download_info_file_list[1] = "stopped"
        writeList(download_info_file,download_info_file_list)
        
        
                





