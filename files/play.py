#!/usr/bin/python
import os
from newopen import Open
import ast

home_address = os.path.expanduser("~")
config_folder = str(home_address) + "/.config/persepolis_download_manager"


#setting
setting_file = config_folder + '/setting'

def playNotification(file):
#getting user setting from setting file
#setting_dict['sound'] >>> enable or disable sound
#setting_dict['sound-volume'] >>>Specify volume of sound . between 0 to 100
    f = Open(setting_file)
    setting_file_lines = f.readlines()
    f.close()
    setting_dict_str = str(setting_file_lines[0].strip())
    setting_dict = ast.literal_eval(setting_dict_str) 

    enable_notification = str(setting_dict['sound'])
    volume_percent = int(setting_dict['sound-volume'])
#Paplay volume value must be between 0 (silent) and 65536 (100% volume)
    volume = int((65536 * volume_percent)/100)

    if enable_notification == 'yes':
        os.system("paplay --volume='"+ str(volume) + "' '" + file + "' &")

