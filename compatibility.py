#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import ast
#this script for compatibility between Version 2.0 and 2.1 of persepolis
home_address = os.path.expanduser("~")
config_folder = str(home_address) + "/.config/persepolis_download_manager"
download_info_folder = config_folder + "/download_info"
download_list_file = config_folder + "/download_list_file"
download_list_file_lines = []
if os.path.isdir(download_info_folder) == True :
    f = open(download_list_file)
    download_list_file_lines = f.readlines()
    f.close()

    for line in download_list_file_lines:
        gid = line.strip()
        download_info_file = download_info_folder + "/" + gid
        f_download_info_file = open(download_info_file) 
        download_info_file_lines = f_download_info_file.readlines()
        f_download_info_file.close()
        if len(download_info_file_lines) == 10 :
            list = []
            for i in range(10) :
                line_strip = download_info_file_lines[i].strip()
                if i == 9 :
                    line_strip = ast.literal_eval(line_strip)
                list.append(line_strip)
            dictionary =  {'list' : list }
            os.system('echo "' + str(dictionary) + '"  >  "' + str(download_info_file) + '"' )
            f_download_info_file = open (download_info_file , 'w')
            f_download_info_file.writelines(str(dictionary))
            f_download_info_file.close()
 

            

