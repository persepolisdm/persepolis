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
import platform

# finding os platform
os_type = platform.system()

# Checking dependencies!
not_installed = ''

# PyQt5 or PySide6
try:
    import PySide6
    print('python3-pyside6 is found')
    pyside6_is_installed = True
except:
    pyside6_is_installed = False

if not(pyside6_is_installed):
    try:
        import PyQt5
        print('python3-pyqt5 is found')
    except:
        print('Error : python3-pyqt5 or pyside6 must be installed!')
        not_installed = not_installed + '(PyQt5 or PySide6) '

# python3-requests
try:
    import requests
    print('python3-requests is found!')
except:
    print('Error : requests is not installed!')
    not_installed = not_installed + 'python3-requests, '

# python3-urllib3
try:
    import urllib3
    print('python3-urllib3 is found!')
except:
    print('Error : urllib3 is not installed!')
    not_installed = not_installed + 'python3-urllib3, '


# python3-setproctitle
try:
    import setproctitle
    print('python3-setproctitle is found!')
except:
    print("Warning: setproctitle is not installed!")
    not_installed = not_installed + 'python3-setproctitle, '

# python3-PySocks
try:
    import socks
    print('python3-pysocks is found!')
except:
    print("Warning: python3-pysocks is not installed!")
    not_installed = not_installed + 'python3-pysocks, '


# psutil
try:
    import psutil
    print('python3-psutil is found!')
except:
    print("Warning: python3-psutil is not installed!")
    not_installed = not_installed + 'psutil, '

# yt_dlp
try:
    import yt_dlp
    print('yt-dlp is found')
except:
    print('Warning: yt-dlp is not installed!')
    not_installed = not_installed + 'yt-dlp, '

# ffmpeg
answer = os.system('ffmpeg -version 1>/dev/null')
if answer != 0:
    print("Warning: ffmpeg not installed!")
    not_installed = not_installed + 'ffmpeg, '
else:
    print('ffmpeg is found!')


if os_type == 'Linux':
    try:
        from dasbus.connection import SessionMessageBus
        print('python3-dasbus is found!')
    except:
        print('python3-dasbus is not installed!')
        not_installed = not_installed + 'python3-dasbus,'

if not_installed != '':
    print('########################')
    print('####### WARNING ########')
    print('########################')
    print('Some dependencies are not installed .It causes some problems for persepolis! : \n')
    print(not_installed + '\n\n')
    print('Read this link for more information: \n')
    print('https://github.com/persepolisdm/persepolis/wiki/git-installation-instruction\n\n')
