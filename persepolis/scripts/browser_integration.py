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
#

import os
import platform
import sys

from persepolis.constants import OS, BROWSER
from persepolis.scripts import osCommands
from persepolis.scripts.useful_tools import determineConfigFolder

os_type = platform.system()

home_address = str(os.path.expanduser("~"))

# download manager config folder .
config_folder = determineConfigFolder()


# browser can be firefox or chromium or chrome

def browserIntegration(browser):
    # for GNU/Linux
    if os_type == OS.LINUX:
        # find Persepolis execution path
        # persepolis execution path
        exec_path = os.path.join(config_folder, 'persepolis_run_shell')

        # Native Messaging Hosts folder path for every browser
        if browser == BROWSER.CHROMIUM:
            native_message_folder = home_address + '/.config/chromium/NativeMessagingHosts'

        elif browser == BROWSER.CHROME:
            native_message_folder = home_address + \
                                    '/.config/google-chrome/NativeMessagingHosts'

        elif browser == BROWSER.FIREFOX:
            native_message_folder = home_address + \
                                    '/.mozilla/native-messaging-hosts'

        elif browser == BROWSER.FIREFOX:
            native_message_folder = home_address + \
                                    '/.config/vivaldi/NativeMessagingHosts'

        elif browser == BROWSER.OPERA:
            native_message_folder = home_address + \
                                    '/.config/opera/NativeMessagingHosts'

    # for FreeBSD and OpenBSD
    elif os_type == OS.FREE_BSD or os_type == OS.OPEN_BSD:
        # find Persepolis execution path
        # persepolis execution path
        exec_path = os.path.join(config_folder, 'persepolis_run_shell')

        # Native Messaging Hosts folder path for every browser
        if browser == BROWSER.CHROMIUM:
            native_message_folder = home_address + '/.config/chromium/NativeMessagingHosts'

        elif browser == BROWSER.CHROME:
            native_message_folder = home_address + \
                                    '/.config/google-chrome/NativeMessagingHosts'

        elif browser == BROWSER.FIREFOX:
            native_message_folder = home_address + \
                                    '/.mozilla/native-messaging-hosts'
        elif browser == BROWSER.FIREFOX:
            native_message_folder = home_address + \
                                    '/.config/vivaldi/NativeMessagingHosts'

        elif browser == BROWSER.OPERA:
            native_message_folder = home_address + \
                                    '/.config/opera/NativeMessagingHosts'



    # for Mac OSX
    elif os_type == OS.DARWIN:
        # find Persepolis execution path
        # persepolis execution path
        exec_path = os.path.join(config_folder, 'persepolis_run_shell')

        # Native Messaging Hosts folder path for every browser
        if browser == BROWSER.CHROMIUM:
            native_message_folder = home_address + \
                                    '/Library/Application Support/Chromium/NativeMessagingHosts'

        elif browser == BROWSER.CHROME:
            native_message_folder = home_address + \
                                    '/Library/Application Support/Google/Chrome/NativeMessagingHosts'

        elif browser == BROWSER.FIREFOX:
            native_message_folder = home_address + \
                                    '/Library/Application Support/Mozilla/NativeMessagingHosts'

        elif browser == BROWSER.FIREFOX:
            native_message_folder = home_address + \
                                    '/Library/Application Support/Vivaldi/NativeMessagingHosts'

        elif browser == BROWSER.OPERA:
            native_message_folder = home_address + \
                                    '/Library/Application Support/Opera/NativeMessagingHosts/'

    # for MicroSoft Windows os (windows 7 , ...)
    elif os_type == OS.WINDOWS:
        # finding Persepolis execution path
        cwd = sys.argv[0]

        current_directory = os.path.dirname(cwd)

        exec_path = os.path.join(
            current_directory, 'Persepolis Download Manager.exe')

        # the execution path in jason file for Windows must in form of
        # c:\\Users\\...\\Persepolis Download Manager.exe , so we need 2
        # "\" in address
        exec_path = exec_path.replace('\\', r'\\')

        if browser in [BROWSER.CHROME, BROWSER.CHROMIUM, BROWSER.OPERA, BROWSER.FIREFOX]:
            native_message_folder = os.path.join(
                home_address, 'AppData\Local\persepolis_download_manager', BROWSER.CHROME)
        else:
            native_message_folder = os.path.join(
                home_address, 'AppData\Local\persepolis_download_manager', BROWSER.FIREFOX)

    # WebExtension native hosts file prototype
    webextension_json_connector = {
        "name": "com.persepolis.pdmchromewrapper",
        "type": "stdio",
        "path": str(exec_path),
        "description": "Integrate Persepolis with %s using WebExtensions" % (browser)
    }

    # Add chrom* keys
    if browser in [BROWSER.CHROME, BROWSER.CHROMIUM, BROWSER.OPERA, BROWSER.FIREFOX]:
        webextension_json_connector["allowed_origins"] = ["chrome-extension://legimlagjjoghkoedakdjhocbeomojao/"]

    # Add firefox keys
    elif browser == BROWSER.FIREFOX:
        webextension_json_connector["allowed_extensions"] = [
            "com.persepolis.pdmchromewrapper@persepolisdm.github.io",
            "com.persepolis.pdmchromewrapper.offline@persepolisdm.github.io"
        ]

    # Build final path
    native_message_file = os.path.join(
        native_message_folder, 'com.persepolis.pdmchromewrapper.json')

    osCommands.makeDirs(native_message_folder)

    # Write NMH file
    f = open(native_message_file, 'w')
    f.write(str(webextension_json_connector).replace("'", "\""))
    f.close()

    if os_type != OS.WINDOWS:
        os.system('chmod +x \"' + str(native_message_file) + '\"')

    else:
        import winreg
        # add the key to the windows registry
        if browser in [BROWSER.CHROME, BROWSER.CHROMIUM, BROWSER.OPERA, BROWSER.FIREFOX]:
            try:
                # create pdmchromewrapper key under NativeMessagingHosts
                winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                                 "SOFTWARE\\Google\\Chrome\\NativeMessagingHosts\\com.persepolis.pdmchromewrapper")
                # open a connection to pdmchromewrapper key
                gintKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                         "SOFTWARE\\Google\\Chrome\\NativeMessagingHosts\\com.persepolis.pdmchromewrapper",
                                         0, winreg.KEY_ALL_ACCESS)
                # set native_message_file as key value
                winreg.SetValueEx(gintKey, '', 0, winreg.REG_SZ, native_message_file)
                # close connection to pdmchromewrapper
                winreg.CloseKey(gintKey)
                return True
            except WindowsError:
                return False
        elif browser == BROWSER.FIREFOX:
            try:
                # create pdmchromewrapper key under NativeMessagingHosts for firefox
                winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                                 "SOFTWARE\\Mozilla\\NativeMessagingHosts\\com.persepolis.pdmchromewrapper")
                # open a connection to pdmchromewrapper key for firefox
                fintKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                         "SOFTWARE\\Mozilla\\NativeMessagingHosts\\com.persepolis.pdmchromewrapper", 0,
                                         winreg.KEY_ALL_ACCESS)
                # set native_message_file as key value
                winreg.SetValueEx(fintKey, '', 0, winreg.REG_SZ, native_message_file)
                # close connection to pdmchromewrapper
                winreg.CloseKey(fintKey)
                return True
            except WindowsError:
                return False

    # create persepolis_run_shell file for gnu/linux and BSD and Mac
    # firefox and chromium and ... call persepolis with Native Messaging system. 
    # json file calls persepolis_run_shell file.
    if os_type == OS.LINUX or os_type == OS.OPEN_BSD or os_type == OS.FREE_BSD or os_type == OS.DARWIN:
        # find available shell
        shell_list = ['/bin/bash', '/usr/local/bin/bash', '/bin/sh', '/usr/local/bin/sh', '/bin/ksh', '/bin/tcsh']

        for shell in shell_list:
            if os.path.isfile(shell):
                # define shebang
                shebang = '#!' + shell
                break

        if os_type == OS.DARWIN:
            # finding Persepolis execution path
            cwd = sys.argv[0]

            current_directory = os.path.dirname(cwd)

            persepolis_path = os.path.join(
                current_directory, 'Persepolis Download Manager')
        else:
            persepolis_path = 'persepolis'

        persepolis_run_shell_contents = shebang + '\n' + '"' + persepolis_path + '" "$@"'

        f = open(exec_path, 'w')
        f.writelines(persepolis_run_shell_contents)
        f.close()

        # make persepolis_run_shell executable

        os.system('chmod +x \"' + exec_path + '\"')
