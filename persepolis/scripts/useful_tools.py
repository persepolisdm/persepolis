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
from persepolis.constants import OS
import urllib.parse
import subprocess
import platform
import sys
import os

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


# determine the config folder path based on the operating system
def determineConfigFolder():
    if os_type in OS.UNIX_LIKE:
        config_folder = os.path.join(
            str(home_address), ".config/persepolis_download_manager")
    elif os_type == OS.OSX:
        config_folder = os.path.join(
            str(home_address), "Library/Application Support/persepolis_download_manager")
    elif os_type == OS.WINDOWS:
        config_folder = os.path.join(
            str(home_address), 'AppData', 'Local', 'persepolis_download_manager')

    return config_folder

# this function returns operating system and desktop environment(for linux and bsd).


def osAndDesktopEnvironment():
    desktop_env = None
    if os_type in OS.UNIX_LIKE:
        # find desktop environment('KDE', 'GNOME', ...)
        desktop_env = os.environ.get('XDG_CURRENT_DESKTOP')

    return os_type, desktop_env


# this function converts file_size to KiB or MiB or GiB
def humanReadbleSize(size, input_type='file_size'): 
    labels = ['KiB', 'MiB', 'GiB', 'TiB']
    i = -1
    if size < 1024:
        return str(size) + ' B'

    while size >= 1024:
        i += 1
        size = size / 1024
        
    if input_type == 'speed':
        j = 0
    else:
        j = 1

    if i > j:
        return str(round(size, 2)) + ' ' + labels[i]
    else:
        return str(round(size, None)) + ' ' + labels[i]

# this function converts human readable size to byte


def convertToByte(file_size):

    # if unit is not in Byte
    if file_size[-2:] != ' B':

        unit = file_size[-3:]

        # persepolis uses float type for GiB and TiB
        if unit == 'GiB' or unit == 'TiB':

            size_value = float(file_size[:-4])

        else:
            size_value = int(float(file_size[:-4]))
    else:
        unit = None
        size_value = int(float(file_size[:-3]))

    # covert them in byte
    if not(unit):
        in_byte_value = size_value

    elif unit == 'KiB':
        in_byte_value = size_value*1024

    elif unit == 'MiB':
        in_byte_value = size_value*1024*1024

    elif unit == 'GiB':
        in_byte_value = size_value*1024*1024*1024

    elif unit == 'TiB':
        in_byte_value = size_value*1024*1024*1024*1024

    return int(in_byte_value)


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
    if os_type != OS.WINDOWS:
        download_path_temp = str(home_address) + '/.persepolis'
    else:
        download_path_temp = os.path.join(
            str(home_address), 'AppData', 'Local', 'persepolis')

    # user download folder path
    download_path = os.path.join(str(home_address), 'Downloads', 'Persepolis')

    # find available styles(It's depends on operating system and desktop environments).
    available_styles = QStyleFactory.keys()
    style = 'Fusion'
    color_scheme = 'Dark Fusion'
    icons = 'Breeze-Dark'
    if os_type in OS.UNIX_LIKE:
        if desktop_env == 'KDE':
            if 'Breeze' in available_styles:
                style = 'Breeze'
                color_scheme = 'System'
        else:
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
                icons = 'Breeze'
                if 'Adwaita' in available_styles:
                    style = 'Adwaita'
                    color_scheme = 'System'
                else:
                    style = 'Fusion'
                    color_scheme = 'Light Fusion'

    elif os_type == OS.OSX:
        if 'macintosh' in available_styles:
            style = 'macintosh'
            color_scheme = 'System'
            icons = 'Breeze'

    elif os_type == OS.WINDOWS:
        style = 'Fusion'
        color_scheme = 'Dark Fusion'
        icons = 'Breeze-Dark'

    else:
        style = 'Fusion'
        color_scheme = 'Dark Fusion'
        icons = 'Breeze-Dark'

    # keyboard shortcuts
    delete_shortcut = "Ctrl+D"
    remove_shortcut = "Ctrl+R"
    add_new_download_shortcut = "Ctrl+N"
    import_text_shortcut = "Ctrl+O"
    video_finder_shortcut = "Ctrl+V"
    quit_shortcut = "Ctrl+Q"
    hide_window_shortcut = "Ctrl+W"
    move_up_selection_shortcut = "Ctrl+Up"
    move_down_selection_shortcut = "Ctrl+Down"

    # Persepolis default setting
    default_setting_dict = {'locale': 'en_US', 'toolbar_icon_size': 32, 'wait-queue': [0, 0], 'awake': 'no', 'custom-font': 'no', 'column0': 'yes',
                            'column1': 'yes', 'column2': 'yes', 'column3': 'yes', 'column4': 'yes', 'column5': 'yes', 'column6': 'yes', 'column7': 'yes',
                            'column10': 'yes', 'column11': 'yes', 'column12': 'yes', 'subfolder': 'yes', 'startup': 'no', 'show-progress': 'yes',
                            'show-menubar': 'no', 'show-sidepanel': 'yes', 'rpc-port': 6801, 'notification': 'Native notification', 'after-dialog': 'yes',
                            'tray-icon': 'yes', 'browser-persepolis': 'yes', 'hide-window': 'yes', 'max-tries': 5, 'retry-wait': 0, 'timeout': 60,
                            'connections': 16, 'download_path_temp': download_path_temp, 'download_path': download_path, 'sound': 'yes', 'sound-volume': 100,
                            'style': style, 'color-scheme': color_scheme, 'icons': icons, 'font': 'Ubuntu', 'font-size': 9, 'aria2_path': '',
                            'video_finder/max_links': '3', 'shortcuts/delete_shortcut': delete_shortcut, 'shortcuts/remove_shortcut': remove_shortcut,
                            'shortcuts/add_new_download_shortcut': add_new_download_shortcut, 'shortcuts/import_text_shortcut': import_text_shortcut,
                            'shortcuts/video_finder_shortcut': video_finder_shortcut, 'shortcuts/quit_shortcut': quit_shortcut,
                            'shortcuts/hide_window_shortcut': hide_window_shortcut, 'shortcuts/move_up_selection_shortcut': move_up_selection_shortcut,
                            'shortcuts/move_down_selection_shortcut': move_down_selection_shortcut}

    return default_setting_dict


def muxer(parent, video_finder_dictionary):

    result_dictionary = {'error': 'no_error',
                         'ffmpeg_error_message': None,
                         'final_path': None,
                         'final_size': None}

    # find file path
    video_file_dictionary = parent.persepolis_db.searchGidInAddLinkTable(video_finder_dictionary['video_gid'])
    audio_file_dictionary = parent.persepolis_db.searchGidInAddLinkTable(video_finder_dictionary['audio_gid'])

    # find inputs and output file path for ffmpeg
    video_file_path = video_file_dictionary['download_path']
    audio_file_path = audio_file_dictionary['download_path']
    final_path = video_finder_dictionary['download_path']

    # calculate final file's size
    video_file_size = parent.persepolis_db.searchGidInDownloadTable(video_finder_dictionary['video_gid'])['size']
    audio_file_size = parent.persepolis_db.searchGidInDownloadTable(video_finder_dictionary['audio_gid'])['size']

    # convert size to byte
    video_file_size = convertToByte(video_file_size)
    audio_file_size = convertToByte(audio_file_size)

    final_file_size = video_file_size + audio_file_size

    # check free space
    free_space = freeSpace(final_path)

    if free_space:
        if final_file_size > free_space:
            result_dictionary['error'] = 'not enough free space'

        else:

            # find final file's name
            final_file_name = urllib.parse.unquote(os.path.basename(video_file_path))

            # if video's extension is 'mp4' then the final output file's extension is 'mp4'
            # if video's extension is 'webm' then the final output file's extension is 'mkv'

            file_name_split = final_file_name.split('.')
            video_extension = file_name_split[-1]

            if video_extension == 'webm':
                extension_length = len(file_name_split[-1]) + 1

                final_file_name = final_file_name[0:-extension_length] + '.mkv'

            if parent.persepolis_setting.value('settings/download_path') == final_path:
                if parent.persepolis_setting.value('settings/subfolder') == 'yes':
                    final_path = os.path.join(final_path, 'Videos')

            # rename file if file already existed
            i = 1
            final_path_pluse_name = os.path.join(final_path, final_file_name)

            while os.path.isfile(final_path_pluse_name):

                extension_length = len(file_name_split[-1]) + 1

                new_name = final_file_name[0:-extension_length] + \
                    '_' + str(i) + final_file_name[-extension_length:]

                final_path_pluse_name = os.path.join(final_path, new_name)
                i = i + 1

            # start muxing
            if os_type in OS.UNIX_LIKE:
                pipe = subprocess.Popen(['ffmpeg', '-i', video_file_path,
                                         '-i', audio_file_path,
                                         '-c', 'copy',
                                         '-shortest',
                                         '-map', '0:v:0',
                                         '-map', '1:a:0',
                                         '-loglevel', 'error',
                                         '-strict', '-2',
                                         final_path_pluse_name],
                                        stderr=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stdin=subprocess.PIPE,
                                        shell=False)

            elif os_type == OS.DARWIN:
                # ffmpeg path in mac
                # ...path/Persepolis Download Manager.app/Contents/MacOS/ffmpeg
                cwd = sys.argv[0]
                current_directory = os.path.dirname(cwd)
                ffmpeg_path = os.path.join(current_directory, 'ffmpeg')

                pipe = subprocess.Popen([ffmpeg_path, '-i', video_file_path,
                                         '-i', audio_file_path,
                                         '-c', 'copy',
                                         '-shortest',
                                         '-map', '0:v:0',
                                         '-map', '1:a:0',
                                         '-loglevel', 'error',
                                         '-strict', '-2',
                                         final_path_pluse_name],
                                        stderr=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stdin=subprocess.PIPE,
                                        shell=False)

            elif os_type == OS.WINDOWS:
                # ffmpeg path in windows
                cwd = sys.argv[0]
                current_directory = os.path.dirname(cwd)
                ffmpeg_path = os.path.join(current_directory, 'ffmpeg.exe')

                # NO_WINDOW option avoids opening additional CMD window in MS Windows.
                NO_WINDOW = 0x08000000

                pipe = subprocess.Popen([ffmpeg_path, '-i', video_file_path,
                                         '-i', audio_file_path,
                                         '-c', 'copy',
                                         '-shortest',
                                         '-map', '0:v:0',
                                         '-map', '1:a:0',
                                         '-loglevel', 'error',
                                         '-strict', '-2',
                                         final_path_pluse_name],
                                        stdout=subprocess.PIPE,
                                        stdin=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        shell=False,
                                        creationflags=NO_WINDOW)

            if pipe.wait() == 0:
                # muxing was finished successfully.
                result_dictionary['error'] = 'no error'

                result_dictionary['final_path'] = final_path_pluse_name
                result_dictionary['final_size'] = humanReadbleSize(final_file_size)

            else:
                result_dictionary['error'] = 'ffmpeg error'
                out, ffmpeg_error_message = pipe.communicate()

                result_dictionary['ffmpeg_error_message'] = ffmpeg_error_message.decode('utf-8')

    return result_dictionary
