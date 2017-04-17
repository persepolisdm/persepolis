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

import platform
import os
from newopen import Open
import osCommands
import sys

os_type = platform.system()

home_address = str(os.path.expanduser("~"))


# browser can be firefox or chromium or chrome

def browserIntegration(browser):
    # for GNU/Linux
    if os_type == 'Linux':
        # persepolis execution path
        exec_path = '/usr/bin/persepolis'

        # Native Messaging Hosts folder path for every browser
        if browser == 'chromium':
            native_message_folder = home_address + '/.config/chromium/NativeMessagingHosts'

        elif browser == 'chrome':
            native_message_folder = home_address + \
                                    '/.config/google-chrome/NativeMessagingHosts'

        elif browser == 'firefox':
            native_message_folder = home_address + \
                                    '/.mozilla/native-messaging-hosts'


    # for FreeBSD and OpenBSD
    elif os_type == 'FreeBSD' or os_type == 'OpenBSD':
        # persepolis execution path
        exec_path = '/usr/local/bin/persepolis'

        # Native Messaging Hosts folder path for every browser
        if browser == 'chromium':
            native_message_folder = home_address + '/.config/chromium/NativeMessagingHosts'

        elif browser == 'chrome':
            native_message_folder = home_address + \
                                    '/.config/google-chrome/NativeMessagingHosts'

        elif browser == 'firefox':
            native_message_folder = home_address + \
                                    '/.mozilla/native-messaging-hosts'


    # for Mac OSX
    elif os_type == 'Darwin':
        # finding Persepolis execution path
        cwd = sys.argv[0]
        current_directory = os.path.dirname(cwd)

        exec_path = os.path.join(
            current_directory, 'Persepolis Download Manager')

        # Native Messaging Hosts folder path for every browser
        if browser == 'chromium':
            native_message_folder = home_address + \
                                    '/Library/Application Support/Chromium/NativeMessagingHosts'

        elif browser == 'chrome':
            native_message_folder = home_address + \
                                    '/Library/Application Support/Google/Chrome/NativeMessagingHosts'

        elif browser == 'firefox':
            native_message_folder = home_address + \
                                    '/Library/Application Support/Mozilla/NativeMessagingHosts'


    # for MicroSoft Windows os (windows 7 , ...)
    elif os_type == 'Windows':
        # finding Persepolis execution path
        cwd = sys.argv[0]
        current_directory = os.path.dirname(cwd)

        exec_path = os.path.join(
            current_directory, 'Persepolis Download Manager.exe')

        # the execution path in jason file for Windows must in form of
        # c:\\Users\\...\\Persepolis Download Manager.exe , so we need 2
        # "\" in address
        exec_path = exec_path.replace('\\', r'\\')

        native_message_folder = os.path.join(
            home_address, 'AppData\Local\persepolis_download_manager', str(browser))

    # WebExtension native hosts file prototype
    webextension_json_connector = {
        "name": "com.persepolis.pdmchromewrapper",
        "type": "stdio",
        "path": str(exec_path),
        "description": "Integrate Persepolis with %s using WebExtensions" % (browser)
    }

    # Add chrom* keys
    if browser == 'chrome' or browser == 'chromium':
        webextension_json_connector["allowed_origins"] = [ "chrome-extension://legimlagjjoghkoedakdjhocbeomojao/" ]

    # Add firefox keys
    elif browser == 'firefox':
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

    if os_type != 'Windows':
        os.system('chmod +x "' + str(native_message_file) + '"')

    else:
        import winreg
        # add the key to the windows registry
        if browser == 'chrome' or browser == 'chromium':
            try:
                # create pdmchromewrapper key under NativeMessagingHosts
                winreg.CreateKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\\Google\\Chrome\\NativeMessagingHosts\\com.persepolis.pdmchromewrapper")
                # open a connection to pdmchromewrapper key
                gintKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\\Google\\Chrome\\NativeMessagingHosts\\com.persepolis.pdmchromewrapper", 0, winreg.KEY_ALL_ACCESS)
                # set native_message_file as key value
                winreg.SetValueEx(gintKey, '', 0,winreg.REG_SZ, native_message_file)
                # close connection to pdmchromewrapper
                winreg.CloseKey(gintKey)
                return True
            except WindowsError:
                return False
        elif browser == 'firefox':
            try:
                # create pdmchromewrapper key under NativeMessagingHosts for firefox
                winreg.CreateKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\\Mozilla\\NativeMessagingHosts\\com.persepolis.pdmchromewrapper")
                # open a connection to pdmchromewrapper key for firefox
                fintKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\\Mozilla\\NativeMessagingHosts\\com.persepolis.pdmchromewrapper", 0, winreg.KEY_ALL_ACCESS)
                # set native_message_file as key value
                winreg.SetValueEx(fintKey, '', 0,winreg.REG_SZ, native_message_file)
                # close connection to pdmchromewrapper
                winreg.CloseKey(fintKey)
                return True
            except WindowsError:
                return False
