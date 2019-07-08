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

from PyQt5.QtCore import QSize, QPoint, QThread, QTranslator, QCoreApplication, QLocale
from PyQt5.QtWidgets import QLineEdit, QWidget, QSizePolicy,  QInputDialog
from persepolis.gui.video_finder_progress_ui import VideoFinderProgressWindow_Ui
from persepolis.scripts.shutdown import shutDown
from persepolis.scripts.bubble import notifySend
from persepolis.scripts import download
from PyQt5.QtGui import QIcon
import platform
import time
import os

os_type = platform.system()


class ShutDownThread(QThread):
    def __init__(self, parent, category, password=None):
        QThread.__init__(self)
        self.category = category
        self.password = password
        self.parent = parent

    def run(self):
        shutDown(self.parent, category=self.category, password=self.password)


class VideoFinderProgressWindow(VideoFinderProgressWindow_Ui):
    def __init__(self, parent, gid_list, persepolis_setting):
        super().__init__(persepolis_setting)
        self.persepolis_setting = persepolis_setting
        self.parent = parent

        # first item in the gid_list is related to video's link and second item is related to audio's link.
        self.gid_list = gid_list

        # this variable can be changed by checkDownloadInfo method in mainwindow.py 
        # self.gid defines that wich gid is downloaded. 
        self.gid = gid_list[0]


        # this variable used as category name in ShutDownThread
        self.video_finder_plus_gid = 'video_finder_' + str(gid_list[0])

        # connect signals and sluts 
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

        # add support for other languages
        locale = str(self.persepolis_setting.value('settings/locale'))
        QLocale.setDefault(QLocale(locale))
        self.translator = QTranslator()
        if self.translator.load(':/translations/locales/ui_' + locale, 'ts'):
            QCoreApplication.installTranslator(self.translator)

        # check if limit speed actived by user or not
        add_link_dictionary = self.parent.persepolis_db.searchGidInAddLinkTable(gid_list[0])

        limit = str(add_link_dictionary['limit_value'])
        if limit != '0':
            limit_number = limit[:-1]
            limit_unit = limit[-1]
            self.limit_spinBox.setValue(float(limit_number))
            if limit_unit == 'K':
                self.after_comboBox.setCurrentIndex(0)
            else:
                self.after_comboBox.setCurrentIndex(1)
            self.limit_checkBox.setChecked(True)

        self.after_comboBox.currentIndexChanged.connect(self.afterComboBoxChanged)

        self.limit_comboBox.currentIndexChanged.connect(self.limitComboBoxChanged)

        self.limit_spinBox.valueChanged.connect(self.limitComboBoxChanged)

  # set window size and position
        size = self.persepolis_setting.value(
            'ProgressWindow/size', QSize(595, 274))
        position = self.persepolis_setting.value(
            'ProgressWindow/position', QPoint(300, 300))
        self.resize(size)
        self.move(position)

    def closeEvent(self, event):

        # save window size and position
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
            if not(answer):
                version_answer = download.aria2Version()
                if version_answer == 'did not respond':
                    self.parent.aria2Disconnected()
                    notifySend(QCoreApplication.translate("progress_src_ui_tr", "Aria2 disconnected!"), QCoreApplication.translate("progress_src_ui_tr", "Persepolis is trying to connect! be patient!"),
                               10000, 'warning', parent=self.parent)
                else:
                    notifySend(QCoreApplication.translate("progress_src_ui_tr", "Aria2 did not respond!"), QCoreApplication.translate("progress_src_ui_tr", "Please try again."), 10000,
                               'warning', parent=self.parent)


    def pausePushButtonPressed(self, button):

        if self.status == "downloading":
            answer = download.downloadPause(self.gid)

            # if aria2 did not respond , then this function is checking for aria2
            # availability , and if aria2 disconnected then aria2Disconnected is
            # executed
            if not(answer):
                version_answer = download.aria2Version()
                if version_answer == 'did not respond':
                    self.parent.aria2Disconnected()
                    download.downloadStop(self.gid, self.parent)
                    notifySend("Aria2 disconnected!", "Persepolis is trying to connect! be patient!",
                               10000, 'warning', parent=self.parent)
                else:
                    notifySend(QCoreApplication.translate("progress_src_ui_tr", "Aria2 did not respond!"), QCoreApplication.translate("progress_src_ui_tr", "Try again!"), 10000,
                               'critical', parent=self.parent)

    def stopPushButtonPressed(self, button):
        
        # cancel shut down progress
        dictionary = {'category': self.video_finder_plus_gid,
                'shutdown': 'canceled'}

        self.parent.temp_db.updateQueueTable(dictionary)


        answer = download.downloadStop(self.gid, self.parent)
        
        # if aria2 did not respond , then this function is checking for aria2
        # availability , and if aria2 disconnected then aria2Disconnected is
        # executed
        if answer == 'None':
            version_answer = download.aria2Version()
            if version_answer == 'did not respond':
                self.parent.aria2Disconnected()
                notifySend(QCoreApplication.translate("progress_src_ui_tr", "Aria2 disconnected!"), QCoreApplication.translate("progress_src_ui_tr", "Persepolis is trying to connect! be patient!"),
                           10000, 'warning', parent=self.parent)

    def limitCheckBoxToggled(self, checkBoxes):

        # user checked limit_checkBox
        if self.limit_checkBox.isChecked() == True:
            self.limit_frame.setEnabled(True)
            self.limit_pushButton.setEnabled(True)

        # user unchecked limit_checkBox
        else:
            self.limit_frame.setEnabled(False)

            # check download status is "scheduled" or not!
            for i in [0, 1]:
                gid = self.gid_list[i]
                dictionary = self.parent.persepolis_db.searchGidInDownloadTable(gid) 
                status = dictionary['status']

                if status != 'scheduled':

                    # tell aria2 for unlimiting speed
                    download.limitSpeed(gid, "0")

                else:
                    # update limit value in data_base
                    add_link_dictionary = {'gid': gid, 'limit_value': '0'}
                    self.parent.persepolis_db.updateAddLinkTable([add_link_dictionary])

    def limitComboBoxChanged(self, connect):

        self.limit_pushButton.setEnabled(True)

    def afterComboBoxChanged(self, connect):

        self.after_pushButton.setEnabled(True)

    def afterCheckBoxToggled(self, checkBoxes):

        if self.after_checkBox.isChecked():

            self.after_frame.setEnabled(True)
        else:

            # so user canceled shutdown after download
            # write cancel value in data_base for this gid
            dictionary = {'category': self.video_finder_plus_gid,
                        'shutdown': 'canceled'}

            self.parent.temp_db.updateQueueTable(dictionary)
    
    def afterPushButtonPressed(self, button):

        self.after_pushButton.setEnabled(False)

        # For Linux and Mac OSX and FreeBSD and OpenBSD
        if os_type != 'Windows':  

            # get root password
            passwd, ok = QInputDialog.getText(
                self, 'PassWord', 'Please enter root password:', QLineEdit.Password)

            if ok:
                # check password is true or not!
                answer = os.system("echo '" + passwd +
                                   "' |sudo -S echo 'checking passwd'  ")
                # Wrong password
                while answer != 0:
                    passwd, ok = QInputDialog.getText(
                        self, 'PassWord', 'Wrong Password!\nPlease try again.', QLineEdit.Password)
                    if ok:
                        answer = os.system(
                            "echo '" + passwd + "' |sudo -S echo 'checking passwd'  ")
                    else:
                        ok = False
                        break

                if ok != False:

                    # if user selects shutdown option after download progress, 
                    # value of 'shutdown' will changed in temp_db for this progress
                    # and "wait" word will be written for this value.
                    # (see ShutDownThread and shutdown.py for more information)
                    # shutDown method will check that value in a loop .
                    # when "wait" changes to "shutdown" then shutdown.py script
                    # will shut down the system.

                    shutdown_enable = ShutDownThread(self.parent, self.video_finder_plus_gid, passwd)
                    self.parent.threadPool.append(shutdown_enable)
                    self.parent.threadPool[len(self.parent.threadPool) - 1].start()

                else:
                    self.after_checkBox.setChecked(False)
            else:
                self.after_checkBox.setChecked(False)

        else:  
            # for Windows
            for gid in gid_list:
                shutdown_enable = ShutDownThread(self.parent, self.video_finder_plus_gid)
                self.parent.threadPool.append(shutdown_enable)
                self.parent.threadPool[len(self.parent.threadPool) - 1].start()

    def limitPushButtonPressed(self, button):

        self.limit_pushButton.setEnabled(False)

        if self.limit_comboBox.currentText() == "KiB/s":

            limit_value = str(self.limit_spinBox.value()) + str("K")
        else:
            limit_value = str(self.limit_spinBox.value()) + str("M")

        # if download was started before , send the limit_speed request to aria2 .
        # else save the request in data_base
        for i in [0, 1]:

            gid = self.gid_list[i]
            dictionary = self.parent.persepolis_db.searchGidInDownloadTable(gid)
            status = dictionary['status']

            if status != 'scheduled':

                download.limitSpeed(self.gid, limit_value)
            else:
                # update limit value in data_base
                add_link_dictionary = {'gid': gid, 'limit_value': limit_value}
                self.parent.persepolis_db.updateAddLinkTable([add_link_dictionary])

    def changeIcon(self, icons):
        icons = ':/' + str(icons) + '/'

        self.resume_pushButton.setIcon(QIcon(icons + 'play'))
        self.pause_pushButton.setIcon(QIcon(icons + 'pause'))
        self.stop_pushButton.setIcon(QIcon(icons + 'stop'))
