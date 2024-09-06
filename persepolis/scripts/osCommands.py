#    This program is free software: you can redistribute it and/or modify  # noqa: N999
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
import shutil
import subprocess

from persepolis.constants import Os

os_type = platform.system()
home_address = os.path.expanduser('~')


# this method finds file manager in linux
def findFileManager() -> str:
    pipe = subprocess.check_output(['xdg-mime', 'query', 'default', 'inode/directory'])
    file_manager = pipe.decode('utf-8').strip().lower()

    return file_manager  # noqa: RET504


def touch(file_path: str) -> None:
    if not (os.path.isfile(file_path)):
        f = open(file_path, 'w')  # noqa: SIM115
        f.close()


# xdgOpen opens files or folders
def xdgOpen(file_path: str, f_type: str = 'file', path: str = 'file') -> None:
    # we have a file path and we want to open it's directory.
    # highlit(select) file in file manager after opening.
    # it's help to find file easier :)
    highlight = f_type == 'folder' and path == 'file'

    # for linux and bsd
    if os_type in Os.UNIX_LIKE:
        file_manager = findFileManager()
        # check default file manager.
        # some file managers wouldn't support highlighting.
        if highlight:
            # dolphin is kde plasma's file manager
            if 'dolphin' in file_manager:
                subprocess.Popen(
                    ['dolphin', '--select', file_path],
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    shell=False,
                )

            # dde-file-manager is deepin's file manager
            elif 'dde-file-manager' in file_manager:
                subprocess.Popen(
                    ['dde-file-manager', '--show-item', file_path],
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    shell=False,
                )

            # if file manager is nautilus or nemo or pantheon-file-manager
            elif file_manager in ['org.gnome.nautilus.desktop', 'nemo.desktop', 'io.elementary.files.desktop']:
                # nautilus is gnome's file manager.
                if 'nautilus' in file_manager:
                    file_manager = 'nautilus'

                # pantheon-files is pantheon's file manager(elementary OS).
                elif 'elementary' in file_manager:
                    file_manager = 'io.elementary.files'

                # nemo is cinnamon's file manager.
                elif 'nemo' in file_manager:
                    file_manager = 'nemo'

                subprocess.Popen(
                    [file_manager, file_path],
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    shell=False,
                )

            else:
                # find folder path
                file_name = os.path.basename(str(file_path))

                file_path_split = file_path.split(file_name)

                del file_path_split[-1]

                folder_path = file_name.join(file_path_split)

                subprocess.Popen(
                    ['xdg-open', folder_path],
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    shell=False,
                )

        else:
            subprocess.Popen(
                ['xdg-open', file_path],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=False,
            )

    # for Mac OS X
    elif os_type == Os.OSX:
        if highlight:
            subprocess.Popen(
                ['open', '-R', file_path],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=False,
            )

        else:
            subprocess.Popen(
                ['open', file_path], stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=False
            )

    # for MS Windows
    elif os_type == Os.WINDOWS:
        CREATE_NO_WINDOW = 0x08000000

        if highlight:
            subprocess.Popen(
                ['explorer.exe', '/select,', file_path],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=False,
                creationflags=CREATE_NO_WINDOW,
            )

        else:
            subprocess.Popen(
                ['cmd', '/C', 'start', file_path, file_path],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=False,
                creationflags=CREATE_NO_WINDOW,
            )


# remove file with path of file_path
def remove(file_path: str) -> str:
    if os.path.isfile(file_path):
        try:
            # function returns  ok, if operation was successful
            os.remove(file_path)
            return 'ok'  # noqa: TRY300

        except:
            # function returns this, if operation was not successful
            return 'cant'

    else:
        # function returns this , if file is not existed
        return 'no'


# removeDir removes folder : folder_path
def removeDir(folder_path: str) -> str:
    # check folder_path existence
    if os.path.isdir(folder_path):
        try:
            # remove folder
            shutil.rmtree(folder_path)
            return 'ok'  # noqa: TRY300

        except:
            # return 'cant' if removing was not successful
            return 'cant'
    else:
        # return 'no' if file didn't existed
        return 'no'


# make directory
def makeDirs(folder_path: str, hidden: bool = False) -> str:
    if hidden:
        # create hidden attribute directory.
        if os_type == Os.WINDOWS:
            os.makedirs(folder_path, exist_ok=True)

            # in MS Windows "attrib +h" command hidden directory.
            CREATE_NO_WINDOW = 0x08000000
            subprocess.Popen(
                ['attrib', '+h', folder_path],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=False,
                creationflags=CREATE_NO_WINDOW,
            )
        else:
            # In linux and bsd a dot character must be added in the start of the directory's name
            dir_name = os.path.basename(folder_path)
            dir_name = '.' + dir_name
            folder_path = os.path.join(os.path.dirname(folder_path), dir_name)

            os.makedirs(folder_path, exist_ok=True)
    else:
        os.makedirs(folder_path, exist_ok=True)

    return folder_path


# this function returns mount point
def findMountPoint(path: str) -> str:
    while not os.path.ismount(path):
        path = os.path.dirname(path)

    return path


# move downloaded file to another destination.
def moveFile(old_file_path: str, new_path: str, new_path_type: str = 'folder') -> bool:
    # new_path_type can be file or folder
    # if it's folder so we have folder path
    # else we have new file path that includes file name
    if os.path.isfile(old_file_path):
        check_path = os.path.isdir(new_path) if new_path_type == 'folder' else True

        if check_path:
            try:
                # move file to new_path
                shutil.move(old_file_path, new_path)
                return True  # noqa: TRY300
            except:
                return False
        else:
            return False
    else:
        return False
