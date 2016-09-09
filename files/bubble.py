#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os , ast
from play import playNotification
from newopen import Open

home_address = os.path.expanduser("~")
config_folder = str(home_address) + "/.config/persepolis_download_manager"

#setting
setting_file = config_folder + '/setting'


#notifySend use notify-send program in user's system for sending notifications
#and use playNotification function in play.py file for playing sound notifications
def notifySend(message1,message2,time,sound ,systemtray=None ):
    if sound == 'ok':
        playNotification('notifications/ok.ogg')
    elif sound == 'fail':
        playNotification('notifications/fail.ogg')
    elif sound == 'warning':
        playNotification('notifications/you.ogg')
    elif sound == 'critical':
        playNotification('notifications/connection.ogg')

    f = Open(setting_file)
    setting_file_lines = f.readlines()
    f.close()
    setting_dict_str = str(setting_file_lines[0].strip())
    setting_dict = ast.literal_eval(setting_dict_str) 

    enable_notification = str(setting_dict['notification'])
 
    time = str(time)
    message1 = str(message1)
    message2 = str(message2)

#using Qt notification or Native system notification
    if enable_notification == 'QT notification':
        systemtray.showMessage(message1 , message2 , 1, 10000)
    else:
        os.system("notify-send --icon='persepolis' --app-name='Persepolis Download Manager' --expire-time='" + time + "' '" +  message1 +  "' \ '" + message2 +  "' "  )

