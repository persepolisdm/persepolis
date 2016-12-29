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


#THIS FILE CONTAINING SOME VARIABLES , ... THAT USING FOR INITIALIZING PERSEPOLIS
#This py file imported in persepolis-download-manager file

#The GID (or gid) is a key to manage each download. Each download will be assigned a unique GID.
#The GID is stored as 64-bit binary value in aria2. For RPC access, 
#it is represented as a hex string of 16 characters (e.g., 2089b05ecca3d829). 
#Normally, aria2 generates this GID for each download, but the user can specify GIDs manually

import  os , shutil , ast 
from newopen import Open
import osCommands
import platform
from compatibility import compatibility
import glob
import PyQt5
from PyQt5.QtCore import QSettings

# initialization
home_address = os.path.expanduser("~")
user_name_split = home_address.split('/')
user_name = user_name_split[2]


# ~/.config/persepolis_download_manager/ is download manager config folder
config_folder = str(home_address) + "/.config/persepolis_download_manager"

#download information (Percentage , Estimate time left , size of file , ... ) saved in download_info folder. 
#Persepolis creates one file for every download . 
#Persepolis uses download's GID for the name of the file
download_info_folder = config_folder + "/download_info"

#category_folder contains some file , and every files named with categories . every file contains gid of downloads for that category
category_folder = config_folder + '/category_folder'


#queue initialization files
#queues_list contains queues name
queues_list = config_folder + '/queues_list' 

#download_list_file contains GID of all downloads
download_list_file = config_folder + "/download_list_file"

#download_list_file_active for active downloads
download_list_file_active = config_folder + "/download_list_file_active"

#single_downloads_list_file contains gid of non categorised downloads
single_downloads_list_file = category_folder + "/" + "Single Downloads"

#persepolis tmp folder in /tmp
persepolis_tmp = '/tmp/persepolis_' + user_name

#lock files perventing to access a file simultaneously

#removing lock files in starting persepolis
pattern_folder_list = [config_folder , download_info_folder , category_folder]

for folder in pattern_folder_list:
    pattern = str(folder) + '/*.lock'
    for file in glob.glob(pattern):
        osCommands.remove(file)


#perseolis_shutdown
perseolis_shutdown = persepolis_tmp + '/shutdown'
shutil.rmtree(perseolis_shutdown, ignore_errors=True, onerror=None)

#creating folders
for folder in  [ config_folder , download_info_folder ,persepolis_tmp , perseolis_shutdown , category_folder ]:
    osCommands.makeDirs(folder)

#creating files
for file in [queues_list , download_list_file , download_list_file_active , single_downloads_list_file ]:
    osCommands.touch(file)


#import persepolis_setting
#persepolis is using QSettings for saving windows size and windows position and program settings
persepolis_setting = QSettings('persepolis_download_manager' , 'persepolis')

persepolis_setting.beginGroup('settings')

download_path_temp = str(home_address) + '/.persepolis'

download_path = str(home_address) + '/Downloads/Persepolis'


default_setting_dict = {'show-menubar' : 'no' , 'show-sidepanel' : 'yes' , 'rpc-port' : 6801 , 'notification' : 'Native notification' , 'after-dialog' : 'yes' , 'tray-icon' : 'yes', 'max-tries' : 5 , 'retry-wait': 0 , 'timeout' : 60 , 'connections' : 16 , 'download_path_temp' : download_path_temp , 'download_path':download_path , 'sound' : 'yes' , 'sound-volume':90 , 'style':'Fusion' , 'color-scheme' : 'Persepolis Dark Red' , 'icons':'Archdroid-Red','font' : 'Ubuntu' , 'font-size' : 9  }

#this loop is checking values in persepolis_setting . if value is not valid then value replaced by default_setting_dict value
for key in default_setting_dict.keys():

    setting_value = persepolis_setting.value(key, default_setting_dict[key] )
    persepolis_setting.setValue(key , setting_value )

persepolis_setting.sync()

#this section  creates temporary download folder and download folder and download sub folders if they did not existed.
download_path_temp  = persepolis_setting.value('download_path_temp')
download_path = persepolis_setting.value('download_path')

persepolis_setting.endGroup()

folder_list = [download_path_temp]
for folder in [ 'Audios' , 'Videos', 'Others','Documents','Compressed' ]:
    folder_list.append(download_path + '/' + folder )

for folder in folder_list :
    osCommands.makeDirs(folder)

#creating shutdown script in /tmp/persepolis
os_type = platform.system()
if os_type == 'Darwin':
    shutdown_script_list = [ 'passwd="$1" ', 'gid="$2"', 'shutdown_notification_file="' + perseolis_shutdown +  '/$gid"', 'echo "wait" > $shutdown_notification_file', 'shutdown_notification="wait"', 'while [ "$shutdown_notification" == "wait" ];do','    sleep 1' ,'    shutdown_notification=`cat "$shutdown_notification_file"`','done','rm "$shutdown_notification_file"','if [ "$shutdown_notification" == "shutdown" ];then','    sleep 20','    echo "shutdown"' ,'    echo "$passwd" |sudo -S shutdown -h now','else','    exit','fi']
elif os_type == 'Linux':
    shutdown_script_list = [ 'passwd="$1" ', 'gid="$2"', 'shutdown_notification_file="' + perseolis_shutdown +  '/$gid"', 'echo "wait" > $shutdown_notification_file', 'shutdown_notification="wait"', 'while [ "$shutdown_notification" == "wait" ];do','    sleep 1' ,'    shutdown_notification=`cat "$shutdown_notification_file"`','done','rm "$shutdown_notification_file"','if [ "$shutdown_notification" == "shutdown" ];then','    sleep 20','    echo "shutdown"' , '	poweroff' , '	if [ "$?" != "0" ];then' , '    	echo "$passwd" |sudo -S poweroff' ,'	fi','    echo "$passwd" |sudo -S poweroff','else','    exit','fi']

shutdown_script_path = persepolis_tmp + '/shutdown_script_root'
f = Open(shutdown_script_path , 'w')
for i in shutdown_script_list :
    f.writelines( i + '\n' )
f.close()

#compatibility
version_file = config_folder + '/' + 'version'
osCommands.touch(version_file)
f = Open(version_file)
version_file_line = f.readline()
f.close()

persepolis_version = version_file_line.strip()

if persepolis_version != '2.3 Alpha':
    compatibility()
    persepolis_version = '2.3 Alpha'
    f = Open(version_file , 'w')
    f.writelines(persepolis_version)
    f.close()
    

