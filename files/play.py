
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

import os, logger
from newopen import Open
import ast
import platform
from PyQt5.QtCore import QSettings
import subprocess

os_type = platform.system()

home_address = os.path.expanduser("~")
#config_folder
if os_type == 'Linux' or os_type == 'FreeBSD' :
    config_folder = os.path.join(str(home_address) , ".config/persepolis_download_manager")
elif os_type == 'Darwin':
    config_folder = os.path.join(str(home_address) , "Library/Application Support/persepolis_download_manager")
elif os_type == 'Windows' :
    config_folder = os.path.join(str(home_address) , 'AppData' , 'Local' , 'persepolis_download_manager')



def playNotification(file):
#getting user setting from persepolis_setting
    persepolis_setting = QSettings('persepolis_download_manager' , 'persepolis')

    #enbling or disabling notification sound in persepolis_setting
    enable_notification = str(persepolis_setting.value('settings/sound'))

    #volume of notification in persepolis_setting(an integer between 0 to 100)
    volume_percent = int(persepolis_setting.value('settings/sound-volume'))

#Paplay volume value must be between 0 (silent) and 65536 (100% volume)
    volume = int((65536 * volume_percent)/100)

    if enable_notification == 'yes':
        if os_type == 'Linux':
            os.system("paplay --volume='"+ str(volume) + "' '" + file + "' &")

        elif os_type == 'Darwin' :
            os.system("osascript -e 'set volume alert volume " + str(volume) + "'" )
            os.system("osascript -e 'beep 3' &")

        elif os_type == 'Windows':
            CREATE_NO_WINDOW = 0x08000000
            subprocess.Popen(['rundll32' , 'user32.dll,MessageBeep'] , shell = False , creationflags = CREATE_NO_WINDOW )


        elif os_type == 'FreeBSD':
            print('sorry!no notification sound available for now in FreeBSD')
            logger.sendToLog("Sorry, no notification sound available for now in FreeBSD", "WARNING")


