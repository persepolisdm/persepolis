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
#

from persepolis.scripts.useful_tools import determineConfigFolder
from persepolis.gui.log_window_ui import LogWindow_Ui
from persepolis.scripts import osCommands
from PyQt5.QtCore import QPoint, QSize
from PyQt5.QtGui import QIcon
from PyQt5 import QtWidgets
import os

# config_folder
config_folder = determineConfigFolder()

class LogWindow(LogWindow_Ui):
    def __init__(self, persepolis_setting):
        super().__init__(persepolis_setting)

        self.persepolis_setting = persepolis_setting

        self.copy_log_pushButton.setEnabled(False)

# log file address
        self.log_file = os.path.join(str(config_folder), 'persepolisdm.log')

        f = open(self.log_file, 'r')
        f_lines = f.readlines()
        f.close()

        self.text = 'Log File:\n'
        for line in f_lines:
            self.text = self.text + str(line) + '\n'

        self.text_edit.insertPlainText(self.text)

        self.text_edit.copyAvailable.connect(
            self.copyAvailableSignalHandler)

        self.copy_log_pushButton.clicked.connect(
            self.copyPushButtonPressed)

        self.report_pushButton.clicked.connect(
            self.reportPushButtonPressed)

        self.close_pushButton.clicked.connect(
            self.closePushButtonPressed)

        self.refresh_log_pushButton.clicked.connect(
            self.refreshLogPushButtonPressed)

        self.clear_log_pushButton.clicked.connect(
            self.clearLogPushButtonPressed)

# setting window size and position
        size = self.persepolis_setting.value(
            'LogWindow/size', QSize(720, 300))
        position = self.persepolis_setting.value(
            'LogWindow/position', QPoint(300, 300))
        self.resize(size)
        self.move(position)

        self.minimum_height = self.height()

    def clearLogPushButtonPressed(self, button):
        f = open(self.log_file, 'w')
        f.close()

        self.text = 'Log File:\n'

        self.text_edit.clear()
        self.text_edit.insertPlainText(self.text)



    def reportPushButtonPressed(self, button):
        osCommands.xdgOpen('https://github.com/persepolisdm/persepolis/issues')

    def closePushButtonPressed(self, button):
        self.close()

    def copyAvailableSignalHandler(self, signal):
        if signal:
            self.copy_log_pushButton.setEnabled(True)
        else:
            self.copy_log_pushButton.setEnabled(False)

    def copyPushButtonPressed(self, button):
#         clipboard = QApplication.clipboard()
#         clipboard.setText(self.text)
        self.text_edit.copy()

# this method is refresh log messages in text_edit
    def refreshLogPushButtonPressed(self, button):
        f = open(self.log_file, 'r')
        f_lines = f.readlines()
        f.close()

        self.text = 'Log File:\n'
        for line in f_lines:
            self.text = self.text + str(line) + '\n'

        self.text_edit.clear()
        self.text_edit.insertPlainText(self.text)


    def closeEvent(self, event):
        self.layout().setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.setMinimumSize(QSize(self.width() , self.minimum_height))
        self.resize(QSize(self.width() , self.minimum_height))
 
        self.persepolis_setting.setValue('LogWindow/size', self.size())
        self.persepolis_setting.setValue('LogWindow/position', self.pos())
        self.persepolis_setting.sync()
        event.accept()

    def changeIcon(self, icons):
        icons = ':/' + str(icons) + '/'

        self.close_pushButton.setIcon(QIcon(icons + 'remove'))
        self.copy_log_pushButton.setIcon(QIcon(icons + 'clipboard'))
        self.report_pushButton.setIcon(QIcon(icons + 'about'))
        self.refresh_log_pushButton.setIcon(QIcon(icons + 'refresh'))

