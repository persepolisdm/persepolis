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

import logging
import json
import subprocess
from subprocess import CREATE_NO_WINDOW, DETACHED_PROCESS, CREATE_NEW_PROCESS_GROUP, CREATE_BREAKAWAY_FROM_JOB
import platform
import os
import sys
import struct
import argparse
import random
import sqlite3
from copy import deepcopy
from time import sleep
from PySide6.QtCore import QSettings

# a "PersepolisBI.exe" file must be created from this script. 
# "PersepolisBI.exe" and "Persepolis Download Manager.exe" must be in same directory.
# "PersepolisBI.exe"  act as intermediary between browser(FireFox, Chrome, ...) and "Persepolis Download Manager.exe"

# find operating system
os_type = platform.system()

# user home address
home_address = os.path.expanduser("~")

# persepolis config folder in M.S Windows
config_folder = os.path.join(
    home_address, 'AppData', 'Local', 'persepolis_download_manager')

# create folder if it's not exist.
os.makedirs(config_folder, exist_ok=True)

# persepolis tmp folder path
persepolis_tmp = os.path.join(config_folder, 'persepolis_tmp')

# load persepolis_settings
persepolis_setting = QSettings('persepolis_download_manager', 'persepolis')


# plugins.db is store links, when browser plugins are send new links.
# This class is managing plugin.db
class PluginsDB():
    def __init__(self):
        # plugins.db file path
        plugins_db_path = os.path.join(persepolis_tmp, 'plugins.db')

        # plugins_db_connection
        self.plugins_db_connection = sqlite3.connect(plugins_db_path, check_same_thread=False)

        # plugins_db_cursor
        self.plugins_db_cursor = self.plugins_db_connection.cursor()

        # create a lock for data base
        self.lock = False

    # this method locks data base.
    # this is pervent accessing data base simultaneously.
    def lockCursor(self):
        while self.lock:
            rand_float = random.uniform(0, 0.5)
            sleep(rand_float)

        self.lock = True

    # plugins_db_table contains links that sends by browser plugins.

    # insert new items in plugins_db_table
    def insertInPluginsTable(self, list_):
        # lock data base
        self.lockCursor()

        for dict_ in list_:
            self.plugins_db_cursor.execute("""INSERT INTO plugins_db_table VALUES(
                                                                        NULL,
                                                                        :link,
                                                                        :referer,
                                                                        :load_cookies,
                                                                        :user_agent,
                                                                        :header,
                                                                        :out,
                                                                        'new'
                                                                            )""", dict_)

        self.plugins_db_connection.commit()
        # release lock
        self.lock = False

    # close connections
    def closeConnections(self):
        # lock data base
        self.lockCursor()

        self.plugins_db_cursor.close()
        self.plugins_db_connection.close()

        # release lock
        self.lock = False



# log file address
log_file = os.path.join(str(config_folder), 'persepolisbi.log')

# create log file if it's not exist.
if not os.path.isfile(log_file):
    f = open(log_file, 'w')
    f.close()

# define logging object
logObj = logging.getLogger("Persepolis")
logObj.setLevel(logging.INFO)

# don't show log in console
logObj.propagate = False

# create a file handler
handler = logging.FileHandler(log_file)
handler.setLevel(logging.INFO)
# create a logging format
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logObj.addHandler(handler)


def sendToLog(text="", type="INFO"):
    if type == "INFO":
        logObj.info(text)
    elif type == "ERROR":
        logObj.error(text)
    else:
        logObj.warning(text)



# find exeternal application execution path
def findExternalAppPath(app_name):

    # alongside of the bundle path 
    cwd = sys.argv[0]
    current_directory = os.path.dirname(cwd)
    app_alongside = os.path.join(current_directory, app_name)

   # for Mac OSX and MicroSoft Windows
    app_command = app_alongside
    log_list = ["{}'s file is detected alongside of bundle.".format(app_name), "INFO"]

    return app_command, log_list


# create  terminal arguments
parser = argparse.ArgumentParser(description='PersepolisBI')
parser.add_argument('--tray', action='store_true',
                    help="Persepolis is starting in tray icon. It's useful when you want to put persepolis in system's startup.")
parser.add_argument('--parent-window', action='store', nargs=1,
                    help='this switch is used for chrome native messaging in Windows')
parser.add_argument('--version', action='version', version='PersepolisBI 1.0.0')


# Clears unwanted args ( like args from Browers via NHM )
# unknown arguments (may sent by browser) will save in unknownargs.
args, unknownargs = parser.parse_known_args()

browser_url = True

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
    if os_type == 'Windows':
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


# when browsers plugin calls persepolis or user runs persepolis by terminal arguments,
# then persepolis creates a request file in persepolis_tmp folder and link information added to
# plugins_db.db file(see data_base.py for more information).
# persepolis mainwindow checks persepolis_tmp for plugins request file every 2 seconds (see CheckingThread class in mainwindow.py)
# when request received in CheckingThread, a popup window (AddLinkWindow) comes up and window gets additional download information
# from user (port , proxy , ...) and download starts and request file deleted
if len(plugin_list) != 0:

    # create an object for PluginsDB
    plugins_db = PluginsDB()

    # add plugin_list to plugins_table in plugins.db file.
    plugins_db.insertInPluginsTable(plugin_list)

    # Job is done! close connections.
    plugins_db.closeConnections()

    # notify that a link is added!
    plugin_ready = os.path.join(persepolis_tmp, 'persepolis-plugin-ready')
    f = open(plugin_ready, 'w')
    f.close()

# start persepolis in system tray if browser executed
# and if user select this option in preferences window.
if str(persepolis_setting.value('settings/browser-persepolis')) == 'yes' and (args.parent_window or unknownargs):
    start_persepolis_if_browser_executed = True
else:
    start_persepolis_if_browser_executed = False




# find "Persepolis Download Manager.exe" file path
app_command, log_list = findExternalAppPath('Persepolis Download Manager.exe')
sendToLog(log_list[0], log_list[1])




# call persepolis 
try:
    creationflags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_BREAKAWAY_FROM_JOB | CREATE_NO_WINDOW
    
    if browser_url:
        subprocess.Popen([app_command],
                         creationflags=creationflags,                
                        shell=False)

        sendToLog("Download link(s) is sended to persepolis", "INFO")

    elif start_persepolis_if_browser_executed:
        subprocess.Popen([app_command, '--tray'],
                         creationflags=creationflags,
                        shell=False)
        sendToLog("Browser is executed and persepolis called by browser.")

except Exception as e:
    sendToLog(str(e), "ERROR")