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

import os
import platform

from PyQt5.QtCore import QSettings

from persepolis.constants import OS
from persepolis.scripts.play import playNotification

# platform
os_type = platform.system()

if os_type == OS.DARWIN:
    from persepolis.scripts.mac_notification import notifyMac

elif os_type == OS.WINDOWS:
    from persepolis.scripts.windows_notification import Windows_Notification

# notifySend use notify-send program in user's system for sending notifications
# and use playNotification function in play.py file for playing sound
# notifications
def notifySend(message1, message2, time, sound, parent=None):
    if os_type == OS.LINUX:
        notifications_path = '/usr/share/sounds/freedesktop/stereo/'
    elif os_type == OS.FREE_BSD or os_type == OS.OPEN_BSD:
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
        parent.system_tray_icon.showMessage(message1, message2, 0, 10000)
    else:
        if os_type == OS.LINUX or os_type == OS.FREE_BSD or os_type == OS.OPEN_BSD:
            os.system("notify-send --icon='persepolis' --app-name='Persepolis Download Manager' --expire-time='" +
                      time + "' '" + message1 + "' \ '" + message2 + "' ")

        elif os_type == OS.DARWIN:
            notifyMac("Persepolis Download Manager", message1, message2)

        elif os_type == OS.WINDOWS:
            message = Windows_Notification(parent=parent, time=time, text1=message1, text2=message2, persepolis_setting=persepolis_setting)
            message.show()
