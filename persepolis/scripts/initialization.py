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
import shutil
import subprocess
import plistlib
from persepolis.scripts.browser_integration import install_native_hosts, remove_manifests_for_browsers

try:
    from PySide6.QtCore import QSettings
except:
    from PyQt5.QtCore import QSettings
# for windows platform, we need to import winreg
if sys.platform == "win32":
    import winreg

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
# Set default browsers for native messaging integration (only if not already set)
persepolis_setting.beginGroup("settings/native_messaging")

def detect_installed_browsers():   
    detected_browsers = set()
    if sys.platform == "win32":
        # Windows-specific registry detection
        registry_locations = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Clients\StartMenuInternet"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Clients\StartMenuInternet"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Clients\StartMenuInternet"),
        ]
        browser_mapping = {
            "Google Chrome": "chrome",
            "Chromium": "chromium",
            "Mozilla Firefox": "firefox",
        }
        for root, path in registry_locations:
            try:
                with winreg.OpenKey(root, path) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        subkey_name = winreg.EnumKey(key, i)
                        display_name = winreg.QueryValue(key, subkey_name)
                        mapped_browser = browser_mapping.get(display_name)
                        if mapped_browser:
                            detected_browsers.add(mapped_browser)
            except FileNotFoundError:
                continue
    elif sys.platform == "darwin":
        # macOS-specific detection using Spotlight and Info.plist
        browser_mapping = {
            "firefox": "org.mozilla.firefox",
            "chrome": "com.google.Chrome",
            "chromium": "org.chromium.Chromium",
        }
        for name, bundle_id in browser_mapping.items():
            try:
                output = subprocess.check_output(
                    ['mdfind', f'kMDItemCFBundleIdentifier=="{bundle_id}"'],
                    text=True, stderr=subprocess.DEVNULL
                ).strip()
                if output:
                    app_path = output.splitlines()[0]
                    plist_path = os.path.join(app_path, "Contents", "Info.plist")
                    if os.path.exists(plist_path):
                        with open(plist_path, "rb") as f:
                            plist = plistlib.load(f)
                            exec_name = plist.get("CFBundleExecutable")
                            if exec_name:
                                exec_path = os.path.join(app_path, "Contents", "MacOS", exec_name)
                                if os.path.exists(exec_path):
                                    detected_browsers.add(name)
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
    else:
        # PATH-based detection for Linux and other Unix-likes
        browser_mapping = {
            "firefox": ["firefox"],
            "chrome": ["google-chrome", "google-chrome-stable", "chrome"],
            "chromium": ["chromium", "chromium-browser"],
        }

        for browser, executables in browser_mapping.items():
            if any(shutil.which(name) for name in executables):
                detected_browsers.add(browser)

    return detected_browsers

supported_browsers = ['chrome', 'chromium', 'opera', 'vivaldi', 'firefox', 'brave', 'librewolf']
default_enabled_browsers = detect_installed_browsers()

for browser in supported_browsers:
    if persepolis_setting.value(browser) is None:
        persepolis_setting.setValue(browser, 'true' if browser in default_enabled_browsers else 'false')

persepolis_setting.endGroup()
persepolis_setting.sync()



# Browser integration for Firefox and chromium and google chrome


# Load user-selected browsers from QSettings
persepolis_setting.beginGroup('settings/native_messaging')
enabled_browsers = []

for key in persepolis_setting.childKeys():
    if persepolis_setting.value(key) == 'true':
        enabled_browsers.append(key)

persepolis_setting.endGroup()

# Install manifests only for selected browsers
log_messages = install_native_hosts(enabled_browsers)
for log in log_messages:
    logger.sendToLog(log, 'INITIALIZATION')

# Optional: Clean up manifests from unselected browsers
all_known_browsers = ['chrome', 'chromium', 'opera', 'vivaldi', 'firefox', 'brave', 'librewolf']
disabled_browsers = list(set(all_known_browsers) - set(enabled_browsers))
remove_manifests_for_browsers(disabled_browsers)


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


if persepolis_version < 5.2:
    persepolis_setting.beginGroup('settings')

    for key in default_setting_dict.keys():

        setting_value = default_setting_dict[key]
        persepolis_setting.setValue(key, setting_value)

    persepolis_setting.endGroup()

persepolis_setting.setValue('version/version', 5.2)

persepolis_setting.sync()
