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

import os.path
import platform
import winreg
from winreg import QueryValueEx, OpenKey, SetValueEx


#finding os_type
os_type = platform.system()

# check startup
def checkstartup():
    # check if it is linux
    if os_type == "Linux" :
        homedir = os.environ['HOME']
        # check if the startup exists
        if os.path.exists(homedir + "/.config/autostart/persepolis.desktop"):
            print("startup enabled !")
            # some more ...
        else:
            print("startup disabled !")
            # some more ...

    # check if it is mac OS
    #elif platform == "darwin":
        # OS X

    # check if it is Windows
    elif os_type == "Windows":
        # try to open startup key and check persepolis value
        try:
            aKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_ALL_ACCESS)
            startupvalue = winreg.QueryValueEx(aKey,'persepolis')
            startup = True
        except WindowsError:
            startup = False

        # if the startup enabled or disabled
        if startup:
            print("startup enabled !")
            # some more ...
        if not startup:
            print("startup disabled !")
            # some more ...

        # Close the connection
        winreg.CloseKey(aKey)

# add startup file
def addstartup():
    # check if it is linux
    if os_type == 'Linux': 
        homedir = os.environ['HOME']
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
        if os.path.exists(homedir + "/.config/autostart"):
            startupfile = open(homedir + "/.config/autostart/persepolis.desktop", 'w+')
            startupfile.write(entry)
            os.chmod(homedir + "/.config/autostart/persepolis.desktop",0o777)
        if not os.path.exists(homedir + "/.config/autostart"):
            os.makedirs(homedir + "/.config/autostart",0o777)
            startupfile = open(homedir + "/.config/autostart/persepolis.desktop", 'w+')
            startupfile.write(entry)
            os.chmod(homedir + "/.config/.autostart/persepolis.desktop",0o777)

    # check if it is mac OS
    #elif platform == "darwin":
        # OS X

    # check if it is Windows
    elif os_type == "Windows":
        # Connect to the startup path in Registry
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,"Software\\Microsoft\\Windows\\CurrentVersion\\Run",0,winreg.KEY_ALL_ACCESS)
        # add persepolis to startup
        winreg.SetValueEx(key, 'persepolis', 0, winreg.REG_SZ, '"C:\Program Files (x86)\Persepolis Download Manager\Persepolis Download Manager.exe" --tray')
        # Close connection
        winreg.CloseKey(key)

# remove startup file
def removestartup():
    # check if it is linux
    if os_type == 'Linux': 
        homedir = os.environ['HOME']
        # if startup file exists
        if os.path.exists(homedir + "/.config/autostart/persepolis.desktop"):
            # remove it
            os.remove(homedir + "/.config/autostart/persepolis.desktop")
        else:
            print("startup not activated !")
            # some more

        # check if it is mac OS
        #elif platform == "darwin":
            # OS X

    # check if it is Windows
    elif os_type == 'Windows': 
        # Connect to the startup path in Registry
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,"Software\\Microsoft\\Windows\\CurrentVersion\\Run",0,winreg.KEY_ALL_ACCESS)
        # add persepolis to startup
        winreg.DeleteValue(key, 'persepolis')
        # Close connection
        winreg.CloseKey(key)


addstartup()
#removestartup()
checkstartup()
