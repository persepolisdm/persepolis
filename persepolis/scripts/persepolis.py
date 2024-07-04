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

try:
    from PySide6 import QtWidgets, QtCore
    from PySide6.QtCore import __version__ as QT_VERSION_STR
    from PySide6.QtGui import QFont
    from PySide6.QtCore import QFile, QTextStream, QSettings, Qt
except:
    from PyQt5 import QtWidgets, QtCore
    from PyQt5.QtGui import QFont
    from PyQt5.QtCore import QFile, QTextStream, QSettings, Qt, QT_VERSION_STR

from persepolis.gui import resources
import traceback
from persepolis.scripts.error_window import ErrorWindow
from persepolis.gui.palettes import DarkFusionPalette, LightFusionPalette
import json
import struct
import argparse
from persepolis.scripts import osCommands
from persepolis.scripts.useful_tools import osAndDesktopEnvironment, determineConfigFolder
from persepolis.constants import OS
from copy import deepcopy
import sys
import os

# finding os platform
os_type, desktop_env = osAndDesktopEnvironment()

# Don't run persepolis as root!
if os_type in (OS.UNIX_LIKE + [OS.OSX]):
    uid = os.getuid()
    if uid == 0:
        print('Do not run persepolis as root.')
        sys.exit(1)


# initialization
# find home address
home_address = os.path.expanduser("~")

# persepolis config_folder
config_folder = determineConfigFolder()

# persepolis tmp folder path
persepolis_tmp = os.path.join(config_folder, 'persepolis_tmp')


# if lock_file_validation == True >> not another instance running,
# else >> another instance of persepolis is running now.
global lock_file_validation

if os_type != OS.WINDOWS:
    import fcntl
    user_name_split = home_address.split('/')
    user_name = user_name_split[2]
# persepolis lock file
    lock_file = '/tmp/persepolis_exec_' + user_name + '.lock'

# create lock file
    fp = open(lock_file, 'w')

    try:
        fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)

        lock_file_validation = True  # Lock file created successfully!
    except IOError:
        lock_file_validation = False  # creating lock_file was unsuccessful! So persepolis is still running

else:  # for windows
    # pypiwin32 must be installed by pip
    from win32event import CreateMutex
    from win32api import GetLastError
    from winerror import ERROR_ALREADY_EXISTS

    handle = CreateMutex(None, 1, 'persepolis_download_manager')

    if GetLastError() == ERROR_ALREADY_EXISTS:
        lock_file_validation = False
    else:
        lock_file_validation = True

# run persepolis mainwindow
if lock_file_validation:

    # execute initialization script
    from persepolis.scripts import initialization
    from persepolis.scripts.mainwindow import MainWindow

# set "persepolis" name for this process in linux and bsd
    if os_type in OS.UNIX_LIKE:
        try:
            from setproctitle import setproctitle
            setproctitle("persepolisdm")
        except:
            from persepolis.scripts import logger
            logger.sendToLog('setproctitle is not installed!', "ERROR")


# load persepolis_settings
persepolis_setting = QSettings('persepolis_download_manager', 'persepolis')


class PersepolisApplication(QtWidgets.QApplication):
    def __init__(self, argv):
        super().__init__(argv)

    def setPersepolisStyle(self, style):
        # set style
        self.persepolis_style = style
        self.setStyle(style)

    def setPersepolisFont(self, font, font_size, custom_font):
        # font and font_size
        self.persepolis_font = font
        self.persepolis_font_size = font_size

        if custom_font == 'yes':
            self.setFont(QFont(font, font_size))
# color_scheme

    def setPersepolisColorScheme(self, color_scheme):
        self.persepolis_color_scheme = color_scheme
        if color_scheme == 'Dark Fusion':
            dark_fusion = DarkFusionPalette()
            self.setPalette(dark_fusion)
            file = QFile(":/dark_style.qss")
            file.open(QFile.ReadOnly | QFile.Text)
            stream = QTextStream(file)
            self.setStyleSheet(stream.readAll())

        elif color_scheme == 'Light Fusion':
            light_fusion = LightFusionPalette()
            self.setPalette(light_fusion)
            file = QFile(":/light_style.qss")
            file.open(QFile.ReadOnly | QFile.Text)
            stream = QTextStream(file)
            self.setStyleSheet(stream.readAll())


# create  terminal arguments
parser = argparse.ArgumentParser(description='Persepolis Download Manager')
# parser.add_argument('chromium', nargs = '?', default = 'no', help='this switch is used for chrome native messaging in Linux and Mac')
parser.add_argument('--link', action='store', nargs=1, help='Download link.(Use "" for links)')
parser.add_argument('--referer', action='store', nargs=1,
                    help='Set an http referrer (Referer). This affects all http/https downloads.  If * is given, the download URI is also used as the referrer.')
parser.add_argument('--cookie', action='store', nargs=1, help='Cookie')
parser.add_argument('--agent', action='store', nargs=1,
                    help='Set user agent for HTTP(S) downloads.  Default: aria2/$VERSION, $VERSION is replaced by package version.')
parser.add_argument('--headers', action='store', nargs=1, help='Append HEADER to HTTP request header. ')
parser.add_argument('--name', action='store', nargs=1, help='The  file  name  of  the downloaded file. ')
parser.add_argument('--default', action='store_true', help='restore default setting')
parser.add_argument('--clear', action='store_true', help='Clear download list and user setting!')
parser.add_argument('--tray', action='store_true',
                    help="Persepolis is starting in tray icon. It's useful when you want to put persepolis in system's startup.")
parser.add_argument('--parent-window', action='store', nargs=1,
                    help='this switch is used for chrome native messaging in Windows')
parser.add_argument('--version', action='version', version='Persepolis Download Manager 4.2.0')


# Clears unwanted args ( like args from Browers via NHM )
# unknown arguments (may sent by browser) will save in unknownargs.
args, unknownargs = parser.parse_known_args()

# if --execute >> yes  >>> persepolis main window  will start.
# if --execute >> no >>> persepolis started before!
browser_url = True

add_link_dictionary = {}
plugin_list = []
browser_plugin_dict = {'link': None,
                       'referer': None,
                       'load_cookies': None,
                       'user_agent': None,
                       'header': None,
                       'out': None
                       }


# This dirty trick will show Persepolis version when there are unknown args
# Unknown args are sent by Browsers for NHM
if args.parent_window or unknownargs:

    # Platform specific configuration
    if os_type == OS.WINDOWS:
        # Set the default I/O mode to O_BINARY in windows
        import msvcrt
        msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

    # Send message to browsers plugin
    message = '{"enable": true, "version": "1.85"}'.encode('utf-8')
    sys.stdout.buffer.write((struct.pack('i', len(message))))
    sys.stdout.buffer.write(message)
    sys.stdout.flush()

    text_length_bytes = sys.stdin.buffer.read(4)

    # Unpack message length as 4 byte integer.
    text_length = struct.unpack('@I', text_length_bytes)[0]

    # Read the text (JSON object) of the message.
    text = sys.stdin.buffer.read(text_length).decode("utf-8")

    if text:

        new_dict = json.loads(text)

        if 'url_links' in new_dict:

            # new_dict is sended by persepolis browser add-on.
            # new_dict['url_links'] contains some lists.
            # every list contains link information.
            for item in new_dict['url_links']:

                copy_dict = deepcopy(browser_plugin_dict)

                if 'url' in item.keys():
                    copy_dict['link'] = str(item['url'])

                    if 'header' in item.keys() and item['header'] != '':
                        copy_dict['header'] = item['header']

                    if 'referrer' in item.keys() and item['referrer'] != '':
                        copy_dict['referer'] = item['referrer']

                    if 'filename' in item.keys() and item['filename'] != '':
                        copy_dict['out'] = os.path.basename(str(item['filename']))

                    if 'useragent' in item.keys() and item['useragent'] != '':
                        copy_dict['user_agent'] = item['useragent']

                    if 'cookies' in item.keys() and item['cookies'] != '':
                        copy_dict['load_cookies'] = item['cookies']

                    plugin_list.append(copy_dict)

        else:
            browser_url = False


# persepolis --clear >> remove config_folder
if args.clear:
    from persepolis.scripts.data_base import PersepolisDB

    # create an object for PersepolisDB
    persepolis_db = PersepolisDB()

    # Reset data base
    persepolis_db.resetDataBase()

    # close connections
    persepolis_db.closeConnections()

    # Reset persepolis_setting
    persepolis_setting.clear()
    persepolis_setting.sync()

    sys.exit(0)

# persepolis --default >> remove persepolis setting.
if args.default:
    persepolis_setting.clear()
    persepolis_setting.sync()
    print('Persepolis restored default')
    sys.exit(0)


if args.link:
    add_link_dictionary['link'] = "".join(args.link)

# if plugins call persepolis, then just start persepolis in system tray
    args.tray = True

if args.referer:
    add_link_dictionary['referer'] = "".join(args.referer)
else:
    add_link_dictionary['referer'] = None

if args.cookie:
    add_link_dictionary['load_cookies'] = "".join(args.cookie)
else:
    add_link_dictionary['load_cookies'] = None

if args.agent:
    add_link_dictionary['user_agent'] = "".join(args.agent)
else:
    add_link_dictionary['user_agent'] = None

if args.headers:
    add_link_dictionary['header'] = "".join(args.headers)
else:
    add_link_dictionary['header'] = None

if args.name:
    add_link_dictionary['out'] = "".join(args.name)
else:
    add_link_dictionary['out'] = None

if args.tray:
    start_in_tray = True
else:
    start_in_tray = False


# when browsers plugin calls persepolis or user runs persepolis by terminal arguments,
# then persepolis creates a request file in persepolis_tmp folder and link information added to
# plugins_db.db file(see data_base.py for more information).
# persepolis mainwindow checks persepolis_tmp for plugins request file every 2 seconds (see CheckingThread class in mainwindow.py)
# when request received in CheckingThread, a popup window (AddLinkWindow) comes up and window gets additional download information
# from user (port , proxy , ...) and download starts and request file deleted

if ('link' in add_link_dictionary.keys()):
    plugin_dict = {'link': add_link_dictionary['link'],
                   'referer': add_link_dictionary['referer'],
                   'load_cookies': add_link_dictionary['load_cookies'],
                   'user_agent': add_link_dictionary['user_agent'],
                   'header': add_link_dictionary['header'],
                   'out': add_link_dictionary['out']
                   }

    plugin_list.append(plugin_dict)

if len(plugin_list) != 0:

    # import PluginsDB
    from persepolis.scripts.data_base import PluginsDB

    # create an object for PluginsDB
    plugins_db = PluginsDB()

    # add plugin_list to plugins_table in plugins.db file.
    plugins_db.insertInPluginsTable(plugin_list)

    # Job is done! close connections.
    plugins_db.closeConnections()

    # notify that a link is added!
    plugin_ready = os.path.join(persepolis_tmp, 'persepolis-plugin-ready')
    osCommands.touch(plugin_ready)

    # start persepolis in system tray
    start_in_tray = True


# start persepolis in system tray if browser executed
# and if user select this option in preferences window.
if str(persepolis_setting.value('settings/browser-persepolis')) == 'yes' and (args.parent_window or unknownargs):
    start_persepolis_if_browser_executed = True
    start_in_tray = True
else:
    start_persepolis_if_browser_executed = False


def main():
    # if lock_file is existed , it means persepolis is still running!
    if lock_file_validation and (not ((args.parent_window or unknownargs) and browser_url is False) or ((args.parent_window or unknownargs) and start_persepolis_if_browser_executed)):

        QAPP = QtWidgets.QApplication.instance()
        if QAPP is None:
            # We do not have an already instantiated QApplication
            # let's add some sane defaults

            # hidpi handling
            qtVersionCompare = tuple(map(int, QT_VERSION_STR.split(".")))
            if qtVersionCompare > (6, 0):
                # Qt6 seems to support hidpi without needing to do anything so continue
                pass
            elif qtVersionCompare > (5, 14):

                try:
                    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
                    QtWidgets.QApplication.setHighDpiScaleFactorRoundingPolicy(
                        QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
                    )
                except Exception as error_message:
                    from persepolis.scripts import logger
                    logger.sendToLog(str(error_message), "ERROR")

            else:  # qt 5.12 and 5.13
                try:
                    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
                    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
                except Exception as error_message:
                    from persepolis.scripts import logger
                    logger.sendToLog(str(error_message), "ERROR")

        # set QT_AUTO_SCREEN_SCALE_FACTOR to 1 for "high DPI displays"
#         os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'

        # run mainwindow

        # set color_scheme and style
        # see palettes.py and setting.py

        # create QApplication
        persepolis_download_manager = PersepolisApplication(sys.argv)

        # setQuitOnLastWindowClosed(False) is needed to prevent persepolis exiting,
        # when it's minimized in system tray.
        persepolis_download_manager.setQuitOnLastWindowClosed(False)

#         # Enable High DPI display
#         try:
#             if hasattr(QStyleFactory, 'AA_UseHighDpiPixmaps'):
#                 persepolis_download_manager.setAttribute(Qt.AA_UseHighDpiPixmaps)
#         except:
#             from persepolis.scripts import logger
#             # write error_message in log file.
#             logger.sendToLog('Qt.AA_UseHighDpiPixmaps is not available!', "ERROR")
        # this line is added fot fixing persepolis view in HighDpi displays
        # more information at: https://doc.qt.io/qt-5/highdpi.html
#         try:
#             persepolis_download_manager.setAttribute(Qt.AA_EnableHighDpiScaling)
#         except:
#             from persepolis.scripts import logger
#             # write error_message in log file.
#             logger.sendToLog('Qt.AA_EnableHighDpiScaling is not available!', "ERROR")
        # set organization name and domain and application name
        persepolis_download_manager.setOrganizationName('com.github.persepolisdm.persepolis')
        persepolis_download_manager.setApplicationName('PersepolisDM')
        persepolis_download_manager.setDesktopFileName('com.github.persepolisdm.persepolis')
        persepolis_download_manager.setApplicationVersion('4.2.0')

        # Persepolis setting
        persepolis_download_manager.setting = QSettings('persepolis_download_manager', 'persepolis')

        # get user's desired font and style , ... from setting
        custom_font = persepolis_download_manager.setting.value('settings/custom-font')
        font = persepolis_download_manager.setting.value('settings/font')
        font_size = int(persepolis_download_manager.setting.value('settings/font-size'))
        style = persepolis_download_manager.setting.value('settings/style')
        color_scheme = persepolis_download_manager.setting.value('settings/color-scheme')
        ui_direction = persepolis_download_manager.setting.value('ui_direction')

        # set style
        persepolis_download_manager.setPersepolisStyle(style)

        # set font
        persepolis_download_manager.setPersepolisFont(font, font_size, custom_font)

        # set color_scheme
        persepolis_download_manager.setPersepolisColorScheme(color_scheme)

        # set ui direction
        if ui_direction == 'rtl':
            persepolis_download_manager.setLayoutDirection(Qt.RightToLeft)

        elif ui_direction in 'ltr':
            persepolis_download_manager.setLayoutDirection(Qt.LeftToRight)

        # run mainwindow
        try:
            mainwindow = MainWindow(start_in_tray, persepolis_download_manager, persepolis_download_manager.setting)
            if start_in_tray:
                mainwindow.hide()
            else:
                mainwindow.show()

        except Exception:
            from persepolis.scripts import logger
            error_message = str(traceback.format_exc())

            # write error_message in log file.
            logger.sendToLog(error_message, "ERROR")

            # Reset persepolis
            error_window = ErrorWindow(error_message)
            error_window.show()

        sys.exit(persepolis_download_manager.exec_())

    elif not ((args.parent_window or unknownargs)):

        # this section warns user that program is still running and no need to run it again
        # and creating a file to notify mainwindow for showing itself!
        # (see CheckingThread in mainwindow.py for more information)
        if len(plugin_list) == 0:

            show_window_file = os.path.join(persepolis_tmp, 'show-window')
            f = open(show_window_file, 'w')
            f.close()

        sys.exit(0)
