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
import json
import sys
if sys.platform == "win32":
    import winreg

os_type = platform.system()
home_address = str(os.path.expanduser("~"))

# download manager config folder .
config_folder = determineConfigFolder()

# Mapping for registry keys per browser
windows_registry_paths = {
    BROWSER.CHROME: r"SOFTWARE\Google\Chrome\NativeMessagingHosts\com.persepolis.chrome",
    BROWSER.CHROMIUM: r"SOFTWARE\Chromium\NativeMessagingHosts\com.persepolis.chromium",
    BROWSER.BRAVE: r"SOFTWARE\BraveSoftware\Brave-Browser\NativeMessagingHosts\com.persepolis.brave",
    BROWSER.VIVALDI: r"SOFTWARE\Vivaldi\NativeMessagingHosts\com.persepolis.vivaldi",
    BROWSER.OPERA: r"SOFTWARE\Opera Software\Opera Stable\NativeMessagingHosts\com.persepolis.opera",
    BROWSER.FIREFOX: r"SOFTWARE\Mozilla\NativeMessagingHosts\com.persepolis.firefox",
    "librewolf": r"SOFTWARE\Mozilla\NativeMessagingHosts\com.persepolis.librewolf"
}
def browserIntegration(browser, custom_path=None):
    exec_dictionary = getExecPath()
    exec_path = exec_dictionary['modified_exec_file_path']
    logg_message = ["", "INITIALIZATION"]

    if os_type == OS.LINUX or os_type in OS.BSD_FAMILY or os_type == OS.OSX:
        intermediary = os.path.join(config_folder, 'persepolis_run_shell')
        native_message_folder = get_native_message_folder(browser, custom_path)
    elif os_type == OS.WINDOWS:
        possible_paths = [
            os.path.join(os.environ.get('ProgramFiles', ''), 'Persepolis Download Manager', 'PersepolisBI.exe'),
            os.path.join(os.environ.get('ProgramFiles(x86)', ''), 'Persepolis Download Manager', 'PersepolisBI.exe'),
        ]
        intermediary = None
        for path in possible_paths:
            if os.path.isfile(path):
                intermediary = path
                break
        if not intermediary:
            intermediary, logg_message = findExternalAppPath('PersepolisBI')
            if not os.path.isabs(intermediary):
                intermediary = os.path.abspath(intermediary)
        native_message_folder = get_native_message_folder(browser, custom_path)

    webextension_json_connector = {
        "name": f"com.persepolis.{browser.lower()}",
        "type": "stdio",
        "path": str(intermediary),
        "description": f"Integrate Persepolis with {browser} using WebExtensions"
    }


    # Determine manifest file name and write JSON only once
    if browser == BROWSER.FIREFOX:
        webextension_json_connector["name"] = "com.persepolis.firefox"
        webextension_json_connector["allowed_extensions"] = [
            "com.persepolis.pdmchromewrapper@persepolisdm.github.io",
            
        ]
        manifest_filename = "com.persepolis.firefox.json"
    elif browser == "librewolf":
        webextension_json_connector["name"] = "com.persepolis.librewolf"
        webextension_json_connector["allowed_extensions"] = [
            "com.persepolis.pdmchromewrapper@persepolisdm.github.io",
        ]
        manifest_filename = "com.persepolis.librewolf.json"
    else:
        if browser in BROWSER.CHROME_FAMILY:
            webextension_json_connector["allowed_origins"] = ["chrome-extension://legimlagjjoghkoedakdjhocbeomojao/"]
        manifest_filename = get_manifest_filename(browser)

    native_message_file = os.path.join(native_message_folder, manifest_filename)
    osCommands.makeDirs(native_message_folder)
    with open(native_message_file, 'w') as f:
        json.dump(webextension_json_connector, f, indent=2)

    json_done = False
    native_done = None

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
        # Registry for Chromium-based browsers
        reg_path = windows_registry_paths.get(browser)
        if reg_path:
            try:
                winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
                gintKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_ALL_ACCESS)
                winreg.SetValueEx(gintKey, '', 0, winreg.REG_SZ, native_message_file)
                winreg.CloseKey(gintKey)
                json_done = True
            except OSError:
                json_done = False
        # Registry for Firefox and LibreWolf
        elif browser == BROWSER.FIREFOX or browser == "librewolf":
            reg_path = windows_registry_paths.get(browser)
            try:
                winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
                fintKey = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_ALL_ACCESS)
                winreg.SetValueEx(fintKey, '', 0, winreg.REG_SZ, native_message_file)
                winreg.CloseKey(fintKey)
                json_done = True
            except OSError:
                json_done = False

    if os_type in OS.UNIX_LIKE or os_type == OS.OSX:
        shell_list = ['/bin/bash', '/usr/local/bin/bash', '/bin/sh', '/usr/local/bin/sh', '/bin/ksh', '/bin/tcsh']
        shebang = ''
        for shell in shell_list:
            if os.path.isfile(shell):
                shebang = '#!' + shell
                break
        persepolis_run_shell_contents = shebang + '\n' + "python3 -m persepolis \"$@\""
        with open(intermediary, 'w') as f:
            f.writelines(persepolis_run_shell_contents)
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


def get_manifest_filename(browser):
    return f"com.persepolis.{browser.lower()}.json"


def get_manifest_path_for_browser(browser, custom_path=None):
    folder = get_native_message_folder(browser, custom_path)
    if not folder:
        return None
    return os.path.join(folder, get_manifest_filename(browser))


def get_native_message_folder(browser, custom_path=None):
    if custom_path:
        return os.path.expanduser(custom_path)

    if os_type == OS.LINUX or os_type in OS.BSD_FAMILY:
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
        elif browser == "librewolf":
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
        elif browser == "librewolf":
            return os.path.join(home_address, 'Library/LibreWolf/NativeMessagingHosts')

    elif os_type == OS.WINDOWS:
        if browser == "librewolf":
            return os.path.join(os.environ['LOCALAPPDATA'], "Librewolf", "NativeMessagingHosts")
        elif browser == BROWSER.CHROMIUM:
            return os.path.join(os.environ['LOCALAPPDATA'], "Chromium", "User Data", "NativeMessagingHosts")
        elif browser == BROWSER.FIREFOX:
            return os.path.join(os.environ['LOCALAPPDATA'],  "Mozilla", "NativeMessagingHosts")
        elif browser == BROWSER.CHROME:
            return os.path.join(os.environ['LOCALAPPDATA'], "Google", "Chrome", "User Data", "NativeMessagingHosts")
        elif browser == BROWSER.BRAVE:
            return os.path.join(os.environ['LOCALAPPDATA'],  "BraveSoftware", "Brave-Browser", "User Data", "NativeMessagingHosts")
        elif browser == BROWSER.OPERA:
            return os.path.join(os.environ['LOCALAPPDATA'],  "Opera Software", "Opera Stable", "NativeMessagingHosts")
        elif browser == BROWSER.VIVALDI:
            return os.path.join(os.environ['LOCALAPPDATA'],  "Vivaldi", "User Data", "NativeMessagingHosts")
    return None


def remove_registry_key(browser):
    reg_path = windows_registry_paths.get(browser)
    if reg_path:
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, reg_path)
        except FileNotFoundError:
            pass
        except OSError as e:
            print(f"Failed to remove registry key for {browser}: {e}")


def remove_manifests_for_browsers(browsers, custom_path=None):
    for browser in browsers:
        try:
            if browser.strip() == "":
                continue
            path = get_manifest_path_for_browser(browser, custom_path)
            if path and os.path.exists(path):
                os.remove(path)
                print(f"Removed manifest for {browser}: {path}")
            if os_type == OS.WINDOWS:
                remove_registry_key(browser)
        except Exception as e:
            print(f"Failed to remove manifest for {browser}: {e}")


def install_native_hosts(browsers, custom_path=None):
    log_messages = []
    for browser in browsers:
        try:
            json_done, native_done, log = browserIntegration(browser, custom_path)
            log_messages.append(f"[{browser}] JSON: {json_done}, Native: {native_done}")
        except Exception as e:
            log_messages.append(f"[{browser}] Failed: {str(e)}")
    return log_messages
