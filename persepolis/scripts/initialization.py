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


# THIS FILE CONTAINING SOME VARIABLES , ... THAT USING FOR INITIALIZING PERSEPOLIS

from persepolis.scripts.browser_integration import browserIntegration
from persepolis.scripts.useful_tools import determineConfigFolder
from persepolis.scripts import osCommands
from PyQt5.QtCore import QSettings
import subprocess
import platform
import shutil
import time
import os

# initialization

# user home address
home_address = os.path.expanduser("~")

# os_type >> Linux or Darwin(Mac osx) or Windows(Microsoft Windows) or
# FreeBSD or OpenBSD
os_type = platform.system()

# download manager config folder .
config_folder = determineConfigFolder(os_type, home_address)

# persepolis tmp folder path
persepolis_tmp = os.path.join(config_folder, 'persepolis_tmp')


# create folders
for folder in [config_folder, persepolis_tmp]:
    osCommands.makeDirs(folder)

# persepolisdm.log file contains persepolis log.
from persepolis.scripts import logger

# refresh logs!
log_file = os.path.join(str(config_folder), 'persepolisdm.log')

# get current time
current_time = time.strftime('%Y/%m/%d %H:%M:%S')

# find number of lines in log_file. 
with open(log_file) as f:
    lines = sum(1 for _ in f)

# if number of lines in log_file is more than 300, then keep last 200 lines in log_file.
if lines < 300:
    f = open(log_file, 'a')
    f.writelines('Persepolis Download Manager, '\
            + current_time\
            +'\n')
    f.close()
else:
# keep last 200 lines
    line_num = lines - 200
    f = open(log_file, 'r')
    f_lines = f.readlines()
    f.close()

    line_counter = 1
    f = open(log_file, 'w')
    for line in f_lines:
        if line_counter > line_num:
            f.writelines(str(line))

        line_counter = line_counter + 1
    f.close()

    f = open(log_file, 'a')
    f.writelines('Persepolis Download Manager, '\
            + current_time\
            +'\n')
    f.close()


from persepolis.scripts.data_base import PersepolisDB, PluginsDB

# create an object for PersepolisDB
persepolis_db = PersepolisDB()

# create tables
persepolis_db.createTables()

# close connections
persepolis_db.closeConnections()

# create an object for PluginsDB
plugins_db = PluginsDB()

# create tables
plugins_db.createTables()

# delete old links
plugins_db.deleteOldLinks()

# close connections
plugins_db.closeConnections()


# import persepolis_setting
# persepolis is using QSettings for saving windows size and windows
# position and program settings.

persepolis_setting = QSettings('persepolis_download_manager', 'persepolis')

persepolis_setting.beginGroup('settings')

# download files is downloading in temporary folder(download_path_temp) and then they will be moved to user download folder(download_path) after completion.
# persepolis temporary download folder
if os_type != 'Windows':
    download_path_temp = str(home_address) + '/.persepolis'
else:
    download_path_temp = os.path.join(
        str(home_address), 'AppData', 'Local', 'persepolis')

# user download folder path    
download_path = os.path.join(str(home_address), 'Downloads', 'Persepolis')

# Persepolis default setting
default_setting_dict = {'locale': 'en_US', 'toolbar_icon_size': 32, 'wait-queue': [0, 0], 'awake': 'no', 'custom-font': 'no', 'column0': 'yes', 'column1': 'yes', 'column2': 'yes', 'column3': 'yes', 'column4': 'yes', 'column5': 'yes', 'column6': 'yes', 'column7': 'yes', 'column10': 'yes', 'column11': 'yes', 'column12': 'yes',
                             'subfolder': 'yes', 'startup': 'no', 'show-progress': 'yes', 'show-menubar': 'no', 'show-sidepanel': 'yes', 'rpc-port': 6801, 'notification': 'Native notification', 'after-dialog': 'yes', 'tray-icon': 'yes',
                             'max-tries': 5, 'retry-wait': 0, 'timeout': 60, 'connections': 16, 'download_path_temp': download_path_temp, 'download_path': download_path, 'sound': 'yes', 'sound-volume': 100, 'style': 'Fusion',
                             'color-scheme': 'Persepolis Light Blue', 'icons': 'Breeze', 'font': 'Ubuntu', 'font-size': 9, 'aria2_path': '', 
                             'video_finder/enable': 'yes', 'video_finder/hide_no_audio': 'yes', 'video_finder/hide_no_video': 'yes', 'video_finder/max_links': '3'}

# this loop is checking values in persepolis_setting . if value is not
# valid then value replaced by default_setting_dict value
for key in default_setting_dict.keys():

    setting_value = persepolis_setting.value(key, default_setting_dict[key])
    persepolis_setting.setValue(key, setting_value)

# Check that mount point is available of not!
if not(os.path.exists(persepolis_setting.value('download_path_temp'))):
    persepolis_setting.setValue('download_path_temp', default_setting_dict['download_path_temp'])

if not(os.path.exists(persepolis_setting.value('download_path'))):
    persepolis_setting.setValue('download_path', default_setting_dict['download_path'])


persepolis_setting.sync()

# this section  creates temporary download folder and download folder and
# download sub folders if they did not existed.
download_path_temp = persepolis_setting.value('download_path_temp')
download_path = persepolis_setting.value('download_path')


folder_list = [download_path_temp, download_path]

# add subfolders to folder_list if user checked subfolders check box in setting window.
if persepolis_setting.value('subfolder') == 'yes':
    for folder in ['Audios', 'Videos', 'Others', 'Documents', 'Compressed']:
        folder_list.append(os.path.join(download_path, folder))

# create folders in folder_list
for folder in folder_list:
    osCommands.makeDirs(folder)


persepolis_setting.endGroup()

# Browser integration for Firefox and chromium and google chrome
for browser in ['chrome', 'chromium', 'opera', 'vivaldi', 'firefox']:
    browserIntegration(browser)


# get locale and set ui direction
locale = str(persepolis_setting.value('settings/locale'))

# right to left languages
rtl_locale_list = ['fa_IR']

# left to right languages
ltr_locale_list = ['en_US', 'zh_CN', 'fr_FR']

if locale in rtl_locale_list:
    persepolis_setting.setValue('ui_direction', 'rtl')
else:
    persepolis_setting.setValue('ui_direction', 'ltr')

# compatibility
persepolis_version = float(persepolis_setting.value('version/version', 2.5))
if persepolis_version < 2.6:
    from persepolis.scripts.compatibility import compatibility
    try:
        compatibility()
    except Exception as e:

        # create an object for PersepolisDB
        persepolis_db = PersepolisDB()

        # create tables
        persepolis_db.resetDataBase()

        # close connections
        persepolis_db.closeConnections()

        # write error in log
        logger.sendToLog(
            "compatibility ERROR!", "ERROR")
        logger.sendToLog(
                str(e), "ERROR")


    persepolis_version = 2.6

if persepolis_version < 3.0:
    persepolis_setting.beginGroup('settings')

    for key in default_setting_dict.keys():

        setting_value = default_setting_dict[key]
        persepolis_setting.setValue(key, setting_value)

    persepolis_setting.endGroup()


    persepolis_setting.setValue('version/version', 3.0)

if persepolis_version != 3.1:
    # create an object for PersepolisDB
    persepolis_db = PersepolisDB()

    # correct data base
    persepolis_db.correctDataBase()

    # close connections
    persepolis_db.closeConnections()

persepolis_setting.setValue('version/version', 3.1)


persepolis_setting.sync()

