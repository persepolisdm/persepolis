
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

import os
import platform
import subprocess

from PyQt5.QtCore import QSettings

from persepolis.constants import OS
from persepolis.scripts import logger

os_type = platform.system()


def playNotification(file):
    # getting user setting from persepolis_setting
    persepolis_setting = QSettings('persepolis_download_manager', 'persepolis')

    # enbling or disabling notification sound in persepolis_setting
    enable_notification = str(persepolis_setting.value('settings/sound'))

    # volume of notification in persepolis_setting(an integer between 0 to 100)
    volume_percent = int(persepolis_setting.value('settings/sound-volume'))

# Paplay volume value must be between 0 (silent) and 65536 (100% volume)
    volume = int((65536 * volume_percent)/100)

    if enable_notification == 'yes':
        if os_type == OS.LINUX or os_type == OS.FREE_BSD or os_type == OS.OPEN_BSD:
            answer = os.system("paplay --volume='" + str(volume) + "' '" + file + "' &")
            if answer != 0:
                logger.sendToLog(
                    "paplay not installed!Install it for playing sound notification", "WARNING")


        elif os_type == OS.DARWIN:
            os.system("osascript -e 'set volume alert volume " +
                      str(volume) + "'")
            os.system("osascript -e 'beep 3' &")

        elif os_type == OS.WINDOWS:
            CREATE_NO_WINDOW = 0x08000000
            subprocess.Popen(['rundll32', 'user32.dll,MessageBeep'],
                             shell=False, creationflags=CREATE_NO_WINDOW)
