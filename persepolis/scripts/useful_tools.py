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

from PyQt5.QtWidgets import QStyleFactory
import os
import platform

try:
    from persepolis.scripts import logger
    logger_availability = True
except:
    logger_availability = False

# find operating system
# os_type >> Linux or Darwin(Mac osx) or Windows(Microsoft Windows) or
# FreeBSD or OpenBSD
os_type = platform.system()

# user home address
home_address = os.path.expanduser("~")



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

# this function returns operating system and desktop environment(for linux and bsd).
def osAndDesktopEnvironment():
    desktop_env = None
    if os_type == 'Linux' or os_type == 'FreeBSD' or os_type == 'OpenBSD':
        # find desktop environment('KDE', 'GNOME', ...)
        desktop_env = os.environ.get('XDG_CURRENT_DESKTOP')

    return os_type, desktop_env


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

def returnDefaultSettings():
    os_type, desktop_env = osAndDesktopEnvironment() 

    # persepolis temporary download folder
    if os_type != 'Windows':
        download_path_temp = str(home_address) + '/.persepolis'
    else:
        download_path_temp = os.path.join(
            str(home_address), 'AppData', 'Local', 'persepolis')

    # user download folder path    
    download_path = os.path.join(str(home_address), 'Downloads', 'Persepolis')


    # find available styles(It's depends on operating system and desktop environments).
    available_styles = QStyleFactory.keys()
    icons = 'Breeze'
    if os_type == 'Linux' or os_type == 'FreeBSD' or 'os_type' == 'OpenBSD':
        if desktop_env == 'KDE':
            if 'Breeze' in available_styles:
                style = 'Breeze'
                color_scheme = 'System'
            else:
                style = 'Fusion'
                color_scheme = 'Persepolis Light Blue'

        elif desktop_env == 'GNOME':
    # finout user prefers dark theme or light theme :)
    # read this links for more information:
    # https://wiki.archlinux.org/index.php/GTK%2B#Basic_theme_configuration
    # https://wiki.archlinux.org/index.php/GTK%2B#Dark_theme_variant

            # find user gtk3 config file path.
            gtk3_confing_file_path = os.path.join(home_address, '.config', 'gtk-3.0', 'settings.ini')
            if not(os.path.isfile(gtk3_confing_file_path)):
                if os.path.isfile('/etc/gtk-3.0/settings.ini'):
                    gtk3_confing_file_path = '/etc/gtk-3.0/settings.ini'
                else:
                    gtk3_confing_file_path = None
    
            # read this for more information:
            dark_theme = False
            if gtk3_confing_file_path:
                with open(gtk3_confing_file_path) as f:
                    for line in f:
                        if "gtk-application-prefer-dark-theme" in line:
                            if 'true' in line:
                                dark_theme = True
                            else:
                                dark_theme = False

            if dark_theme:
                icons = 'Breeze-Dark'
                if 'Adwaita-Dark' in available_styles:
                    style = 'Adwaita-Dark'
                    color_scheme = 'System'
                else:
                    style = 'Fusion'
                    color_scheme = 'Persepolis Dark Blue'

            else:
                icons = 'Breeze'
                if 'Adwaita' in available_styles:
                    style = 'Adwaita'
                    color_scheme = 'System'
                else:
                    style = 'Fusion'
                    color_scheme = 'Persepolis Light Blue'
    
    elif os_type == 'Darwin':
        style = 'Macintosh'
        color_scheme = 'System'

    else:
        style = 'Fusion'
        color_scheme = 'Persepolis Light Blue'


    # Persepolis default setting
    default_setting_dict = {'locale': 'en_US', 'toolbar_icon_size': 32, 'wait-queue': [0, 0], 'awake': 'no', 'custom-font': 'no', 'column0': 'yes',
                        'column1': 'yes', 'column2': 'yes', 'column3': 'yes', 'column4': 'yes', 'column5': 'yes', 'column6': 'yes', 'column7': 'yes',
                        'column10': 'yes', 'column11': 'yes', 'column12': 'yes', 'subfolder': 'yes', 'startup': 'no', 'show-progress': 'yes',
                        'show-menubar': 'no', 'show-sidepanel': 'yes', 'rpc-port': 6801, 'notification': 'Native notification', 'after-dialog': 'yes',
                        'tray-icon': 'yes', 'max-tries': 5, 'retry-wait': 0, 'timeout': 60, 'connections': 16, 'download_path_temp': download_path_temp,
                        'download_path': download_path, 'sound': 'yes', 'sound-volume': 100, 'style': style, 'color-scheme': color_scheme,
                        'icons': icons, 'font': 'Ubuntu', 'font-size': 9, 'aria2_path': '', 'video_finder/enable': 'yes', 'video_finder/hide_no_audio': 'yes',
                        'video_finder/hide_no_video': 'yes', 'video_finder/max_links': '3'}

    return default_setting_dict
