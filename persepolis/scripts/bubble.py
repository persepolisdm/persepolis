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
#

from __future__ import annotations

import os
import platform
import subprocess
from typing import TYPE_CHECKING

from persepolis.constants import Os
from persepolis.gui import resources  # noqa: F401
from persepolis.scripts.play import playNotification

try:
    from PySide6.QtCore import QSettings
    from PySide6.QtGui import QIcon
except:
    from PyQt5.QtCore import QSettings
    from PyQt5.QtGui import QIcon

if TYPE_CHECKING:
    try:
        from PySide6.QtWidgets import QWidget
    except ImportError:
        from PyQt5.QtWidgets import QWidget

# platform
os_type = platform.system()


# notifySend use notify-send program in user's system for sending notifications
# and use playNotification function in play.py file for playing sound
# notifications
def notifySend(message1: str, message2: str, time: int, sound: str, parent: QWidget | None = None) -> None:
    if os_type == Os.LINUX:
        notifications_path = '/usr/share/sounds/freedesktop/stereo/'
    elif os_type in Os.BSD_FAMILY:
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
        parent.system_tray_icon.showMessage(
            message1, message2, QIcon.fromTheme('persepolis-tray', QIcon(':/persepolis-tray.svg')), 10000
        )

    elif os_type in Os.UNIX_LIKE:
        subprocess.Popen(
            [
                'notify-send',
                '--icon',
                'com.github.persepolisdm.persepolis',
                '--app-name',
                'Persepolis Download Manager',
                '--expire-time',
                time,
                message1,
                message2,
            ],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            shell=False,
        )

    else:
        parent.system_tray_icon.showMessage(
            message1, message2, QIcon.fromTheme('persepolis-tray', QIcon(':/persepolis-tray.svg')), 10000
        )
