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


# initialization
home_address = os.path.expanduser("~")

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
persepolis_tmp = '/tmp/persepolis'

#user's preferences will saved in setting file
setting_file = config_folder + '/setting'

#when user is resizing a window , size of window is saving in windows_size file .
windows_size = config_folder + '/windows_size'

#perseolis_shutdown
perseolis_shutdown = '/tmp/persepolis/shutdown'
shutil.rmtree(perseolis_shutdown, ignore_errors=True, onerror=None)

#creating folders
for folder in  [ config_folder , download_info_folder ,persepolis_tmp , perseolis_shutdown , category_folder ]:
    osCommands.makeDirs(folder)

#creating files
for file in [queues_list , download_list_file , download_list_file_active , single_downloads_list_file ]:
    osCommands.touch(file)

osCommands.touch(setting_file)
f = Open(setting_file)
setting_file_lines = f.readlines()
f.close()
try :
    setting_dict_str = str(setting_file_lines[0].strip())
    setting_dict = ast.literal_eval(setting_dict_str) 
except :
    setting_dict = [] 

#this section is checking setting file existed or not !and if it is not existed , exists a default setting file
if len(setting_dict) != 19:
    download_path_temp = str(home_address) + '/.persepolis'

    download_path = str(home_address) + '/Downloads/Persepolis'

    default_setting = {'show_menubar' : 'no' , 'show_sidepanel' : 'yes' , 'rpc-port' : 6801 , 'notification' : 'Native notification' , 'after-dialog' : 'yes' , 'tray-icon' : 'yes', 'max-tries' : 5 , 'retry-wait': 0 , 'timeout' : 60 , 'connections' : 16 , 'download_path_temp' : download_path_temp , 'download_path':download_path , 'sound' : 'yes' , 'sound-volume':90 , 'style':'Fusion' , 'color-scheme' : 'Persepolis Dark Red' , 'icons':'Archdroid-Red','font' : 'Ubuntu' , 'font-size' : 9  }
    f = Open(setting_file , 'w')
    f.writelines(str(default_setting))
    f.close()

    f = Open(setting_file)
    setting_file_lines = f.readlines()
    f.close()
    setting_dict_str = str(setting_file_lines[0].strip())
    setting_dict = ast.literal_eval(setting_dict_str) 

osCommands.touch(windows_size)
f = Open(windows_size)
windows_size_lines = f.readlines()
f.close()
try:
    size_dict_str = str(windows_size_lines[0].strip())
    size_dict = ast.literal_eval(size_dict_str) 
except:
    size_dict = []


#this section is checking windows_size existed or not!and if it is not existed , then exists the file with default value .
if len(size_dict) != 7:
    default_size = { 'TextQueue_Ui' : [700 , 500] , 'MainWindow_Ui' : [900,500] , 'AddLinkWindow_Ui' : [520 , 565] , 'Setting_Ui' : [578 , 465] , 'ProgressWindow_Ui' : [595,284] , 'AboutWindow' : [363 , 300] , 'AfterDownloadWindow_Ui' : [570 , 290] }
    f = Open(windows_size, 'w')
    f.writelines(str(default_size))
    f.close()


#this section  creates temporary download folder and download folder and download sub folders if they did not existed.
download_path_temp  = setting_dict ['download_path_temp']
download_path = setting_dict [ 'download_path']
folder_list = [download_path_temp]
for folder in [ 'Audios' , 'Videos', 'Others','Documents','Compressed' ]:
    folder_list.append(download_path + '/' + folder )

for folder in folder_list :
    osCommands.makeDirs(folder)

#creating shutdown script in /tmp/persepolis
os_type = platform.system()
if os_type == 'Darwin':
    shutdown_script_list = [ 'passwd="$1" ', 'gid="$2"', 'shutdown_notification_file="/tmp/persepolis/shutdown/$gid"', 'echo "wait" > $shutdown_notification_file', 'shutdown_notification="wait"', 'while [ "$shutdown_notification" == "wait" ];do','    sleep 1' ,'    shutdown_notification=`cat "$shutdown_notification_file"`','done','rm "$shutdown_notification_file"','if [ "$shutdown_notification" == "shutdown" ];then','    sleep 20','    echo "shutdown"' ,'    echo "$passwd" |sudo -S shutdown -h now','else','    exit','fi']
elif os_type == 'Linux':
    shutdown_script_list = [ 'passwd="$1" ', 'gid="$2"', 'shutdown_notification_file="/tmp/persepolis/shutdown/$gid"', 'echo "wait" > $shutdown_notification_file', 'shutdown_notification="wait"', 'while [ "$shutdown_notification" == "wait" ];do','    sleep 1' ,'    shutdown_notification=`cat "$shutdown_notification_file"`','done','rm "$shutdown_notification_file"','if [ "$shutdown_notification" == "shutdown" ];then','    sleep 20','    echo "shutdown"' , '	poweroff' , '	if [ "$?" != "0" ];then' , '    	echo "$passwd" |sudo -S poweroff' ,'	fi','    echo "$passwd" |sudo -S poweroff','else','    exit','fi']

shutdown_script_path = '/tmp/persepolis/shutdown_script_root'
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
    

