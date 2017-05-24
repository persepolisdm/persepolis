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

import platform
import sys
import os
import shutil

# finding os platform
os_type = platform.system()


# installation path
if os_type == 'Linux':
    print('GNU/Linux distribution detected!')
    bin_path = '/usr/bin/persepolis'
    share_path = '/usr/share/persepolis/'
    pixamps_path = '/usr/share/pixmaps/persepolis.svg'
    applications_path = '/usr/share/applications/persepolis.desktop'
    man_path = '/usr/share/man/man1/persepolis.1.gz'

elif os_type == 'FreeBSD' or os_type == 'OpenBSD':
    print('BSD distribution detected!')
    bin_path = '/usr/local/bin/persepolis'
    share_path = '/usr/local/share/persepolis/'
    pixamps_path = '/usr/local/share/pixmaps/persepolis.svg'
    applications_path = '/usr/local/share/applications/persepolis.desktop'
    man_path = '/usr/local/share/man/man1/persepolis.1.gz'

else:
    print('Exit!')
    sys.exit(0)

uid = os.getuid()
if uid != 0:
    print('Error: please run this file as root user!')
    sys.exit(1)



# Checking dependencies!
try:
    import PyQt5
    print('python3-pyqt5 is found')
except:
    print('Error : python3-pyqt5 is not installed!')
    sys.exit(1)

try:
    import requests 
    print('python3-requests is found!')
except:
    print('Error : requests is not installed!')
    sys.exit(1)

try:
    import setproctitle
    print('python3-setproctitle is found!')
except:
    print("Warning: setproctitle is not installed!")

answer = os.system('aria2c --version 1>/dev/null')
if answer != 0:
    print("Error aria2 not installed!")
    sys.exit(1)
else:
    print('aria2 is found!')

answer = os.system('notify-send --version 1>/dev/null')
if answer != 0:
    print("Error libnotify-bin is not installed!")
    sys.exit(1)
else:
    print('libnotify-bin is found!')

answer = os.system('paplay --version 1>/dev/null')
if answer != 0:
    print("Warning: paplay not installed!You need pulseaudio for sound notifications!")
else:
    print('paplay is found!')

# finding current directory
cwd = os.path.abspath(__file__)
setup_dir = os.path.dirname(cwd)

# adding shebang to bin/persepolis_exec
if os_type == 'OpenBSD':
    shebang = '#!/usr/local/bin/python3.6'
else:
    shebang = '#!/usr/bin/env python3'

persepolis_exec_path = os.path.join(setup_dir ,'bin' ,'Persepolis Download Manager')
f = open(persepolis_exec_path, 'r')
f_lines = f.readlines()
f.close()

persepolis_path = os.path.join(setup_dir, 'bin', 'persepolis')
f = open(persepolis_path , 'w')
f.writelines(str(shebang) + '\n')

for line in f_lines:
    f.writelines(str(line))

f.close()

# making persepolis executable
os.system('chmod +x "'
        + persepolis_path 
        + '"' )
print('persepolis file is generated in: \n '
        + persepolis_path)

# moving persepolis executable file to persepolis_bin
if os.path.isfile(bin_path):
    os.remove(bin_path)

shutil.move(persepolis_path, bin_path)

print('persepolis file is moved to:\n '
        + bin_path)


# Creating share_folder contents
share_folder = os.path.join(setup_dir, 'persepolis')
if os.path.isdir(share_folder):
    shutil.rmtree(share_folder)

os.mkdir(share_folder)

src_path = os.path.join(setup_dir, 'src')

share_src_path = os.path.join(share_folder , 'src')
shutil.copytree(src_path, share_src_path)


src_pycache = os.path.join(share_folder, 'src', '__pycache__')
gui_pycache = os.path.join(share_folder, 'src', 'gui', '__pycache__')
scripts_pycache = os.path.join(share_folder, 'src', 'scripts', '__pycache__')

for folder in [src_pycache, gui_pycache, scripts_pycache]:
    if os.path.isdir(folder):
        shutil.rmtree(folder)
print('persepolis share folder contents is generated!')

# copying share_folder to share_path
if os.path.isdir(share_path):
    shutil.rmtree(share_path)

shutil.copytree(share_folder, share_path)
shutil.rmtree(share_folder)

print('persepolis share folder is copied!')


# copying persepolis.desktop
persepolis_desktop_path = os.path.join(setup_dir, 'xdg', 'persepolis.desktop')
os.system('chmod +x "'
        + persepolis_desktop_path
        + '"')
if os.path.isfile(applications_path):
    os.remove(applications_path)

shutil.copy(persepolis_desktop_path, applications_path)

print('persepolis desktop file is copied!')

# copying man page
# Creating man page file
persepolis_man_page = os.path.join(setup_dir, 'man', 'persepolis.1')
os.system('gzip -k -9 "'
        + persepolis_man_page
        + '"')
print('man page file is generated!')
persepolis_man_file = os.path.join(setup_dir, 'man', 'persepolis.1.gz')
if os.path.isfile(man_path):
    os.remove(man_path)

shutil.move(persepolis_man_file, man_path)

print('man page file is copied!')

# copying icon file
icon_path = os.path.join(setup_dir, 'icons', 'icon.svg')
shutil.copy(icon_path, pixamps_path)

print('persepolis icon file is copied!')

print('installation is finished!')
