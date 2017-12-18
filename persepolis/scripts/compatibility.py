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
import os
import ast
from persepolis.scripts.newopen import readList
from persepolis.scripts.data_base import PersepolisDB 
import platform
from persepolis.scripts.osCommands import remove, removeDir

home_address = os.path.expanduser("~")

# finding os platform
os_type = platform.system()


# config_folder
if os_type == 'Linux' or os_type == 'FreeBSD' or os_type == 'OpenBSD':
    config_folder = os.path.join(
        str(home_address), ".config/persepolis_download_manager")
elif os_type == 'Darwin':
    config_folder = os.path.join(
        str(home_address), "Library/Application Support/persepolis_download_manager")
elif os_type == 'Windows':
    config_folder = os.path.join(
        str(home_address), 'AppData', 'Local', 'persepolis_download_manager')


download_info_folder = os.path.join(config_folder, "download_info")


# download_list_file contains GID of all downloads
download_list_file = os.path.join(config_folder, "download_list_file")

# download_list_file_active for active downloads
download_list_file_active = os.path.join(
    config_folder, "download_list_file_active")

# queues_list contains queues name
queues_list_file = os.path.join(config_folder, 'queues_list')

# category_folder contains some file , and every files named with queues .
# every file contains gid of downloads for that queue
category_folder = os.path.join(config_folder, 'category_folder')

# queue_info_folder is contains queues information(start time,end
# time,limit speed , ...)
queue_info_folder = os.path.join(config_folder, "queue_info")

# single_downloads_list_file contains gid of non categorised downloads
single_downloads_list_file = os.path.join(category_folder, "Single Downloads")






# this script for compatibility between Version 2 and 3 

def compatibility():
    if os.path.isfile(queues_list_file):
        persepolis_db = PersepolisDB()

        # add categories to category_db_table in data_base
        f = open(queues_list_file)
        queues_list = f.readlines()
        f.close()

        # remove queues_list_file
        remove(queues_list_file)
    else:
        return

    category_list = ['All Downloads', 'Single Downloads']
    for line in queues_list:
        queue_name = line.strip()
        category_list.append(queue_name)


    for category in category_list:
        gid_list = []

        if category == 'All Downloads':
            category_info_file = download_list_file 
        else:
            category_info_file = os.path.join(category_folder, category)

        f = open(category_info_file)
        category_info_file_list = f.readlines()
        f.close()

        for item in category_info_file_list:
            gid = item.strip()
            gid_list.append(gid)
        
        category_dict = {'category': category,
                    'start_time_enable': 'no',
                    'start_time': '0:0',
                    'end_time_enable': 'no',
                    'end_time': '0:0',
                    'reverse': 'no',
                    'limit_enable': 'no',
                    'limit_value': '0K',
                    'after_download': 'no',
                    'gid_list': str(gid_list) 
                    }
            

        # add category to data_base
        if category == 'All Downloads' or category == 'Single Downloads':
            persepolis_db.updateCategoryTable([category_dict])
        else:
            persepolis_db.insertInCategoryTable(category_dict)

    # add items to download_db_table in data base
    f_download_list_file = open(download_list_file)
    download_list_file_lines = f_download_list_file.readlines()
    f_download_list_file.close()

    for line in download_list_file_lines:
        gid = line.strip()
        download_info_file = os.path.join(download_info_folder, gid)

        download_info_file_list = readList(download_info_file)
        add_link_dictionary = download_info_file_list[9]

        dict = {'file_name': download_info_file_list[0],
                'status': download_info_file_list[1],
                'size': download_info_file_list[2],
                'downloaded_size': download_info_file_list[3],
                'percent': download_info_file_list[4],
                'connections': download_info_file_list[5],
                'rate': download_info_file_list[6],
                'estimate_time_left': download_info_file_list[7],
                'gid': download_info_file_list[8],
                'link': add_link_dictionary['link'],
                'first_try_date': download_info_file_list[10], 
                'last_try_date': download_info_file_list[11],
                'category': download_info_file_list[12]}

        add_link_dictionary['gid'] = download_info_file_list[8]

        if 'user-agent' in add_link_dictionary.keys():
            add_link_dictionary['user_agent'] = add_link_dictionary.pop('user-agent')


        if 'load-cookies' in add_link_dictionary.keys():
            add_link_dictionary['load_cookies'] = add_link_dictionary.pop('load-cookies')

        add_link_dictionary['limit_value'] = 0



        keys_list = ['gid',
                    'out',
                    'start_time',
                    'end_time',
                    'link',
                    'ip',
                    'port',
                    'proxy_user',
                    'proxy_passwd',
                    'download_user',
                    'download_passwd',
                    'connections',
                    'limit_value',
                    'download_path',
                    'referer',
                    'load_cookies',
                    'user_agent',
                    'header',
                    'after_download']

        for key in keys_list:  
                # if a key is missed in dict, 
                # then add this key to the dict and assign None value for the key. 
            if key not in add_link_dictionary.keys():
                add_link_dictionary[key] = None 


        # write information in data_base
        persepolis_db.insertInDownloadTable([dict])
        persepolis_db.insertInAddLinkTable([add_link_dictionary])

    # close connections
    persepolis_db.closeConnections()

    # remove unwanted files and folders
    for file in [download_list_file, download_list_file_active]:
        remove(file)

    for folder in [category_folder, queue_info_folder]:
        removeDir(folder)


 
