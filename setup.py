#!/usr/bin/env python3
# coding: utf-8
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
import warnings
import sys
import platform
import shutil

# finding os platform
os_type = platform.system()

if os_type == 'Linux' or os_type == 'FreeBSD' or os_type == 'OpenBSD':
    from setuptools import setup, Command, find_packages
    setuptools_available = True
    print(os_type + " detected!")
else:
    print('This script is only work for GNU/Linux or BSD!')
    sys.exit(1)

# Checking dependencies!
not_installed = ''

# PyQt5
try:
    import PyQt5
    print('python3-pyqt5 is found')
except:
    print('Error : python3-pyqt5 is not installed!')
    not_installed = not_installed + 'PyQt5, '

# python3-requests
try:
    import requests 
    print('python3-requests is found!')
except:
    print('Error : requests is not installed!')
    not_installed = not_installed + 'python3-requests, '

# python3-setproctitle
try:
    import setproctitle
    print('python3-setproctitle is found!')
except:
    print("Warning: setproctitle is not installed!")
    not_installed = not_installed + 'python3-setproctitle, '

# psutil
try:
    import psutil
    print('python3-psutil is found!')
except:
    print("Warning: python3-psutil is not installed!")
    not_installed = not_installed + 'psutil, '

# youtube_dl
try:
    import youtube_dl
    print('youtube-dl is found')
except:
    print('Warning: youtube-dl is not installed!')
    not_installed = not_installed + 'youtube-dl, '

# aria2
answer = os.system('aria2c --version 1>/dev/null')
if answer != 0:
    print("Error aria2 not installed!")
    not_installed = not_installed + 'aria2c, '
else:
    print('aria2 is found!')

# libnotify-bin
answer = os.system('notify-send --version 1>/dev/null')
if answer != 0:
    print("Error libnotify-bin is not installed!")
    not_installed = not_installed + 'libnotify-bin, '
else:
    print('libnotify-bin is found!')

# paplay
answer = os.system('paplay --version 1>/dev/null')
if answer != 0:
    print("Warning: paplay not installed!You need pulseaudio for sound notifications!")
    not_installed = not_installed + 'paplay, '
else:
    print('paplay is found!')

# sound-theme-freedesktop
if os_type == 'Linux':
    notifications_path = '/usr/share/sounds/freedesktop/stereo/'
elif os_type == 'FreeBSD' or os_type == 'OpenBSD':
    notifications_path = '/usr/local/share/sounds/freedesktop/stereo/'

if os.path.isdir(notifications_path):
    print('sound-theme-freedesktop is found!')
else:
    print('Warning: sound-theme-freedesktop is not installed! you need this package for sound notifications!')
    not_installed = not_installed + 'sound-theme-freedesktop'

# show warning , if dependencies not installed!
if not_installed != '':
    print('########################')
    print('####### WARNING ########')
    print('########################')
    print('Some dependencies are not installed .It causes some problems for persepolis! : \n')
    print(not_installed + '\n\n')
    print('Read this link for more information: \n')
    print('https://github.com/persepolisdm/persepolis/wiki/git-installation-instruction\n\n')
    answer = input('Do you want to continue?(y/n)')
    if answer not in ['y', 'Y', 'yes']:
        sys.exit(1)

if sys.argv[1] == "test":
   print('We have not unit test :)')
   sys.exit('0')

DESCRIPTION = 'Persepolis Download Manager'

if os_type == 'Linux':
    DATA_FILES = [
        ('/usr/share/man/man1/', ['man/persepolis.1.gz']),
        ('/usr/share/applications/', ['xdg/com.github.persepolisdm.persepolis.desktop']),
        ('/usr/share/metainfo/', ['xdg/com.github.persepolisdm.persepolis.appdata.xml']),
        ('/usr/share/pixmaps/', ['resources/persepolis.svg']),
        ('/usr/share/pixmaps/', ['resources/persepolis-tray.svg'])
        ]
elif os_type == 'FreeBSD' or os_type == 'OpenBSD':
    DATA_FILES = [
        ('/usr/local/share/man/man1/', ['man/persepolis.1.gz']),
        ('/usr/local/share/applications/', ['xdg/com.github.persepolisdm.persepolis.desktop']),
        ('/usr/local/share/metainfo/', ['xdg/com.github.persepolisdm.persepolis.appdata.xml']),
        ('/usr/local/share/pixmaps/', ['resources/persepolis.svg']),
        ('/usr/local/share/pixmaps/', ['resources/persepolis-tray.svg'])
        ]



# finding current directory
cwd = os.path.abspath(__file__)
setup_dir = os.path.dirname(cwd)

#clearing __pycache__
src_pycache = os.path.join(setup_dir, 'persepolis', '__pycache__')
gui_pycache = os.path.join(setup_dir, 'persepolis', 'gui', '__pycache__')
scripts_pycache = os.path.join(setup_dir, 'persepolis', 'scripts', '__pycache__')

for folder in [src_pycache, gui_pycache, scripts_pycache]:
    if os.path.isdir(folder):
        shutil.rmtree(folder)
        print(str(folder)
            + ' is removed!')


# Creating man page file
persepolis_man_page = os.path.join(setup_dir, 'man', 'persepolis.1')
os.system('gzip -f -k -9 "'
        + persepolis_man_page
        + '"')
print('man page file is generated!')

setup(
    name = 'persepolis',
    version = '3.0.1',
    license = 'GPL3',
    description = DESCRIPTION,
    long_description = DESCRIPTION,
    include_package_data = True,
    url = 'https://github.com/persepolisdm/persepolis',
    author = 'AliReza AmirSamimi',
    author_email = 'alireza.amirsamimi@gmail.com',
    maintainer = 'AliReza AmirSamimi',
    maintainer_email = 'alireza.amirsamimi@gmail.com',
    packages = (
        'persepolis',
        'persepolis.scripts', 'persepolis.gui',
        ),
    data_files = DATA_FILES,
    entry_points={
        'console_scripts': [
              'persepolis = persepolis.__main__'
        ]
    }
)

