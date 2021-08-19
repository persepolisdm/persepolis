
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

try:
    from PySide6.QtCore import QSettings
except:
    from PyQt5.QtCore import QSettings

from persepolis.scripts import logger
from persepolis.constants import OS
import subprocess
import platform

os_type = platform.system()


def playNotification(file):
    # getting user setting from persepolis_setting
    persepolis_setting = QSettings('persepolis_download_manager', 'persepolis')

    # enabling or disabling notification sound in persepolis_setting
    enable_notification = str(persepolis_setting.value('settings/sound'))

    # volume of notification in persepolis_setting(an integer between 0 to 100)
    volume_percent = int(persepolis_setting.value('settings/sound-volume'))

# Paplay volume value must be between 0 (silent) and 65536 (100% volume)
    volume = int((65536 * volume_percent)/100)

    if enable_notification == 'yes':
        if os_type in OS.UNIX_LIKE:

            pipe = subprocess.Popen(['paplay', '--volume=' + str(volume),
                                     str(file)],
                                    stderr=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stdin=subprocess.PIPE,
                                    shell=False)

            answer = pipe.wait()

            if answer != 0:
                logger.sendToLog(
                    "paplay not installed!Install it for playing sound notification", "WARNING")

        elif os_type == OS.OSX:

            pipe = subprocess.Popen(['osascript', '-e',
                                     'set', 'volume', 'alert',
                                     'volume', str(volume)],
                                    stderr=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stdin=subprocess.PIPE,
                                    shell=False)

            pipe = subprocess.Popen(['osascript', '-e',
                                     'beep', '3'],
                                    stderr=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stdin=subprocess.PIPE,
                                    shell=False)

        elif os_type == OS.WINDOWS:

            CREATE_NO_WINDOW = 0x08000000
            subprocess.Popen(['rundll32', 'user32.dll,MessageBeep'],
                             stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stdin=subprocess.PIPE,
                             shell=False,
                             creationflags=CREATE_NO_WINDOW)
