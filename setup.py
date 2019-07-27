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


import gzip
import os
import platform
import shutil
import sys

from persepolis.configs import (VERSION, LICENSE)
from persepolis.constants import OS

# finding os platform
os_type = platform.system()

if os_type == OS.LINUX or os_type == OS.FREE_BSD or os_type == OS.OPEN_BSD:
    from setuptools import setup, find_packages

    setuptools_available = True
    print(os_type + " detected!")
else:
    print('This script is only work for GNU/Linux or BSD!')
    sys.exit(1)


# functions
def generate_persepolis_man_page():
    global persepolis_man_page
    with open(persepolis_man_page, 'rb') as \
            persepolis_man_page_file:
        with gzip.open('{}.gz'.format(persepolis_man_page), 'wb', compresslevel=9) as \
                compressed_persepolis_man_page:
            shutil.copyfileobj(persepolis_man_page_file, compressed_persepolis_man_page)


# Checking dependencies!
not_installed = ''

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
if os_type == OS.LINUX:
    notifications_path = '/usr/share/sounds/freedesktop/stereo/'
elif os_type == OS.FREE_BSD or os_type == OS.OPEN_BSD:
    notifications_path = '/usr/local/share/sounds/freedesktop/stereo/'
else:
    notifications_path = None

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
    print("We don't have unit tests yet :)")
    sys.exit('0')

DESCRIPTION = 'Persepolis Download Manager'

if os_type == OS.LINUX:
    DATA_FILES = [
        ('/usr/share/man/man1/', ['man/persepolis.1.gz']),
        ('/usr/share/applications/', ['xdg/com.github.persepolisdm.persepolis.desktop']),
        ('/usr/share/metainfo/', ['xdg/com.github.persepolisdm.persepolis.appdata.xml']),
        ('/usr/share/pixmaps/', ['resources/persepolis.svg']),
        ('/usr/share/pixmaps/', ['resources/persepolis-tray.svg'])
    ]
elif os_type == OS.FREE_BSD or os_type == OS.OPEN_BSD:
    DATA_FILES = [
        ('/usr/local/share/man/man1/', ['man/persepolis.1.gz']),
        ('/usr/local/share/applications/', ['xdg/com.github.persepolisdm.persepolis.desktop']),
        ('/usr/local/share/metainfo/', ['xdg/com.github.persepolisdm.persepolis.appdata.xml']),
        ('/usr/local/share/pixmaps/', ['resources/persepolis.svg']),
        ('/usr/local/share/pixmaps/', ['resources/persepolis-tray.svg'])
    ]
else:
    DATA_FILES = []

# finding current directory
cwd = os.path.abspath(__file__)
setup_dir = os.path.dirname(cwd)

# clearing __pycache__
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
generate_persepolis_man_page()

print('man page file is generated!')

setup(
    name='persepolis',
    version=VERSION,
    license=LICENSE,
    description=DESCRIPTION,
    long_description=DESCRIPTION,
    include_package_data=True,
    url='https://github.com/persepolisdm/persepolis',
    author='AliReza AmirSamimi',
    author_email='alireza.amirsamimi@gmail.com',
    maintainer='AliReza AmirSamimi',
    maintainer_email='alireza.amirsamimi@gmail.com',
    packages=find_packages(exclude=(
        '.env', '.venv', 'test', 'man', 'resources', 'xdg', '.tx', '.github', 'build', 'dist'
    )),
    install_requires=[
        'youtube-dl',
        'psutil',
        'setproctitle',
        'requests',
        'PyQt5',
        'PyQt5-stubs',
    ],
    data_files=DATA_FILES,
    entry_points={
        'console_scripts': [
            'persepolis = persepolis.__main__:run'
        ]
    },
    classifiers=(
        "Programming Language :: Python :: 3",
    )
)
