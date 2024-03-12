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

from persepolis.scripts.play import playNotification
from persepolis.gui import resources
from persepolis.constants import OS
import subprocess
import platform
import os

try:
    from PySide6.QtCore import QSettings
    from PySide6.QtGui import QIcon
except:
    from PyQt5.QtCore import QSettings
    from PyQt5.QtGui import QIcon



# platform
os_type = platform.system()

if os_type == OS.DARWIN:
    from persepolis.scripts.mac_notification import notifyMac
    
# notifySend use notify-send program in user's system for sending notifications
# and use playNotification function in play.py file for playing sound
# notifications


def notifySend(message1, message2, time, sound, parent=None):

    if os_type == OS.LINUX:
        notifications_path = '/usr/share/sounds/freedesktop/stereo/'
    elif os_type in OS.BSD_FAMILY:
        notifications_path = '/usr/local/share/sounds/freedesktop/stereo/'
    else:
        notifications_path = ''

    if sound == 'ok':
        file = os.path.join(notifications_path, 'complete.oga')
        playNotification(str(file))

    elif sound == 'fail':
        file = os.path.join(notifications_path, 'dialog-error.oga')
        playNotification(str(file))

    elif sound == 'warning':
        file = os.path.join(notifications_path, 'bell.oga')
        playNotification(str(file))

    elif sound == 'critical':
        file = os.path.join(notifications_path, 'power-plug.oga')
        playNotification(str(file))

    elif sound == 'queue':
        file = os.path.join(notifications_path, 'dialog-information.oga')
        playNotification(str(file))

    # load settings
    persepolis_setting = QSettings('persepolis_download_manager', 'persepolis')

    enable_notification = persepolis_setting.value('settings/notification')

    time = str(time)
    message1 = str(message1)
    message2 = str(message2)

    # using Qt notification or Native system notification
    if enable_notification == 'QT notification':
        parent.system_tray_icon.showMessage(message1, message2, QIcon.fromTheme('persepolis-tray', QIcon(':/persepolis-tray.svg')), 10000)


    else:
        if os_type in OS.UNIX_LIKE:
            subprocess.Popen(['notify-send', '--icon', 'persepolis',
                              '--app-name', 'Persepolis Download Manager',
                              '--expire-time', time,
                              message1, message2],
                             stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stdin=subprocess.PIPE,
                             shell=False)

        elif os_type == OS.OSX:
            parent.system_tray_icon.showMessage(message1, message2, QIcon.fromTheme('persepolis-tray', QIcon(':/persepolis-tray.svg')), 10000)

        elif os_type == OS.WINDOWS:
            parent.system_tray_icon.showMessage(message1, message2, QIcon.fromTheme('persepolis-tray', QIcon(':/persepolis-tray.svg')), 10000)
