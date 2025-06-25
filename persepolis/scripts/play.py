
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
    from PySide6.QtCore import QUrl, QSettings
    from PySide6.QtMultimedia import QSoundEffect
except:
    from PyQt5.QtCore import QUrl, QSettings
    from PyQt5.QtMultimedia import QSoundEffect

from persepolis.scripts import logger
from persepolis.constants import OS
import subprocess
import platform

os_type = platform.system()

# It's weird! but effect must be global variable
# See this issue:
# https://stackoverflow.com/questions/64794912/
global effect


def playNotification(file):
    # getting user setting from persepolis_setting
    persepolis_setting = QSettings('persepolis_download_manager', 'persepolis')

    # enabling or disabling notification sound in persepolis_setting
    enable_notification = str(persepolis_setting.value('settings/sound'))

    # volume of notification in persepolis_setting(an integer between 0 to 100)
    volume_percent = int(persepolis_setting.value('settings/sound-volume'))

    global effect
    if enable_notification == 'yes':
        if os_type in OS.UNIX_LIKE:
            try:
                effect = QSoundEffect()
                effect.setSource(QUrl.fromLocalFile(file))
                effect.setLoopCount(1)
                effect.setVolume(volume_percent / 100)
                effect.play()
            except Exception as error:
                logger.sendToLog(
                    str(error), "ERROR")

        elif os_type == OS.OSX:

            try:
                effect = QSoundEffect()
                effect.setSource(QUrl.fromLocalFile(file))
                effect.setLoopCount(1)
                effect.setVolume(volume_percent / 100)
                effect.play()
            except Exception as error:
                logger.sendToLog(
                    str(error), "ERROR")
