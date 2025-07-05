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

from persepolis.scripts.data_base import PersepolisDB, PluginsDB
from persepolis.scripts import logger
from persepolis.scripts.useful_tools import determineConfigFolder, returnDefaultSettings, osAndDesktopEnvironment, getExecPath
from persepolis.scripts.browser_integration import browserIntegration
from persepolis.scripts import osCommands
from persepolis.constants import OS
import time
import os
import sys

try:
    from PySide6.QtCore import QSettings
except:
    from PyQt5.QtCore import QSettings

# initialization

# download manager config folder .
config_folder = determineConfigFolder()

# persepolis tmp folder path
persepolis_tmp = os.path.join(config_folder, 'persepolis_tmp')

# create folders
for folder in [config_folder, persepolis_tmp]:
    osCommands.makeDirs(folder)

# persepolisdm.log file contains persepolis log.

# refresh logs!
# log files address
initialization_log_file = os.path.join(str(config_folder), 'initialization_log_file.log')
downloads_log_file = os.path.join(str(config_folder), 'downloads_log_file.log')
errors_log_file = os.path.join(str(config_folder), 'errors_log_file.log')

log_files_list = [initialization_log_file, downloads_log_file, errors_log_file]

# get current time
current_time = time.strftime('%Y/%m/%d %H:%M:%S')

# find number of lines in log_file.
for log_file in log_files_list:
    with open(log_file) as f:
        lines = sum(1 for _ in f)

    # if number of lines in log_file is more than 300, then keep last 200 lines in log_file.
    if lines < 300:
        f = open(log_file, 'a')
        f.writelines('===================================================\n' + 'Persepolis Download Manager, ' + current_time + '\n')
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
        f.writelines('Persepolis Download Manager, ' + current_time + '\n')
        f.close()


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

default_setting_dict = returnDefaultSettings()
# this loop is checking values in persepolis_setting . if value is not
# valid then value replaced by default_setting_dict value
for key in default_setting_dict.keys():

    setting_value = persepolis_setting.value(key, default_setting_dict[key])
    persepolis_setting.setValue(key, setting_value)

# set default dwonload path
if not (os.path.exists(persepolis_setting.value('download_path'))):
    persepolis_setting.setValue('download_path', default_setting_dict['download_path'])


persepolis_setting.sync()

# Create downloads folder and subfolders.
# download sub folders if they did not existed.
download_path = persepolis_setting.value('download_path')

folder_list = [download_path]

# add subfolders to folder_list if user checked subfolders check box in setting window.
if persepolis_setting.value('subfolder') == 'yes':
    for folder in ['Audios', 'Videos', 'Others', 'Documents', 'Compressed']:
        folder_list.append(os.path.join(download_path, folder))

# create folders in folder_list
for folder in folder_list:
    osCommands.makeDirs(folder)

persepolis_setting.endGroup()

# Browser integration for Firefox and chromium and google chrome
for browser in ['chrome', 'chromium', 'opera', 'vivaldi', 'firefox', 'brave']:
    json_done, native_done, log_message2 = browserIntegration(browser)

    log_message = browser

    if json_done is True:
        log_message = log_message + ': ' + 'Json file is created successfully.\n'

    else:
        log_message = log_message + ': ' + 'Json ERROR!\n'

    if native_done is True:
        log_message = log_message + 'persepolis executer file is created successfully.\n'

    elif native_done is False:
        log_message = log_message + ': ' + 'persepolis executer file ERROR!\n'

    logger.sendToLog(log_message, 'INITIALIZATION')
    logger.sendToLog(log_message2[0], log_message2[1])

# get locale and set ui direction
locale = str(persepolis_setting.value('settings/locale'))

# right to left languages
rtl_locale_list = ['fa_IR', 'ar']

# left to right languages
ltr_locale_list = ['en_US', 'zh_CN', 'fr_FR', 'pl_PL', 'nl_NL', 'pt_BR', 'es_ES', 'hu', 'tr', 'tr_TR']

if locale in rtl_locale_list:
    persepolis_setting.setValue('ui_direction', 'rtl')
else:
    persepolis_setting.setValue('ui_direction', 'ltr')

# check the existance of .desktop and icons file for
# Linux and BSD bundle and create it if it's necessary.
# check if persepolis run as bundle first
# find os platform
os_type, desktop_env = osAndDesktopEnvironment()

if os_type in OS.UNIX_LIKE:
    exec_dictionary = getExecPath()
    is_bundle = exec_dictionary['bundle']
    if is_bundle:
        # user home address
        home_address = os.path.expanduser("~")

        bundle_path = os.path.dirname(sys.executable)
        # check existance of .desktop file
        dot_desktop_path = os.path.join(home_address, '.local/share/applications/com.github.persepolisdm.persepolis.desktop')
        icon_desktop_path = os.path.join(home_address, '.local/share/icons/hicolor/scalable/apps/com.github.persepolisdm.persepolis.svg')
        icon_tray_path = os.path.join(home_address, '.local/share/icons/hicolor/scalable/apps/persepolis-tray.svg')

        local_share_file_path = [dot_desktop_path,
                                 icon_desktop_path,
                                 icon_tray_path]

        dot_desktop_bundle = os.path.join(bundle_path, 'com.github.persepolisdm.persepolis.desktop.in')
        icon_desktop_bundle = os.path.join(bundle_path, 'com.github.persepolisdm.persepolis.svg')
        icon_tray_bundle = os.path.join(bundle_path, 'persepolis-tray.svg')

        in_bundle_file_path = [dot_desktop_bundle,
                               icon_desktop_bundle,
                               icon_tray_bundle]

        for i in range(3):
            # rewrite .desktop file every time
            if not (os.path.exists(local_share_file_path[i])) or i == 0:
                osCommands.copyFile(in_bundle_file_path[i], local_share_file_path[i])

        # rewrite Exec path in .desktop file.
        # perhaps user changed the place of the bundle.
        # get exec path
        # modify lines
        # Because of space in file name and file path,
        # Exec path in .desktop file must be in "".

        exec_path = '"' + exec_dictionary['modified_exec_file_path'] + '"'

        # get .desktop content
        with open(dot_desktop_path, 'r') as file:
            content = file.read()

        # replace @persepolisbin@ by new exec path
        new_content = content.replace('@persepolisbin@', exec_path)

        # write it to file
        with open(dot_desktop_path, 'w') as file:
            file.write(new_content)

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

if persepolis_version < 3.1:
    # create an object for PersepolisDB
    persepolis_db = PersepolisDB()

    # correct data base
    persepolis_db.correctDataBase()

    # close connections
    persepolis_db.closeConnections()

    persepolis_version = 3.1

if persepolis_version < 4.0:
    persepolis_setting.beginGroup('settings')

    for key in default_setting_dict.keys():

        setting_value = default_setting_dict[key]
        persepolis_setting.setValue(key, setting_value)

    persepolis_setting.endGroup()


if persepolis_version < 4.1:
    # create an object for PersepolisDB
    persepolis_db = PersepolisDB()

    # correct data base
    persepolis_db.correctDataBaseForVersion410()

    # close connections
    persepolis_db.closeConnections()

    persepolis_setting.setValue('version/version', 4.1)


if persepolis_version < 4.11:
    # create an object for PersepolisDB
    persepolis_db = PersepolisDB()

    # correct data base
    persepolis_db.correctDataBaseForVersion411()

    # close connections
    persepolis_db.closeConnections()

    persepolis_setting.setValue('version/version', 4.11)

persepolis_setting.setValue('version/version', 4.2)
persepolis_setting.setValue('version/version', 4.3)

if persepolis_version < 5.0:
    persepolis_setting.beginGroup('settings')

    for key in default_setting_dict.keys():

        setting_value = default_setting_dict[key]
        persepolis_setting.setValue(key, setting_value)

    persepolis_setting.endGroup()

if persepolis_version < 5.01:
    persepolis_setting.beginGroup('settings')

    for key in default_setting_dict.keys():

        setting_value = default_setting_dict[key]
        persepolis_setting.setValue(key, setting_value)

    persepolis_setting.endGroup()


persepolis_setting.setValue('version/version', 5.01)
persepolis_setting.setValue('version/version', 5.1)
persepolis_setting.setValue('version/version', 5.11)

persepolis_setting.sync()
