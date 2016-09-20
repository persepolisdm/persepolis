#!/usr/bin/python3
# -*- coding: utf-8 -*-

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
#perseolis_shutdown
perseolis_shutdown = '/tmp/persepolis/shutdown'
shutil.rmtree(perseolis_shutdown, ignore_errors=True, onerror=None)
#creating folders
folder_list = [ config_folder , download_info_folder ,persepolis_tmp , perseolis_shutdown ]
for folder in folder_list :
    if os.path.isdir(folder) == False :
        os.mkdir(folder)


#this section checks setting file existed or not !and if it is not existed , exists a default setting file
if os.path.isfile(setting_file) == False :
    download_path_temp = str(home_address) + '/.persepolis'
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

#this section  creates temporary download folder and download folder and download sub folders if they did not existed.
download_path_temp  = setting_dict ['download_path_temp']
download_path = setting_dict [ 'download_path']
folder_list = [download_path_temp , download_path]
for folder in [ 'Audios' , 'Videos', 'Others','Documents','Compressed' ]:
    folder_list.append(download_path + '/' + folder )

for folder in folder_list :
    if os.path.isdir(folder) == False :
        os.mkdir(folder)



