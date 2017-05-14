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

from newopen import Open, readList, writeList, readDict
from src.gui.after_download_ui import AfterDownloadWindow_Ui
from PyQt5 import QtCore
from PyQt5.QtCore import QSize, QPoint
import os
import ast
from play import playNotification
import osCommands
import platform

os_type = platform.system()

home_address = os.path.expanduser("~")

# config_folder
if os_type == 'Linux' or os_type == 'FreeBSD' or os_type == 'OpenBSD':
    config_folder = os.path.join(
        str(home_address), ".config/persepolis_download_manager")
elif os_type == 'Darwin':
    config_folder = os.path.join(
        str(home_address), "Library/Application Support/persepolis_download_manager")
elif os_type == 'Windows':
    config_folder = os.path.join(
        str(home_address), 'AppData', 'Local', 'persepolis_download_manager')


class AfterDownloadWindow(AfterDownloadWindow_Ui):
    def __init__(self, download_info_file_list, persepolis_setting):
        super().__init__(persepolis_setting)
        self.persepolis_setting = persepolis_setting
        self.download_info_file_list = download_info_file_list
# connecting buttons
        self.open_pushButtun.clicked.connect(self.openFile)
        self.open_folder_pushButtun.clicked.connect(self.openFolder)
        self.ok_pushButton.clicked.connect(self.okButtonPressed)

# labels
        add_link_dictionary = self.download_info_file_list[9]
        final_download_path = add_link_dictionary['final_download_path']
        save_as = final_download_path
        self.save_as_lineEdit.setText(save_as)
        self.save_as_lineEdit.setToolTip(save_as)
        link = str(add_link_dictionary['link'])
        self.link_lineEdit.setText(link)
        self.link_lineEdit.setToolTip(link)
        file_name = "<b>File name</b> : " + \
            str(self.download_info_file_list[0])
        self.file_name_label.setText(file_name)
        self.setWindowTitle(str(self.download_info_file_list[0]))

        size = "<b>Size</b> : " + str(download_info_file_list[2])
        self.size_label.setText(size)
# play notifications
        cwd = os.path.abspath(__file__)
        scripts_path = os.path.dirname(cwd)
        src_path = os.path.dirname(scripts_path)
        notifications_path = os.path.join(src_path, 'notifications', 'ok.ogg')

        playNotification(str(notifications_path))

# disabling link_lineEdit and save_as_lineEdit
        self.link_lineEdit.setEnabled(False)
        self.save_as_lineEdit.setEnabled(False)

 # setting window size and position
        size = self.persepolis_setting.value(
            'AfterDownloadWindow/size', QSize(570, 290))
        position = self.persepolis_setting.value(
            'AfterDownloadWindow/position', QPoint(300, 300))
        self.resize(size)
        self.move(position)

    def openFile(self):
        # executing file
        add_link_dictionary = self.download_info_file_list[9]
        file_path = add_link_dictionary['file_path']

        if os.path.isfile(file_path):
            osCommands.xdgOpen(file_path)

        self.close()

    def openFolder(self):
        # open download folder
        add_link_dictionary = self.download_info_file_list[9]
        file_path = add_link_dictionary['file_path']

        file_name = os.path.basename(file_path)

        file_path_split = file_path.split(file_name)

        del file_path_split[-1]

        download_path = file_name.join(file_path_split)

        if os.path.isdir(download_path):
            osCommands.xdgOpen(download_path)
        self.close()

    def okButtonPressed(self):
        if self.dont_show_checkBox.isChecked() == True:
            self.persepolis_setting.setValue('settings/after-dialog', 'no')
            self.persepolis_setting.sync()
        self.close()

    def closeEvent(self, event):
        # saving window size and position
        self.persepolis_setting.setValue(
            'AfterDownloadWindow/size', self.size())
        self.persepolis_setting.setValue(
            'AfterDownloadWindow/position', self.pos())
        self.persepolis_setting.sync()

        self.destroy()
