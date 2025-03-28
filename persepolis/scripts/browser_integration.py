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

from persepolis.scripts.useful_tools import determineConfigFolder, getExecPath, findExternalAppPath
from persepolis.scripts import osCommands
from persepolis.constants import OS, BROWSER
import subprocess
import platform
import os

os_type = platform.system()

home_address = str(os.path.expanduser("~"))

# download manager config folder .
config_folder = determineConfigFolder()


def browserIntegration(browser):
    # get execution information.
    exec_dictionary = getExecPath()
    exec_path = exec_dictionary['modified_exec_file_path']

    logg_message = ["", "INITIALIZATION"]

    # for GNU/Linux
    if os_type == OS.LINUX:
        # intermediate shell script path
        intermediary = os.path.join(config_folder, 'persepolis_run_shell')

        # Native Messaging Hosts folder path for every browser
        if browser == BROWSER.CHROMIUM:
            native_message_folder = home_address + '/.config/chromium/NativeMessagingHosts'

        elif browser == BROWSER.CHROME:
            native_message_folder = home_address + \
                '/.config/google-chrome/NativeMessagingHosts'

        elif browser == BROWSER.FIREFOX:
            native_message_folder = home_address + \
                '/.mozilla/native-messaging-hosts'

        elif browser == BROWSER.VIVALDI:
            native_message_folder = home_address + \
                '/.config/vivaldi/NativeMessagingHosts'

        elif browser == BROWSER.OPERA:
            native_message_folder = home_address + \
                '/.config/opera/NativeMessagingHosts'

        elif browser == BROWSER.BRAVE:
            native_message_folder = home_address + \
                '/.config/BraveSoftware/Brave-Browser/NativeMessagingHosts'

    # for FreeBSD and OpenBSD
    elif os_type in OS.BSD_FAMILY:
        # find Persepolis execution path
        # persepolis intermediate script path
        intermediary = os.path.join(config_folder, 'persepolis_run_shell')

        # Native Messaging Hosts folder path for every browser
        if browser == BROWSER.CHROMIUM:
            native_message_folder = home_address + '/.config/chromium/NativeMessagingHosts'

        elif browser == BROWSER.CHROME:
            native_message_folder = home_address + \
                '/.config/google-chrome/NativeMessagingHosts'

        elif browser == BROWSER.FIREFOX:
            native_message_folder = home_address + \
                '/.mozilla/native-messaging-hosts'
        elif browser == BROWSER.VIVALDI:
            native_message_folder = home_address + \
                '/.config/vivaldi/NativeMessagingHosts'

        elif browser == BROWSER.OPERA:
            native_message_folder = home_address + \
                '/.config/opera/NativeMessagingHosts'

        elif browser == BROWSER.BRAVE:
            native_message_folder = home_address + \
                '/.config/BraveSoftware/Brave-Browser/NativeMessagingHosts'

    # for Mac OSX
    elif os_type == OS.OSX:
        # find Persepolis execution path
        # persepolis execution path
        intermediary = os.path.join(config_folder, 'persepolis_run_shell')

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

        elif browser == BROWSER.VIVALDI:
            native_message_folder = home_address + \
                '/Library/Application Support/Vivaldi/NativeMessagingHosts'

        elif browser == BROWSER.OPERA:
            native_message_folder = home_address + \
                '/Library/Application Support/Opera/NativeMessagingHosts/'

        elif browser == BROWSER.BRAVE:
            native_message_folder = home_address + \
                '/Library/Application Support/BraveSoftware/Brave-Browser/NativeMessagingHosts/'

    # for MicroSoft Windows os (windows 7 , ...)
    elif os_type == OS.WINDOWS:

        # the execution path in json file for Windows must in form of
        # c:\\Users\\...\\Persepolis Download Manager.exe , so we need 2
        # "\" in address
        intermediary, logg_message = findExternalAppPath('PersepolisBI')

        if browser in BROWSER.CHROME_FAMILY:
            native_message_folder = os.path.join(
                home_address, 'AppData', 'Local',
                'persepolis_download_manager', 'chrome')
        else:
            native_message_folder = os.path.join(
                home_address, 'AppData', 'Local',
                'persepolis_download_manager', 'firefox')

    # WebExtension native hosts file prototype
    webextension_json_connector = {
        "name": "com.persepolis.pdmchromewrapper",
        "type": "stdio",
        "path": str(intermediary),
        "description": "Integrate Persepolis with %s using WebExtensions" % (browser)
    }

    # Add chrom* keys
    if browser in BROWSER.CHROME_FAMILY:
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

        pipe_json = subprocess.Popen(['chmod', '+x', str(native_message_file)],
                                     stderr=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stdin=subprocess.PIPE,
                                     shell=False)

        if pipe_json.wait() == 0:
            json_done = True
        else:
            json_done = False

    else:
        native_done = None
        import winreg
        # add the key to the windows registry
        if browser in BROWSER.CHROME_FAMILY:
            try:
                # create pdmchromewrapper key under NativeMessagingHosts
                winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                                 "SOFTWARE\\Google\\Chrome\\NativeMessagingHosts\\com.persepolis.pdmchromewrapper")
                # open a connection to pdmchromewrapper key
                gintKey = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER, "SOFTWARE\\Google\\Chrome\\NativeMessagingHosts\\com.persepolis.pdmchromewrapper", 0, winreg.KEY_ALL_ACCESS)
                # set native_message_file as key value
                winreg.SetValueEx(gintKey, '', 0, winreg.REG_SZ, native_message_file)
                # close connection to pdmchromewrapper
                winreg.CloseKey(gintKey)

                json_done = True

            except WindowsError:

                json_done = False

        elif browser == BROWSER.FIREFOX:
            try:
                # create pdmchromewrapper key under NativeMessagingHosts for firefox
                winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                                 "SOFTWARE\\Mozilla\\NativeMessagingHosts\\com.persepolis.pdmchromewrapper")
                # open a connection to pdmchromewrapper key for firefox
                fintKey = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER, "SOFTWARE\\Mozilla\\NativeMessagingHosts\\com.persepolis.pdmchromewrapper", 0, winreg.KEY_ALL_ACCESS)
                # set native_message_file as key value
                winreg.SetValueEx(fintKey, '', 0, winreg.REG_SZ, native_message_file)
                # close connection to pdmchromewrapper
                winreg.CloseKey(fintKey)

                json_done = True

            except WindowsError:

                json_done = False

    # create persepolis_run_shell(intermediate script) file for gnu/linux and BSD and Mac
    # firefox and chromium and ... call persepolis with Native Messaging system.
    # json file calls persepolis_run_shell file.
    if os_type in OS.UNIX_LIKE or os_type == OS.OSX:
        # find available shell
        shell_list = ['/bin/bash', '/usr/local/bin/bash', '/bin/sh', '/usr/local/bin/sh', '/bin/ksh', '/bin/tcsh']

        for shell in shell_list:
            if os.path.isfile(shell):
                # define shebang
                shebang = '#!' + shell
                break

        persepolis_run_shell_contents = shebang + '\n' + exec_path + "\t$@"
        f = open(intermediary, 'w')
        f.writelines(persepolis_run_shell_contents)
        f.close()

        # make persepolis_run_shell executable

        pipe_native = subprocess.Popen(['chmod', '+x', intermediary],
                                       stderr=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       stdin=subprocess.PIPE,
                                       shell=False)

        if pipe_native.wait() == 0:
            native_done = True
        else:
            native_done = False

    return json_done, native_done, logg_message
