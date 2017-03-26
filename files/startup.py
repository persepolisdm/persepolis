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

import os
import platform, sys

home_address = os.path.expanduser("~")

#finding os_type
os_type = platform.system()

if os_type == 'Windows':
    import winreg
    from winreg import QueryValueEx, OpenKey, SetValueEx


# check startup
def checkstartup():
    # check if it is linux
    if os_type == "Linux" or os_type == "FreeBSD"  or os_type == 'OpenBSD' :
        # check if the startup exists
        if os.path.exists(home_address + "/.config/autostart/persepolis.desktop"):
            return True
        else:
            return False

    # check if it is mac
    elif os_type == "Darwin":
        # OS X
        if os.path.exists(home_address + "/Library/LaunchAgents/com.persepolisdm.plist"):
            return True
        else:
            return False

    # check if it is Windows
    elif os_type == "Windows":
        # try to open startup key and check persepolis value
        try:
            aKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_ALL_ACCESS)
            startupvalue = winreg.QueryValueEx(aKey,'persepolis')
            startup = True
        except WindowsError:
            startup = False

        # Close the connection
        winreg.CloseKey(aKey)

        # if the startup enabled or disabled
        if startup:
            return True
        if not startup:
            return False

# add startup file
def addstartup():
    # check if it is linux
    if os_type == 'Linux' or os_type == 'FreeBSD' or os_type == 'OpenBSD' :
        entry = '''!/usr/bin/env xdg-open
        [Desktop Entry]
        Name=Persepolis Download Manager
        Name[fa]=پرسپولیس
        Comment=Download Manager
        GenericName=Download Manager
        GenericName[fa]=نرم افزار مدیریت بارگیری
        Keywords=Internet;WWW;Web;
        Terminal=false
        Type=Application
        Categories=Qt;Network;
        StartupNotify=true
        Exec=persepolis --tray
        Icon=persepolis
        StartupWMClass=persepolis-download-manager'''

        # check if the autostart directry exists & create entry
        if os.path.exists(home_address + "/.config/autostart"):
            startupfile = open(home_address + "/.config/autostart/persepolis.desktop", 'w+')
            startupfile.write(entry)
            os.chmod(home_address + "/.config/autostart/persepolis.desktop",0o777)
        if not os.path.exists(home_address + "/.config/autostart"):
            os.makedirs(home_address + "/.config/autostart",0o777)
            startupfile = open(home_address + "/.config/autostart/persepolis.desktop", 'w+')
            startupfile.write(entry)
            os.chmod(home_address + "/.config/.autostart/persepolis.desktop",0o777)
    # check if it is mac
    elif os_type == "Darwin":
        # OS X
        cwd = sys.argv[0]
        cwd = os.path.dirname(cwd)
        entry = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Label</key>
	<string>com.persepolisdm.persepolis</string>
	<key>Program</key>
	<string>''' + cwd + '''/Persepolis Download Manager</string>
	<key>ProgramArguments</key>
	<array>
		<string>--tray</string>
	</array>
	<key>RunAtLoad</key>
	<true/>
</dict>
</plist>\n'''
        startupfile = open(home_address + '/Library/LaunchAgents/com.persepolisdm.plist', 'w+')
        startupfile.write(entry)
        os.system('launchctl load ' + home_address + "/Library/LaunchAgents/com.persepolisdm.plist")
    # check if it is Windows
    elif os_type == "Windows":

        # Connect to the startup path in Registry
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,"Software\\Microsoft\\Windows\\CurrentVersion\\Run",0,winreg.KEY_ALL_ACCESS)
        # find current persepolis exe path
        cwd = os.getcwd()
        persepolisexetray = '"' + cwd + '\Persepolis Download Manager.exe' + '"' + ' --tray'
        # add persepolis to startup
        winreg.SetValueEx(key, 'persepolis', 0, winreg.REG_SZ,persepolisexetray)

        # Close connection
        winreg.CloseKey(key)

# remove startup file
def removestartup():
    # check if it is linux
    if os_type == 'Linux' or os_type == 'FreeBSD' or os_type == 'OpenBSD' :

        # remove it
        os.remove(home_address + "/.config/autostart/persepolis.desktop")

    # check if it is mac OS
    elif os_type == "Darwin":
        # OS X
        if checkstartup():
            os.system('launchctl unload ' + home_address + "/Library/LaunchAgents/com.persepolisdm.plist")
            os.remove(home_address + "/Library/LaunchAgents/com.persepolisdm.plist")

    # check if it is Windows
    elif os_type == 'Windows':
        if checkstartup() :
            # Connect to the startup path in Registry
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,"Software\\Microsoft\\Windows\\CurrentVersion\\Run",0,winreg.KEY_ALL_ACCESS)

            # remove persepolis from startup
            winreg.DeleteValue(key, 'persepolis')

            # Close connection
            winreg.CloseKey(key)
