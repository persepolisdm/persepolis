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
from persepolis.scripts.useful_tools import getExecPath, findExternalAppPath, runApplication
from persepolis.gui import resources
from persepolis.constants import OS
import platform
import os
from persepolis.scripts import logger
import sys
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


# On Linux and BSD, if Persepolis is not run as bundled,
# the audio files in the freedesktop folder must be converted
# from oga format to wav format and moved to the
# ~/.local/share/persepolis_download_manager/sounds/ folder.
# ffmpeg will do this conversion.
# Therefore, it should be checked that ffmpeg must be
# installed. The reason for this format change is that QSoundEffect
# is not able to play oga format.
# First check if persepolis is run as bundle in linux and bsd
def checkNotificationSounds():
    if os_type in OS.UNIX_LIKE:
        persepolis_path_infromation = getExecPath()
        is_bundle = persepolis_path_infromation['bundle']

        if not is_bundle:
            # check if notification sounds available or not!
            notification_directory = '.local/share/persepolis_download_manager/sounds'
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
        else:
            return True
    else:
        return True


def createNotificationSounds():
    # check availability of freedesktop folder
    if os_type == OS.LINUX:
        freedesktop_path = '/usr/share/sounds/freedesktop/stereo'
    elif os_type in OS.BSD_FAMILY:
        freedesktop_path = '/usr/local/share/sounds/freedesktop/stereo'

    if not (os.path.isdir(freedesktop_path)):
        return False

    # create a directory for sounds in:
    # ~/.local/share/persepolis_download_manager/sounds
    sounds_directory = os.path.join(home_address, '.local/share/persepolis_download_manager/sounds')
    makeDirs(sounds_directory)

    ffmpeg_command, log_list = findExternalAppPath('ffmpeg')

    # convert sound files
    notification_sounds = ['ok.wav', 'fail.wav', 'warning.wav', 'queue.wav']
    freedesktop_files = ['complete.oga', 'dialog-error.oga', 'bell.oga', 'message.oga']
    j = 0
    for i in range(4):
        notification_sound_path = os.path.join(sounds_directory, notification_sounds[i])
        freedesktop_file_path = os.path.join(freedesktop_path, freedesktop_files[i])
        command_arguments = [ffmpeg_command, '-i',
                             freedesktop_file_path,
                             notification_sound_path]

        try:
            pipe = runApplication(command_arguments)
            # conversion is successful
            if pipe.wait() == 0:
                j += 1

        except:
            return False

    if j == 4:
        # all 4 files created successfully.
        logger.sendToLog('Notification sounds are created successfully.', "INFO")
        return True
    else:
        return False


def getSoundPath(name):
    if os_type in OS.UNIX_LIKE:
        persepolis_path_infromation = getExecPath()
        is_bundle = persepolis_path_infromation['bundle']
        file_name = name + '.wav'

        if not is_bundle:
            # check if notification sounds available or not!
            sounds_directory = os.path.join(home_address, '.local/share/persepolis_download_manager/sounds')
            file_path = os.path.join(sounds_directory, file_name)

        else:
            # we use nuikita for creating bundle
            bundle_path = os.path.dirname(sys.executable)
            file_path = os.path.join(bundle_path, file_name)

        # return file_path if it exists.
        if os.path.exists(file_path):
            return file_path
        else:
            return None

    else:
        return True


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
