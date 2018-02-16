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

try:
    from persepolis.scripts import logger
    logger_availability = True
except:
    logger_availability = False

# determine the config folder path base on the oprating system
def determineConfigFolder(os_type, home_address):

    if os_type == 'Linux' or os_type == 'FreeBSD' or os_type == 'OpenBSD':
        config_folder = os.path.join(
            str(home_address), ".config/persepolis_download_manager")
    elif os_type == 'Darwin':
        config_folder = os.path.join(
            str(home_address), "Library/Application Support/persepolis_download_manager")
    elif os_type == 'Windows':
        config_folder = os.path.join(
            str(home_address), 'AppData', 'Local', 'persepolis_download_manager')

    return config_folder




# this function converts file_size to KiB or MiB or GiB
def humanReadbleSize(size): 
    labels = ['KiB', 'MiB', 'GiB', 'TiB']
    i = -1
    if size < 1024:
        return str(size) + ' B'

    while size >= 1024:
        i += 1
        size = size / 1024

    p = 2 if i > 1 else None
    return str(round(size, p)) +' '+ labels[i]
   
# this function checks free space in hard disk.
def freeSpace(dir):
    try:
        import psutil
    except:
        if logger_availability:
            logger.sendToLog("psutil in not installed!", "ERROR")

        return None

    try:
        dir_space = psutil.disk_usage(dir)
        free_space = dir_space.free
        return int(free_space)

    except Exception as e:
        # log in to the log file
        if logger_availability:
            logger.sendToLog("persepolis couldn't find free space value:\n" + str(e), "ERROR")

        return None


