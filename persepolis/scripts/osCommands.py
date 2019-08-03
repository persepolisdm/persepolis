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

from persepolis.scripts.bubble import notifySend
from PyQt5.QtCore import QCoreApplication, QThread
import subprocess
import platform
import shutil
import os

os_type = platform.system()

class MoveThread(QThread):
    def __init__(self, parent, gid_list, new_folder_path):
        QThread.__init__(self)
        self.new_folder_path = new_folder_path
        self.parent = parent
        self.gid_list = gid_list
        
    def run(self):
        add_link_dict_list = []
        # move selected downloads
        # find row number for specific gid
        for gid in self.gid_list:
            # find download path
            dictionary = self.parent.persepolis_db.searchGidInAddLinkTable(gid)
            self.old_file_path = dictionary['download_path']

            # find file_name
            self.file_name = os.path.basename(self.old_file_path) 

            if os.path.isfile(self.old_file_path) and os.path.isdir(self.new_folder_path):
                try:
                    shutil.move(self.old_file_path, self.new_folder_path) 
                    self.move = True

                except:
                    self.move = False 
            else:
                self.move = False


            if not(self.move):
                notifySend(str(self.file_name), QCoreApplication.translate("mainwindow_src_ui_tr", 'Operation was not successful!'),
                            5000, 'warning', parent=self.parent)
            else:
                new_file_path = os.path.join(self.new_folder_path, self.file_name) 
                add_link_dict = {'gid': gid,
                                'download_path': new_file_path}

                # add add_link_dict to add_link_dict_list
                add_link_dict_list.append(add_link_dict)

        # update data base 
        self.parent.persepolis_db.updateAddLinkTable(add_link_dict_list)

        # notify user that job is done!
        notifySend(QCoreApplication.translate("mainwindow_src_ui_tr", "Moving is"), 
                QCoreApplication.translate("mainwindow_src_ui_tr", 'finished!'),
                5000, 'warning', parent=self.parent)


# this method finds file manager in linux
def findFileManager():
    pipe = subprocess.check_output(['xdg-mime',
                                    'query',
                                  'default',
                                  'inode/directory'])
    file_manager = pipe.decode('utf-8').strip().lower()

    return file_manager

def touch(file_path):
    if not(os.path.isfile(file_path)):
        f = open(file_path, 'w')
        f.close()

# xdgOpen opens files or folders
def xdgOpen(file_path, f_type='file', path='file'):

    # we have a file path and we want to open it's directory.
    # highlit(select) file in file manager after opening.
    # it's help to find file easier :)
    if f_type == 'folder' and path == 'file':
        highlight = True
    else:
        highlight = False

    # for linux and bsd
    if os_type == 'Linux' or os_type == 'FreeBSD' or os_type == 'OpenBSD':

        file_manager = findFileManager()
        # check default file manager.
        # some file managers wouldn't support highlighting.
        if highlight:

            # dolphin is kde plasma's file manager 
            if 'dolphin' in file_manager:

                subprocess.Popen(['dolphin', 
                    '--select', file_path],
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    shell=False)

            # dde-file-manager is deepin's file manager
            elif 'dde-file-manager' in file_manager:

                subprocess.Popen(['dde-file-manager', 
                    '--show-item', file_path],
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    shell=False)

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

                subprocess.Popen([file_manager, 
                    file_path],
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    shell=False)

            else:
                # find folder path
                file_name = os.path.basename(str(file_path))

                file_path_split = file_path.split(file_name)

                del file_path_split[-1]

                folder_path = file_name.join(file_path_split)


                subprocess.Popen(['xdg-open', folder_path],
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    shell=False)

        else:

            subprocess.Popen(['xdg-open', file_path],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=False)
 
    # for Mac OS X
    elif os_type == 'Darwin':
        if highlight:

           subprocess.Popen(['open', '-R', file_path],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=False)

        else:

            subprocess.Popen(['open', file_path],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=False)

    # for MS Windows
    elif os_type == 'Windows':
        CREATE_NO_WINDOW = 0x08000000

        if highlight:
            subprocess.Popen(['cmd', '/C', 'explorer.exe', '/select',  file_path],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=False,
                creationflags=CREATE_NO_WINDOW)

        else:

            subprocess.Popen(['cmd', '/C', 'start', file_path,  file_path],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=False,
                creationflags=CREATE_NO_WINDOW)


def remove(file_path):  # remove file with path of file_path
    if os.path.isfile(file_path):
        try:
            os.remove(file_path)
            return 'ok'  # function returns  this , if opertation was successful
        except:
            return 'cant'  # function returns this , if operation was not successful
    else:
        return 'no'  # function returns this , if file is not existed


def removeDir(folder_path):  # removeDir removes folder : folder_path
    if os.path.isdir(folder_path):  # check folder_path existance
        try:
            shutil.rmtree(folder_path)  # remove folder
            return 'ok'
        except:
            return 'cant'  # return 'cant' if removing was not successful
    else:
        return 'no'  # return 'no' if file didn't existed


def makeDirs(folder_path):  # make new folders
    os.makedirs(folder_path, exist_ok=True)

def moveSelectedFiles(parent, gid_list, new_folder_path):
    move_thread = MoveThread(parent, gid_list, new_folder_path)
    parent.threadPool.append(move_thread)
    parent.threadPool[len(parent.threadPool) - 1].start()
 
# move downloaded file to another destination.
def moveFile(old_file_path, new_folder_path):
    
    if os.path.isfile(old_file_path) and os.path.isdir(new_folder_path):
        try:
            shutil.move(old_file_path, new_folder_path) 
            return 1
        except:
            return 0
    else:
        return 0
