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
import os
import platform
import subprocess
import sys
if sys.platform == "win32":
    import winreg

os_type = platform.system()
home_address = str(os.path.expanduser("~"))

# download manager config folder .
config_folder = determineConfigFolder()


def removeRegistryKey(browser):
    logg_message = 'trying to remove registry kry for ' + str(browser) + ': '
    if browser == BROWSER.CHROME or browser == BROWSER.CHROMIUM:
        try:
            # Open the parent key
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"SOFTWARE\Google\Chrome\NativeMessagingHosts",
                                0,
                                winreg.KEY_ALL_ACCESS) as parent_key:
                # Delete the pdmchromewrapper key
                winreg.DeleteKey(parent_key, "com.persepolis.pdmchromewrapper")
                logg_message = logg_message + 'Key deleted successfully.'

        except FileNotFoundError:
            logg_message = logg_message + 'The specified key does not exist.'
        except WindowsError as e:
            logg_message = logg_message + f'An error occurred: {e}'
    elif browser == BROWSER.FIREFOX:
        try:
            # Open the parent key
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"SOFTWARE\Mozilla\NativeMessagingHosts",
                                0,
                                winreg.KEY_ALL_ACCESS) as parent_key:
                # Delete the pdmchromewrapper key
                winreg.DeleteKey(parent_key, "com.persepolis.pdmchromewrapper")
                logg_message = logg_message + 'Key deleted successfully.'

        except FileNotFoundError:
            logg_message = logg_message + 'The specified key does not exist.'

        except WindowsError as e:
            logg_message = logg_message + f'An error occurred: {e}'
    else:
        logg_message = logg_message + 'No need to remove registry key.'

    return logg_message


def installIntermidiary(intermediary):
    intermediary_done = None
    exec_dictionary = getExecPath()
    exec_path = exec_dictionary['modified_exec_file_path']

    # create persepolis_run_shell(intermediry script) file for gnu/linux and BSD and Mac
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
            intermediary_done = True
        else:
            intermediary_done = False
    else:
        # for M.S.Windows
        intermediary_done = True

    return intermediary_done


def uninstallNativeMessageHost(browser, native_message_folder):
    # native message host path
    native_message_file = os.path.join(
        native_message_folder, 'com.persepolis.pdmchromewrapper.json')

    # remove file
    answer = osCommands.remove(native_message_file)

    if answer == 'ok':
        logg_message = 'Native message file for ' + str(browser) + ' has been deleted!'
    elif answer == 'cant':
        logg_message = 'Persepolis can not delete native message host file for ' + str(browser) + '.'

    return logg_message


def installNativeMessageHost(browser, native_message_folder, webextension_json_connector):
    json_done = None
    # native message host path
    native_message_file = os.path.join(
        native_message_folder, 'com.persepolis.pdmchromewrapper.json')

    osCommands.makeDirs(native_message_folder)

    # Write native message host file
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
        import winreg
        # add the key to the windows registry
        if browser in BROWSER.CHROME_FAMILY:
            try:
                # create pdmchromewrapper key under NativeMessagingHosts
                winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                                 r"SOFTWARE\Google\Chrome\NativeMessagingHosts\com.persepolis.pdmchromewrapper")
                # open a connection to pdmchromewrapper key
                gintKey = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER, r"SOFTWARE\Google\Chrome\NativeMessagingHosts\com.persepolis.pdmchromewrapper", 0, winreg.KEY_ALL_ACCESS)
                # set native_message_file as key value
                winreg.SetValueEx(gintKey, '', 0, winreg.REG_SZ, native_message_file)
                # close connection to pdmchromewrapper
                winreg.CloseKey(gintKey)

                json_done = True

            except WindowsError:

                json_done = False

        elif browser == BROWSER.FIREFOX_FAMILY:
            try:
                # create pdmchromewrapper key under NativeMessagingHosts for firefox
                winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                                 r"SOFTWARE\Mozilla\NativeMessagingHosts\com.persepolis.pdmchromewrapper")
                # open a connection to pdmchromewrapper key for firefox
                fintKey = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER, r"SOFTWARE\Mozilla\NativeMessagingHosts\com.persepolis.pdmchromewrapper", 0, winreg.KEY_ALL_ACCESS)
                # set native_message_file as key value
                winreg.SetValueEx(fintKey, '', 0, winreg.REG_SZ, native_message_file)
                # close connection to pdmchromewrapper
                winreg.CloseKey(fintKey)

                json_done = True

            except WindowsError:

                json_done = False
    return json_done


def nativeMessageHostFile(browser, intermediary):
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
    elif browser == BROWSER.FIREFOX_FAMILY:
        webextension_json_connector["allowed_extensions"] = [
            "com.persepolis.pdmchromewrapper@persepolisdm.github.io",
            "com.persepolis.pdmchromewrapper.offline@persepolisdm.github.io"
        ]

    return webextension_json_connector


def getIntermediaryPath():

    if os_type in OS.UNIX_LIKE or os_type == OS.OSX:
        intermediary = os.path.join(config_folder, 'persepolis_run_shell')
        logg_message = str(intermediary)
    elif os_type == OS.WINDOWS:
        intermediary, logg_message = findExternalAppPath('PersepolisBI')

    logg_message = "Persepolis intermediary path: " + logg_message
    return intermediary, logg_message


def getNativeMessageFolder(browser):

    if os_type in OS.UNIX_LIKE:
        if browser == BROWSER.CHROMIUM:
            return os.path.join(home_address, '.config/chromium/NativeMessagingHosts')
        elif browser == BROWSER.CHROME:
            return os.path.join(home_address, '.config/google-chrome/NativeMessagingHosts')
        elif browser == BROWSER.FIREFOX:
            return os.path.join(home_address, '.mozilla/native-messaging-hosts')
        elif browser == BROWSER.VIVALDI:
            return os.path.join(home_address, '.config/vivaldi/NativeMessagingHosts')
        elif browser == BROWSER.OPERA:
            return os.path.join(home_address, '.config/opera/NativeMessagingHosts')
        elif browser == BROWSER.BRAVE:
            return os.path.join(home_address, '.config/BraveSoftware/Brave-Browser/NativeMessagingHosts')
        elif browser == BROWSER.LIBREWOLF:
            return os.path.join(home_address, '.librewolf/native-messaging-hosts')

    elif os_type == OS.OSX:
        if browser == BROWSER.CHROMIUM:
            return os.path.join(home_address, 'Library/Application Support/Chromium/NativeMessagingHosts')
        elif browser == BROWSER.CHROME:
            return os.path.join(home_address, 'Library/Application Support/Google/Chrome/NativeMessagingHosts')
        elif browser == BROWSER.FIREFOX:
            return os.path.join(home_address, 'Library/Application Support/Mozilla/NativeMessagingHosts')
        elif browser == BROWSER.VIVALDI:
            return os.path.join(home_address, 'Library/Application Support/Vivaldi/NativeMessagingHosts')
        elif browser == BROWSER.OPERA:
            return os.path.join(home_address, 'Library/Application Support/Opera/NativeMessagingHosts')
        elif browser == BROWSER.BRAVE:
            return os.path.join(home_address, 'Library/Application Support/BraveSoftware/Brave-Browser/NativeMessagingHosts')
        elif browser == BROWSER.LIBREWOLF:
            return os.path.join(home_address, 'Library/LibreWolf/NativeMessagingHosts')

    elif os_type == OS.WINDOWS:
        if browser in BROWSER.CHROME_FAMILY:
            return os.path.join(home_address, 'AppData', 'Local', 'persepolis_download_manager', 'chrome')

        elif browser in BROWSER.FIREFOX_FAMILY:
            return os.path.join(home_address, 'AppData', 'Local', 'persepolis_download_manager', 'firefox')
    else:
        return None


def browserIntegration(browser):
    native_message_folder = getNativeMessageFolder(browser)
    intermediary, logg_message = getIntermediaryPath()
    webextension_json_connector = nativeMessageHostFile(browser, intermediary)
    json_done = installNativeMessageHost(browser, native_message_folder, webextension_json_connector)
    intermediary_done = installIntermidiary(intermediary)

    return json_done, intermediary_done, logg_message


def browserIsolation(browser):
    native_message_folder = getNativeMessageFolder(browser)
    logg_message = uninstallNativeMessageHost(browser, native_message_folder)
    if os_type == OS.WINDOWS:
        logg_message2 = removeRegistryKey(browser)
    else:
        logg_message2 = ''

    return logg_message, logg_message2
