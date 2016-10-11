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


import  os , shutil , ast 
from newopen import Open



# initialization
home_address = os.path.expanduser("~")

# ~/.config/persepolis_download_manager/ is download manager config folder
config_folder = str(home_address) + "/.config/persepolis_download_manager"

#download information (Percentage , Estimate time left , size of file , ... ) saved in download_info folder. 
#Persepolis creates one file for every download . 
#Persepolis uses download's GID for the name of the file
download_info_folder = config_folder + "/download_info"
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
folder_list = [ config_folder , download_info_folder ,persepolis_tmp , perseolis_shutdown ]
for folder in folder_list :
    if os.path.isdir(folder) == False :
        os.mkdir(folder)


#this section is checking setting file existed or not !and if it is not existed , exists a default setting file
if os.path.isfile(setting_file) == False :
    download_path_temp = str(home_address) + '/.persepolis'
    user_download_folder = str(home_address) + '/Downloads'
    os.mkdir(user_download_folder)
    download_path = str(home_address) + '/Downloads/Persepolis'
    default_setting = {'rpc-port' : 6801 , 'notification' : 'Native notification' , 'after-dialog' : 'yes' , 'tray-icon' : 'yes', 'max-tries' : 5 , 'retry-wait': 0 , 'timeout' : 60 , 'connections' : 16 , 'download_path_temp' : download_path_temp , 'download_path':download_path , 'sound' : 'yes' , 'sound-volume':90 , 'style':'Fusion' , 'color-scheme' : 'Persepolis Dark Red' , 'icons':'Archdroid-Red','font' : 'Ubuntu' , 'font-size' : 9  }
    f = Open(setting_file , 'w')
    f.writelines(str(default_setting))
    f.close()

f = Open(setting_file)
setting_file_lines = f.readlines()
f.close()
setting_dict_str = str(setting_file_lines[0].strip())
setting_dict = ast.literal_eval(setting_dict_str) 

#this section is checking windows_size existed or not!and if it is not existed , then exists the file with default value .
if os.path.isfile(windows_size) == False:
    default_size = {'MainWindow_Ui' : [600,400] , 'AddLinkWindow_Ui' : [520 , 465] , 'Setting_Ui' : [578 , 465] , 'ProgressWindow_Ui' : [595,284] , 'AboutWindow' : [363 , 300] , 'AfterDownloadWindow_Ui' : [570 , 290] }
    f = Open(windows_size, 'w')
    f.writelines(str(default_size))
    f.close()


#this section  creates temporary download folder and download folder and download sub folders if they did not existed.
download_path_temp  = setting_dict ['download_path_temp']
download_path = setting_dict [ 'download_path']
folder_list = [download_path_temp , download_path]
for folder in [ 'Audios' , 'Videos', 'Others','Documents','Compressed' ]:
    folder_list.append(download_path + '/' + folder )

for folder in folder_list :
    if os.path.isdir(folder) == False :
        os.mkdir(folder)



