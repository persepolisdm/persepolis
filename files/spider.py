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

import os
import requests 
from newopen import Open , readList , writeList
from http.cookies import SimpleCookie
from requests.cookies import cookiejar_from_dict
from requests import Session
import platform

os_type = platform.system()



home_address = os.path.expanduser("~")

#config_folder
if os_type == 'Linux' or os_type == 'FreeBSD' :
    config_folder = os.path.join(str(home_address) , ".config/persepolis_download_manager")
elif os_type == 'Darwin':
    config_folder = os.path.join(str(home_address) , "Library/Application Support/persepolis_download_manager")
elif os_type == 'Windows' :
    config_folder = os.path.join(str(home_address) , 'AppData' , 'Local' , 'persepolis_download_manager')



download_info_folder = os.path.join(config_folder  , "download_info")
download_list_file =  os.path.join(config_folder , "download_list_file")
download_list_file_active =  os.path.join(config_folder , "download_list_file_active")

#for more informations about "requests" library , please see http://docs.python-requests.org/en/master/



#spider function finding name of file and file size from header
def spider(add_link_dictionary , gid):
    #getting user's download request from add_link_dictionary
    link = add_link_dictionary ['link']
    ip = add_link_dictionary['ip']
    port = add_link_dictionary['port']
    proxy_user = add_link_dictionary['proxy_user']
    proxy_passwd = add_link_dictionary['proxy_passwd']
    download_user = add_link_dictionary['download_user']
    download_passwd = add_link_dictionary['download_passwd']
    header = add_link_dictionary['header']
    out = add_link_dictionary['out']
    user_agent = add_link_dictionary['user-agent']
    raw_cookies = add_link_dictionary['load-cookies']
    referer = add_link_dictionary['referer']

    if out == '***':
        out = None
    
    requests_session = requests.Session() #defining a requests Session
    if ip :
        ip_port = 'http://' + str(ip) + ":" + str(port)
        if proxy_user :
            ip_port = 'http://' + proxy_user + ':' + proxy_passwd + '@' + ip_port
        requests_session.proxies = {'http' : ip_port} #setting proxy to the session

    if download_user :
        requests_session.auth(download_user , download_passwd) #setting download user pass to the session

    if raw_cookies != None : #setting cookies
        cookie = SimpleCookie()
        cookie.load(raw_cookies)

        cookies = {key: morsel.value for key, morsel in cookie.items()}
        requests_session.cookies = cookiejar_from_dict(cookies)

    if referer != None :
        requests_session.headers.update({'referer': referer }) #setting referer to the session

    if user_agent != None :
        requests_session.headers.update({'user-agent':user_agent }) #setting user_agent to the session
        
    #finding headers
    response = requests_session.head(link)   
    header = response.headers
    filename = '***'
    filesize = '***'
    if 'Content-Disposition' in header.keys() : #checking if filename is available
        content_disposition = header['Content-Disposition']
        if content_disposition.find('filename') != -1 :
            filename_splited = content_disposition.split('filename=')
            filename_splited = filename_splited[-1]
            filename = filename_splited[1:-1] #getting file name in desired format 
    
    
    if filename == '***' :
        filename = link.split('/')[-1]
    if out != None :
        filename = out
       
    if 'Content-Length' in header.keys(): #checking if file_size is available
        file_size = int (header['Content-Length'])
        if int(file_size/1073741824) != 0 : #converting file_size to KB or MB or GB
            file_size = file_size/1073741824
            size_str = str(round(file_size , 2)) + " GB"
        elif int(file_size/1048576) != 0:
            size_str = str(int(file_size/1048576)) + " MB"
        elif int(file_size/1024) != 0:
            size_str = str(int(file_size/1024)) + " KB"
        else:
            size_str = str(file_size)
        filesize = size_str
 
    download_info_file =os.path.join( download_info_folder , gid)
    download_info_file_list = readList(download_info_file)
    

    download_info = [filename , None , filesize , None ,  None , None , None ,None , None , None , None , None  , None ]

   
    for i in range(13):
        if download_info[i] != None:
            download_info_file_list[i] = download_info[i]
 
        
    writeList(download_info_file , download_info_file_list)

#this function finds and returns name of the file
def queueSpider(add_link_dictionary):
    #getting user's download request from add_link_dictionary
    for i in ['link' , 'header' , 'out' , 'user-agent' , 'load-cookies' , 'referer' ]:
        if not (i in add_link_dictionary):
            add_link_dictionary[i] = None

    link = add_link_dictionary ['link']
    header = add_link_dictionary['header']
    user_agent = add_link_dictionary['user-agent']
    raw_cookies = add_link_dictionary['load-cookies']
    referer = add_link_dictionary['referer']
    
    requests_session = requests.Session() #defining a requests Session

    if raw_cookies != None : #setting cookies
        cookie = SimpleCookie()
        cookie.load(raw_cookies)

        cookies = {key: morsel.value for key, morsel in cookie.items()}
        requests_session.cookies = cookiejar_from_dict(cookies)

    if referer != None :
        requests_session.headers.update({'referer': referer }) #setting referer to the session

    if user_agent != None :
        requests_session.headers.update({'user-agent':user_agent }) #setting user_agent to the session
        
    #finding headers
    response = requests_session.head(link)   
    header = response.headers
    filename = '***'
    if 'Content-Disposition' in header.keys() : #checking if filename is available
        content_disposition = header['Content-Disposition']
        if content_disposition.find('filename') != -1 :
            filename_splited = content_disposition.split('filename=')
            filename_splited = filename_splited[-1]
            filename = filename_splited[1:-1] #getting file name in desired format 
    
    
    if filename == '***' :
        filename = link.split('/')[-1]
 
    return filename
