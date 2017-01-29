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

import os , ast
import platform
from play import playNotification
from newopen import Open
from PyQt5.QtCore import QSettings

home_address = os.path.expanduser("~")

#platform
os_type = platform.system()

#config_folder
if os_type == 'Linux' or os_type == 'FreeBSD' :
    config_folder = os.path.join(str(home_address) , ".config/persepolis_download_manager")
elif os_type == 'Darwin':
    config_folder = os.path.join(str(home_address) , "Library/Application Support/persepolis_download_manager")
elif os_type == 'Windows' :
    config_folder = os.path.join(str(home_address) , 'AppData','Local','persepolis_download_manager')



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
    elif sound == 'queue':
        playNotification('notifications/queue.ogg')

    #load settings
    persepolis_setting = QSettings('persepolis_download_manager' , 'persepolis')

    enable_notification = persepolis_setting.value('settings/notification')

    time = str(time)
    message1 = str(message1)
    message2 = str(message2)

#using Qt notification or Native system notification
    if enable_notification == 'QT notification':
        systemtray.showMessage(message1 , message2 , 0, 10000)
    else:
        if os_type == 'Linux' or os_type == 'FreeBSD' :
            os.system("notify-send --icon='persepolis' --app-name='Persepolis Download Manager' --expire-time='" + time + "' '" +  message1 +  "' \ '" + message2 +  "' "  )
        elif os_type == 'Darwin':
            from mac_notification import notifyMac

            notifyMac("Persepolis Download Manager", message1, message2)

        elif os_type == 'Windows':
            systemtray.showMessage(message1 , message2 , 0, 10000)
           
