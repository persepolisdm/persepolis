
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

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QSizePolicy,  QInputDialog
from PyQt5.QtCore import QSize, QPoint, QThread
from persepolis.gui.progress_ui import ProgressWindow_Ui
import os
import time
import ast
from newopen import Open, readList, writeList, readDict
import download
from bubble import notifySend
import platform
from shutdown import shutDown

os_type = platform.system()

home_address = os.path.expanduser("~")


class ShutDownThread(QThread):
    def __init__(self, gid, password=None):
        QThread.__init__(self)
        self.gid = gid
        self.password = password

    def run(self):
        shutDown(self.gid, self.password)


# persepolis tmp folder (temporary folder)
if os_type != 'Windows':

    user_name_split = home_address.split('/')
    user_name = user_name_split[2]

    persepolis_tmp = '/tmp/persepolis_' + user_name
else:
    persepolis_tmp = os.path.join(
        str(home_address), 'AppData', 'Local', 'persepolis_tmp')


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


download_info_folder = os.path.join(config_folder, "download_info")


class ProgressWindow(ProgressWindow_Ui):
    def __init__(self, parent, gid, persepolis_setting):
        super().__init__(persepolis_setting)
        self.persepolis_setting = persepolis_setting
        self.parent = parent
        self.gid = gid
        self.status = None
        self.resume_pushButton.clicked.connect(self.resumePushButtonPressed)
        self.stop_pushButton.clicked.connect(self.stopPushButtonPressed)
        self.pause_pushButton.clicked.connect(self.pausePushButtonPressed)
        self.download_progressBar.setValue(0)
        self.limit_pushButton.clicked.connect(self.limitPushButtonPressed)

        self.limit_frame.setEnabled(False)
        self.limit_checkBox.toggled.connect(self.limitCheckBoxToggled)

        self.after_frame.setEnabled(False)
        self.after_checkBox.toggled.connect(self.afterCheckBoxToggled)

        self.after_pushButton.clicked.connect(self.afterPushButtonPressed)
# check if limit speed actived by user or not
        download_info_file_list_len = 1
        while download_info_file_list_len != 13:
            download_info_file = download_info_folder + "/" + self.gid
            download_info_file_list = readList(download_info_file)
            download_info_file_list_len = len(download_info_file_list)

        add_link_dictionary = download_info_file_list[9]
        limit = add_link_dictionary['limit']
        if limit != 0:
            limit_number = limit[:-1]
            limit_unit = limit[-1]
            self.limit_spinBox.setValue(int(limit_number))
            if limit_unit == 'K':
                self.after_comboBox.setCurrentIndex(0)
            else:
                self.after_comboBox.setCurrentIndex(1)
            self.limit_checkBox.setChecked(True)

        self.after_comboBox.currentIndexChanged.connect(
            self.afterComboBoxChanged)
        self.limit_comboBox.currentIndexChanged.connect(
            self.limitComboBoxChanged)
        self.limit_spinBox.valueChanged.connect(self.limitComboBoxChanged)

  # setting window size and position
        size = self.persepolis_setting.value(
            'ProgressWindow/size', QSize(595, 274))
        position = self.persepolis_setting.value(
            'ProgressWindow/position', QPoint(300, 300))
        self.resize(size)
        self.move(position)

    def closeEvent(self, event):
        # saving window size and position
        self.persepolis_setting.setValue('ProgressWindow/size', self.size())
        self.persepolis_setting.setValue('ProgressWindow/position', self.pos())
        self.persepolis_setting.sync()

        self.hide()

    def resumePushButtonPressed(self, button):
        if self.status == "paused":
            answer = download.downloadUnpause(self.gid)
# if aria2 did not respond , then this function is checking for aria2
# availability , and if aria2 disconnected then aria2Disconnected is
# executed
            if answer == 'None':
                version_answer = download.aria2Version()
                if version_answer == 'did not respond':
                    self.parent.aria2Disconnected()
                    notifySend("Aria2 disconnected!", "Persepolis is trying to connect!be patient!",
                               10000, 'warning', systemtray=self.parent.system_tray_icon)
                else:
                    notifySend("Aria2 did not respond!", "Try agian!", 10000,
                               'warning', systemtray=self.parent.system_tray_icon)

    def pausePushButtonPressed(self, button):
        if self.status == "downloading":
            answer = download.downloadPause(self.gid)
# if aria2 did not respond , then this function is checking for aria2
# availability , and if aria2 disconnected then aria2Disconnected is
# executed
            if answer == 'None':
                version_answer = download.aria2Version()
                if version_answer == 'did not respond':
                    self.parent.aria2Disconnected()
                    download.downloadStop(self.gid)
                    notifySend("Aria2 disconnected!", "Persepolis is trying to connect!be patient!",
                               10000, 'warning', systemtray=self.parent.system_tray_icon)
                else:
                    notifySend("Aria2 did not respond!", "Try agian!", 10000,
                               'critical', systemtray=self.parent.system_tray_icon)

    def stopPushButtonPressed(self, button):
        answer = download.downloadStop(self.gid)
# if aria2 did not respond , then this function is checking for aria2
# availability , and if aria2 disconnected then aria2Disconnected is
# executed
        if answer == 'None':
            version_answer = download.aria2Version()
            if version_answer == 'did not respond':
                self.parent.aria2Disconnected()
                notifySend("Aria2 disconnected!", "Persepolis is trying to connect!be patient!",
                           10000, 'warning', systemtray=self.parent.system_tray_icon)

    def limitCheckBoxToggled(self, checkBoxes):
        if self.limit_checkBox.isChecked() == True:
            self.limit_frame.setEnabled(True)
            self.limit_pushButton.setEnabled(True)
        else:
            self.limit_frame.setEnabled(False)
            if self.status != 'scheduled':
                download.limitSpeed(self.gid, "0")
            else:
                download_info_file = download_info_folder + '/' + self.gid
                download_info_file_list = readList(download_info_file)
                add_link_dictionary = download_info_file_list[9]
                add_link_dictionary['limit'] = '0'
                download_info_file_list[9] = add_link_dictionary
                writeList(download_info_file, download_info_file_list)

    def limitComboBoxChanged(self, connect):
        self.limit_pushButton.setEnabled(True)

    def afterComboBoxChanged(self, connect):
        self.after_pushButton.setEnabled(True)

    def afterCheckBoxToggled(self, checkBoxes):
        if self.after_checkBox.isChecked() == True:
            self.after_frame.setEnabled(True)
        else:
            self.after_frame.setEnabled(False)
            shutdown_file = os.path.join(persepolis_tmp, 'shutdown', self.gid)
            f = Open(shutdown_file, 'w')
            f.writelines('canceled')
            f.close()

    def afterPushButtonPressed(self, button):
        self.after_pushButton.setEnabled(False)

        if os_type != 'Windows':  # For Linux and Mac OSX and FreeBSD and OpenBSD
            # getting root password
            passwd, ok = QInputDialog.getText(
                self, 'PassWord', 'Please enter root password:', QtWidgets.QLineEdit.Password)
            if ok:
                # checking password
                answer = os.system("echo '" + passwd +
                                   "' |sudo -S echo 'checking passwd'  ")
                while answer != 0:
                    passwd, ok = QInputDialog.getText(
                        self, 'PassWord', 'Wrong Password!\nTry again!', QtWidgets.QLineEdit.Password)
                    if ok:
                        answer = os.system(
                            "echo '" + passwd + "' |sudo -S echo 'checking passwd'  ")
                    else:
                        ok = False
                        break

                if ok != False:
                    # sending password and queue name to shutdown_script
                    # this script is creating a file with name of self.gid in  this folder "persepolis_tmp/shutdown/" . and writing a "wait" word in this file
                    # shutdown_script is checking that file every second . when
                    # "wait" changes to "shutdown" in that file then script is
                    # shutting down system

                    shutdown_enable = ShutDownThread(self.gid, passwd)
                    self.parent.threadPool.append(shutdown_enable)
                    self.parent.threadPool[len(
                        self.parent.threadPool) - 1].start()

                else:
                    self.after_checkBox.setChecked(False)
            else:
                self.after_checkBox.setChecked(False)

        else:  # for Windows
            shutdown_enable = ShutDownThread(self.gid)
            self.parent.threadPool.append(shutdown_enable)
            self.parent.threadPool[len(self.parent.threadPool) - 1].start()

    def limitPushButtonPressed(self, button):
        self.limit_pushButton.setEnabled(False)
        if self.limit_comboBox.currentText() == "KB/S":
            limit = str(self.limit_spinBox.value()) + str("K")
        else:
            limit = str(self.limit_spinBox.value()) + str("M")
# if download was started before , send the limit_speed request to aria2 .
# else save the request in download_information_file
        if self.status != 'scheduled':
            download.limitSpeed(self.gid, limit)
        else:
            download_info_file = os.path.join(download_info_folder, self.gid)
            download_info_file_list = readList(download_info_file)
            add_link_dictionary = download_info_file_list[9]
            add_link_dictionary['limit'] = limit
            download_info_file_list[9] = add_link_dictionary
            writeList(download_info_file, download_info_file_list)
