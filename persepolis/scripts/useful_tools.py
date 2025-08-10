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

from persepolis.constants.Os import OS
from pathlib import Path
import urllib.parse
import subprocess
import requests
import platform
import textwrap
import time
import sys
import os

try:
    from PySide6.QtCore import QThread, Signal, QProcess
    from PySide6.QtWidgets import QStyleFactory
except ImportError:
    from PyQt5.QtWidgets import QStyleFactory
    from PyQt5.QtCore import QThread, QProcess
    from PyQt5.QtCore import pyqtSignal as Signal

try:
    from persepolis.scripts import logger
    logger_availability = True
except ImportError:
    logger_availability = False

# find operating system
# os_type >> Linux or Darwin(Mac osx) or Windows(Microsoft Windows) or
# FreeBSD or OpenBSD
os_type = platform.system()

# user home address
home_address = os.path.expanduser("~")

# runApplication in a thread.


class RunApplicationThread(QThread):
    RUNAPPCALLBACKSIGNAL = Signal(list)

    def __init__(self, command_argument, call_back=False):
        QThread.__init__(self)
        self.command_argument = command_argument
        self.call_back = call_back

    def run(self):
        pipe = runApplication(self.command_argument)

        if self.call_back:
            self.RUNAPPCALLBACKSIGNAL.emit([pipe])

# determine the config folder path based on the operating system


def determineConfigFolder():
    if os_type in OS.UNIX_LIKE:
        config_folder = os.path.join(
            home_address, ".config/persepolis_download_manager")
    elif os_type == OS.OSX:
        config_folder = os.path.join(
            home_address, "Library/Application Support/persepolis_download_manager")
    elif os_type == OS.WINDOWS:
        config_folder = os.path.join(
            home_address, 'AppData', 'Local', 'persepolis_download_manager')

    return config_folder

# this function returns operating system and desktop environment(for linux and bsd).


def osAndDesktopEnvironment():
    desktop_env = None
    if os_type in OS.UNIX_LIKE:
        # find desktop environment('KDE', 'GNOME', ...)
        xdg_desktop = os.environ.get("XDG_CURRENT_DESKTOP")
        if xdg_desktop is not None:
            desktop_env = xdg_desktop.lower()
        else:
            desktop_env = "unknown"
            if logger_availability:
                logger.sendToLog(
                    "XDG_CURRENT_DESKTOP environment variable not found.", "WARNING"
                )
    return os_type, desktop_env


# this function converts file_size to KiB or MiB or GiB
def humanReadableSize(size, input_type='file_size'):
    labels = ['KiB', 'MiB', 'GiB', 'TiB']
    i = -1
    if size < 1024:
        return str(size), 'B'

    while size >= 1024:
        i += 1
        size = size / 1024

    if i > 1:
        return round(size, 2), labels[i]
    elif i == 1 and input_type == 'speed':
        return round(size, 1), labels[i]
    else:
        return round(size, None), labels[i]

# this function converts second to hour and minute


def convertTime(time):
    minutes = int(time // 60)
    if minutes == 0:
        return str(int(time)) + 's'
    elif minutes < 60:
        return str(minutes) + 'm'
    else:
        hours = minutes // 60
        minutes = minutes - (hours * 60)
        return str(hours) + 'h ' + str(minutes) + 'm'


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
    if not (unit):
        in_byte_value = size_value

    elif unit == 'KiB':
        in_byte_value = size_value * 1024

    elif unit == 'MiB':
        in_byte_value = size_value * 1024 * 1024

    elif unit == 'GiB':
        in_byte_value = size_value * 1024 * 1024 * 1024

    elif unit == 'TiB':
        in_byte_value = size_value * 1024 * 1024 * 1024 * 1024

    return int(in_byte_value)


# this function checks free space in hard disk.
def freeSpace(dir):
    try:
        import psutil
    except ImportError:
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

    # user download folder path
    download_path = os.path.join(home_address, 'Downloads', 'Persepolis')

    # set dark fusion for default style settings.
    style = 'Fusion'
    color_scheme = 'Dark Fusion'
    icons = 'Papirus'
    style = 'Fusion'

    # find available styles(It's depends on operating system and desktop environments).
    available_styles = QStyleFactory.keys()
    if os_type in OS.UNIX_LIKE:
        if desktop_env in ['kde', 'lxqt', 'paperde', 'plainde', 'thedesk', 'lumina']:
            style = 'System'
            color_scheme = 'System'
        else:
            if 'Breeze' in available_styles:
                style = 'Breeze'
                color_scheme = 'System'
            elif 'Adwaita' in available_styles:
                style = 'Adwaita'
                color_scheme = 'System'
            else:
                style = 'Fusion'
                color_scheme = 'Dark Fusion'

    elif os_type == OS.OSX:
        if 'macOS' in available_styles:
            style = 'macOS'
            color_scheme = 'System'

    elif os_type == OS.WINDOWS:
        if 'windows11' in available_styles:
            style = 'windows11'
            color_scheme = 'System'

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
                            'show-menubar': 'no', 'show-sidepanel': 'yes', 'notification': 'QT notification', 'after-dialog': 'yes',
                            'tray-icon': 'yes', 'browser-persepolis': 'yes', 'hide-window': 'yes', 'max-tries': 5, 'retry-wait': 5, 'timeout': 10,
                            'connections': 64, 'download_path': download_path, 'sound': 'yes', 'sound-volume': 100, 'chunk-size': 100,
                            'style': style, 'color-scheme': color_scheme, 'icons': icons, 'font': 'Ubuntu', 'font-size': 9,
                            'video_finder/max_links': '3', 'shortcuts/delete_shortcut': delete_shortcut, 'shortcuts/remove_shortcut': remove_shortcut,
                            'shortcuts/add_new_download_shortcut': add_new_download_shortcut, 'shortcuts/import_text_shortcut': import_text_shortcut,
                            'shortcuts/video_finder_shortcut': video_finder_shortcut, 'shortcuts/quit_shortcut': quit_shortcut,
                            'shortcuts/hide_window_shortcut': hide_window_shortcut, 'shortcuts/move_up_selection_shortcut': move_up_selection_shortcut,
                            'shortcuts/move_down_selection_shortcut': move_down_selection_shortcut, 'dont-check-certificate': 'no',
                            'native_messaging/chrome': 'true', 'native_messaging/chromium': 'true', 'native_messaging/firefox': 'true',
                            'native_messaging/brave': 'false', 'native_messaging/librewolf': 'false', 'native_messaging/opera': 'false',
                            'native_messaging/vivaldi': 'false'}

    return default_setting_dict

# mix video and audio that downloads by video finder


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

    # calculate final file size
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
            final_path_plus_name = os.path.join(final_path, final_file_name)

            while os.path.isfile(final_path_plus_name):

                extension_length = len(file_name_split[-1]) + 1

                new_name = final_file_name[0:-extension_length] + \
                    '_' + str(i) + final_file_name[-extension_length:]

                final_path_plus_name = os.path.join(final_path, new_name)
                i = i + 1

            # start muxing
            # find ffmpeg path
            ffmpeg_command, log_list = findExternalAppPath('ffmpeg')

            # run ffmpeg
            command_argument = ['ffmpeg', '-i', video_file_path,
                                '-i', audio_file_path,
                                '-c', 'copy',
                                '-shortest',
                                '-map', '0:v:0',
                                '-map', '1:a:0',
                                '-loglevel', 'error',
                                '-strict', '-2',
                                final_path_plus_name]

            pipe = runApplication(command_argument)

            if pipe.wait() == 0:
                # muxing was finished successfully.
                result_dictionary['error'] = 'no error'

                result_dictionary['final_path'] = final_path_plus_name
                file_size, file_size_unit = humanReadableSize(final_file_size)
                result_dictionary['final_size'] = str(file_size) + ' ' + str(file_size_unit)

            else:
                result_dictionary['error'] = 'ffmpeg error'
                out, ffmpeg_error_message = pipe.communicate()

                result_dictionary['ffmpeg_error_message'] = ffmpeg_error_message.decode('utf-8', 'ignore')

    return result_dictionary


# return version of ffmpeg
def ffmpegVersion():

    # find ffmpeg path
    ffmpeg_command, log_list = findExternalAppPath('ffmpeg')

    # Try to test ffmpeg
    command_argument = [ffmpeg_command, '-version']
    try:
        pipe = runApplication(command_argument)

        if pipe.wait() == 0:
            ffmpeg_is_installed = True
            ffmpeg_output, error = pipe.communicate()
            ffmpeg_output = ffmpeg_output.decode('utf-8')

        else:
            ffmpeg_is_installed = False
            ffmpeg_output = 'ffmpeg is not installed'
    except Exception:
        ffmpeg_is_installed = False
        ffmpeg_output = 'ffmpeg is not installed'

    # wrap ffmpeg_output with width=70
    wrapper = textwrap.TextWrapper()
    ffmpeg_output = wrapper.fill(ffmpeg_output)

    ffmpeg_output = '\n**********\n'\
        + str(ffmpeg_output)\
        + '\n**********\n'

    return ffmpeg_is_installed, ffmpeg_output, log_list


# run apllication with qprocess
def qRunApplication(command: str, command_argument: list, parent=None):

    process = QProcess(parent=parent)
    process.start(command, command_argument)
    return process

# run an application


def runApplication(command_argument):
    if os_type == OS.WINDOWS:

        # NO_WINDOW option avoids opening additional CMD in MS Windows.
        NO_WINDOW = 0x08000000
        pipe = subprocess.Popen(command_argument,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                stdin=subprocess.PIPE,
                                shell=False,
                                creationflags=NO_WINDOW)

    else:
        pipe = subprocess.Popen(
            command_argument,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False)

    return pipe

# find exeternal application execution path


def findExternalAppPath(app_name):

    # get Persepolis type information first.
    persepolis_path_infromation = getExecPath()
    is_bundle = persepolis_path_infromation['bundle']
    is_test = persepolis_path_infromation['test']

    if os_type == OS.WINDOWS:
        app_name = app_name + '.exe'

    # If Persepolis run as a bundle.
    if is_bundle:

        # alongside of the bundle path
        cwd = sys.argv[0]
        current_directory = os.path.dirname(cwd)
        app_alongside = os.path.join(current_directory, app_name)

        # inside of the bundle path.
        if os_type in OS.UNIX_LIKE:
            # we use nuikita for creating bundle
            bundle_path = os.path.dirname(sys.executable)
            app_inside = os.path.join(bundle_path, app_name)
        else:
            # we use pyinstaller for creating bundle
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            app_inside = os.path.join(base_path, app_name)

        if os_type in OS.UNIX_LIKE:
            # Check outside of the bundle first.
            if os.path.exists(app_alongside):

                app_command = app_alongside
                log_list = ["{}'s file is detected alongside of bundle.".format(app_name), "INFO"]

            # Check inside of the bundle.
            elif os.path.exists(app_inside):
                # get executable pathAdd commentMore actions
                app_command = app_inside
                log_list = ["{}'s file is detected inside of bundle.".format(app_name), "INFO"]

            else:
                # use app that installed on user's system
                app_command = app_name
                log_list = ["Persepolis will use {} that installed on user's system.".format(app_name), "INFO"]

        else:

            # for Mac OSX and MicroSoft Windows
            app_command = app_alongside
            log_list = ["{}'s file is detected alongside of bundle.".format(app_name), "INFO"]

    # I Persepolis run from test directory.
    if is_test:

        # Check inside of test directory.
        cwd = sys.argv[0]
        current_directory = os.path.dirname(cwd)
        app_alongside = os.path.join(current_directory, app_name)

        if os.path.exists(app_alongside):

            app_command = app_alongside
            log_list = ["{}'s file is detected inside of test directory.".format(app_name), "INFO"]

        else:
            # use app that installed on user's system
            app_command = app_name
            log_list = ["Persepolis will use {} that installed on user's system.".format(app_name), "INFO"]

    if not (is_bundle) and not (is_test):

        app_command = app_name
        log_list = ["Persepolis will use {} that installed on user's system.".format(app_name), "INFO"]

    return app_command, log_list


# This function returns persepolis's execution path.
def getExecPath():

    exec_dictionary = {'bundle': None,
                       'test': False,
                       'exec_file_path': None,
                       'modified_exec_file_path': None}

    # check if persepolis is run as a bundle.
    # On Windows and Mac we use pyinstaller to build the bundle,
    # and on Linux and BSD we use nuitka.
    # the output of this code for pyinstaller bundle is True
    # getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
    # But this code doesn't work for nuitka!
    # So we have to use a workaround to identify nuitka bundle.
    # We check the inside of the bundle and look for the
    # com.github.persepolisdm.persepolis.svg file(icon).
    # file that we placed. If it was, then the bundle file
    # generated with nuitka is running.
    if os_type in OS.UNIX_LIKE:
        bundle_path = os.path.dirname(sys.executable)
        icon_file_path = os.path.join(bundle_path, 'com.github.persepolisdm.persepolis.svg')

        # check availability of com.github.persepolisdm.persepolis.svg
        if os.path.exists(icon_file_path):
            exec_dictionary['bundle'] = True

            # for nuitka
            # get executable path
            bundle_path = os.path.abspath(sys.argv[0])

            exec_file_path = bundle_path

    # for windows and osx(pyinstaller bundle)
    else:
        # check pyinstaller bundle
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            exec_dictionary['bundle'] = True
            # get executable path
            bundle_path = os.path.dirname(sys.executable)

            # get bundle name
            bundle_name = os.path.basename(sys.executable)

            exec_file_path = os.path.join(bundle_path, bundle_name)

    if exec_dictionary['bundle'] is not True:

        # persepolis is run from python script
        exec_dictionary['bundle'] = False

        # get execution path
        script_path = os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__))
        script_name = os.path.basename(sys.argv[0])

        if script_name == 'test.py':

            # persepolis is run from test directory
            exec_dictionary['test'] = True

        exec_file_path = os.path.join(script_path, script_name)

    # replace space with \+space for UNIX_LIKE and OSX
    if os_type in OS.UNIX_LIKE or os_type == OS.OSX:

        modified_exec_file_path = exec_file_path.replace(" ", r"\ ")

    elif os_type == OS.WINDOWS:
        modified_exec_file_path = exec_file_path.replace('\\', r'\\')

    # write it in dictionary
    exec_dictionary['exec_file_path'] = exec_file_path
    exec_dictionary['modified_exec_file_path'] = modified_exec_file_path

    # return ressults
    return exec_dictionary


# This method returns data and time in string format
# for example >> 2017/09/09 , 13:12:26
def nowDate():
    date = time.strftime("%Y/%m/%d , %H:%M:%S")
    return date


def fold(header):
    line = "%s: %s" % (header[0], header[1])
    if len(line) < 998:
        return line
    # fold
    else:
        lines = [line]
        while len(lines[-1]) > 998:
            split_this = lines[-1]
            # find last space in longest chunk admissible
            split_here = split_this[:998].rfind(" ")
            del lines[-1]
            lines = lines + [split_this[:split_here],
                             split_this[split_here:]]  # this may still be too long
        # hence the while on lines[-1]
        return "\n".join(lines)


def dictToHeader(data):
    return "\n".join((fold(header) for header in data.items()))


# this method get http header as string and convert it to dictionary
def headerToDict(headers):
    dic = {}
    for line in headers.split("\n"):
        if line.startswith(("GET", "POST")):
            continue
        point_index = line.find(":")
        dic[line[:point_index].strip()] = line[point_index + 1:].strip()

    return dic


def readCookieJar(load_cookies):
    jar = None
    if os.path.isfile(load_cookies):
        # Open cookie file
        cookies_txt = open(load_cookies, 'r')

        # Initialize RequestsCookieJar
        jar = requests.cookies.RequestsCookieJar()

        for line in cookies_txt.readlines():
            words = line.split()

            # Filter out lines that don't contain cookies
            if (len(words) == 7) and (words[0] != "#"):
                # Split cookies into the appropriate parameters
                jar.set(words[5], words[6], domain=words[0], path=words[2])

        return jar


# get file name from link string
def getFileNameFromLink(link):
    link = requests.utils.unquote(link)
    parsed_linkd = urllib.parse.urlparse(link)
    file_name = Path(parsed_linkd.path).name

    return file_name


# Return a new name for the file, if a file with the current name exists.
def returnNewFileName(folder_path, file_name):
    i = 1
    file_path = os.path.join(folder_path, file_name)

    # If file is already exists.
    while os.path.isfile(file_path):
        # split file name to file_name + extension
        file_name_split = list(os.path.splitext(file_name))

        # add _i to the end of file name

        if file_name_split[0][-2] == '_':
            try:
                # check the last character of file_name.
                # If it's integer, add 1 to it.
                j = file_name_split[0][-1]

                j = int(j)
                j += 1
                file_name = file_name_split[0][:-1] + str(j) + file_name_split[-1]
            except Exception:
                file_name = file_name_split[0] + '_' + str(i) + file_name_split[-1]
                i += 1
        else:
            file_name = file_name_split[0] + '_' + str(i) + file_name_split[-1]
            i += 1

        # create new file_path
        file_path = os.path.join(folder_path, file_name)

    return file_name
