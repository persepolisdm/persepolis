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
from persepolis.constants import OS

# finding os platform
os_type = platform.system()

if os_type in OS.UNIX_LIKE:
    print(os_type + " detected!")
else:
    print('This script is only work for GNU/Linux or BSD!')
    sys.exit(1)


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


uid = os.getuid()
if uid != 0:
    print('Run this script as root\n\
    if you want to clean unwanted files that created by setup tools')
    sys.exit(1)


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

# clear unwanted files!
for folder in ['build', 'dist', 'root', 'persepolis.egg-info']:
    if os.path.isdir(folder):
        shutil.rmtree(folder)
        print(str(folder)
              + ' is removed!')

man_page = 'man/persepolis.1.gz'
if os.path.isfile(man_page):
    os.remove('man/persepolis.1.gz')
