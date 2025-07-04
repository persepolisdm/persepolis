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
from persepolis.scripts.osCommands import makeDirs
from persepolis.gui import resources
from persepolis.constants import OS
import platform
import os
from persepolis.scripts import logger
from persepolis.scripts.download_link import DownloadSingleLink
try:
    from PySide6.QtCore import QSettings
    from PySide6.QtGui import QIcon
except:
    from PyQt5.QtCore import QSettings
    from PyQt5.QtGui import QIcon


# platform
os_type = platform.system()

global dasbus_is_installed
if os_type in OS.LINUX:
    try:
        from dasbus.connection import SessionMessageBus
        dasbus_is_installed = True
    except:
        dasbus_is_installed = False
        logger.sendToLog('python3-dasbus is not installed', 'ERROR')

# notifySend use notify-send program in user's system for sending notifications
# and use playNotification function in play.py file for playing sound
# notifications

# user home address
home_address = os.path.expanduser("~")


# When Persepolis is running on Linux, BSD, and MacOSX operating systems,
# the program will check for the presence of notification sound files,
# and if there are no files, it will download them from GitHub.
# The Windows operating system uses its own notification sounds,
# so there is no need for notification sound files in Windows.
def checkNotificationSounds():
    if os_type in OS.UNIX_LIKE:
        # for linux and bsd
        # ~/.local/share/persepolis_download_manager/sounds
        notification_directory = os.path.join(home_address, '.local/share/persepolis_download_manager/sounds')
    elif os_type in OS.OSX:
        # for mac
        # ~/Library/Application Support/<YourAppName>/sounds/
        notification_directory = os.path.join(home_address, 'Library/Application Support/persepolis_download_manager/sounds/')
    else:
        # windows
        return True

    notification_sounds = ['ok.wav', 'fail.wav', 'warning.wav', 'queue.wav']
    file_availability = 0
    for file in notification_sounds:
        file_path = os.path.join(home_address, notification_directory, file)
        if os.path.exists(file_path):
            file_availability += 1

    if file_availability == 4:
        return True
    else:
        logger.sendToLog('Notification sounds are not available', 'ERROR')
        return False


# this function downloads notification sounds from github for Linux, BSD and MacOSX
def createNotificationSounds(main_window):
    # create a directory for sounds in:
    if os_type in OS.UNIX_LIKE:
        # for linux and bsd
        # ~/.local/share/persepolis_download_manager/sounds
        sounds_directory = os.path.join(home_address, '.local/share/persepolis_download_manager/sounds')
    elif os_type in OS.OSX:
        # for mac
        # ~/Library/Application Support/<YourAppName>/sounds/
        sounds_directory = os.path.join(home_address, 'Library/Application Support/persepolis_download_manager/sounds/')

    # create directory
    makeDirs(sounds_directory)

    # file names
    notification_sounds = ['ok.wav', 'fail.wav', 'warning.wav', 'queue.wav']

    # download links
    file_links = ['https://raw.githubusercontent.com/persepolisdm/persepolis/refs/heads/master/resources/notification%20sounds/ok.wav',
                  'https://raw.githubusercontent.com/persepolisdm/persepolis/refs/heads/master/resources/notification%20sounds/fail.wav',
                  'https://raw.githubusercontent.com/persepolisdm/persepolis/refs/heads/master/resources/notification%20sounds/warning.wav',
                  'https://raw.githubusercontent.com/persepolisdm/persepolis/refs/heads/master/resources/notification%20sounds/queue.wav']

    # download notification sound files from github.
    # The result will be written to the log.
    for i in range(4):
        new_download = DownloadSingleLink(file_links[i], os.path.join(sounds_directory, notification_sounds[i]))
        main_window.threadPool.append(new_download)
        main_window.threadPool[-1].start()

    return True


def getSoundPath(name):
    # create a directory for sounds in:
    if os_type in OS.UNIX_LIKE:
        # for linux and bsd
        # ~/.local/share/persepolis_download_manager/sounds
        sounds_directory = os.path.join(home_address, '.local/share/persepolis_download_manager/sounds')
    elif os_type in OS.OSX:
        # for mac
        # ~/Library/Application Support/<YourAppName>/sounds/
        sounds_directory = os.path.join(home_address, 'Library/Application Support/persepolis_download_manager/sounds/')
    # Windows
    else:
        return None

    file_name = name + '.wav'

    file_path = os.path.join(sounds_directory, file_name)

    # return file_path if it exists.
    if os.path.exists(file_path):
        return file_path
    else:
        return None


def notifySend(message1, message2, time, sound, parent=None):

    file = getSoundPath(sound)
    if file is not None:
        playNotification(file)

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
        if os_type in OS.LINUX and dasbus_is_installed:
            bus = SessionMessageBus()

            proxy = bus.get_proxy(
                "org.freedesktop.Notifications",
                "/org/freedesktop/Notifications"
            )

            proxy.Notify(
                "Persepolis", 0, QIcon.fromTheme('persepolis-tray', QIcon(':/persepolis-tray.svg')).name(), message1, message2, [], {}, 10000)

        else:
            parent.system_tray_icon.showMessage(message1, message2, QIcon.fromTheme('persepolis-tray', QIcon(':/persepolis-tray.svg')), 10000)
