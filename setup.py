#!/usr/bin/env python3
# coding: utf-8


import os.path
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
# PyQt5
try:
    import PyQt5
    print('python3-pyqt5 is found')
except:
    print('Error : python3-pyqt5 is not installed!')
    sys.exit(1)

# python3-requests
try:
    import requests 
    print('python3-requests is found!')
except:
    print('Error : requests is not installed!')
    sys.exit(1)

# python3-setproctitle
try:
    import setproctitle
    print('python3-setproctitle is found!')
except:
    print("Warning: setproctitle is not installed!")

# aria2
answer = os.system('aria2c --version 1>/dev/null')
if answer != 0:
    print("Error aria2 not installed!")
    sys.exit(1)
else:
    print('aria2 is found!')

# libnotify-bin
answer = os.system('notify-send --version 1>/dev/null')
if answer != 0:
    print("Error libnotify-bin is not installed!")
    sys.exit(1)
else:
    print('libnotify-bin is found!')

# paplay
answer = os.system('paplay --version 1>/dev/null')
if answer != 0:
    print("Warning: paplay not installed!You need pulseaudio for sound notifications!")
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
 
DESCRIPTION = 'Persepolis Download Manager'

if os_type == 'Linux':
    DATA_FILES = [
        ('/usr/share/man/man1/', ['man/persepolis.1.gz']),
        ('/usr/share/applications/', ['xdg/persepolis.desktop']),
        ('/usr/share/pixmaps/', ['icons/persepolis.svg'])
        ]
elif os_type == 'FreeBSD' or os_type == 'OpenBSD':
    DATA_FILES = [
        ('/usr/local/share/man/man1/', ['man/persepolis.1.gz']),
        ('/usr/local/share/applications/', ['xdg/persepolis.desktop']),
        ('/usr/local/share/pixmaps/', ['icons/persepolis.svg'])
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
    version = '2.4.2',
    license = 'GPL3',
    description = DESCRIPTION,
    long_description = DESCRIPTION,
    include_package_data=True,
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
# clearing after installation finished!
for folder in  [ 'build', 'dist', 'root', 'persepolis.egg-info']:
    if os.path.isdir(folder):
        shutil.rmtree(folder)
        print(str(folder)
            + ' is removed!')
os.remove('man/persepolis.1.gz')

