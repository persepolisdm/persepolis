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
import os

try:
    from PySide6.QtCore import Qt, QPoint, QSize
    from PySide6.QtGui import QIcon
    from PySide6 import QtWidgets
except ImportError:
    from PyQt5.QtCore import Qt, QPoint, QSize
    from PyQt5.QtGui import QIcon
    from PyQt5 import QtWidgets

# config_folder
config_folder = determineConfigFolder()


class LogWindow(LogWindow_Ui):

    def __init__(self, persepolis_setting):
        super().__init__(persepolis_setting)

        self.persepolis_setting = persepolis_setting

        self.copy_log_pushButton.setEnabled(False)

        # log files address
        self.initialization_log_file = os.path.join(str(config_folder), 'initialization_log_file.log')
        self.downloads_log_file = os.path.join(str(config_folder), 'downloads_log_file.log')
        self.errors_log_file = os.path.join(str(config_folder), 'errors_log_file.log')

        # lists
        self.log_files_list = [self.initialization_log_file, self.downloads_log_file, self.errors_log_file]
        self.text_widgets_list = [self.initialization_text_edit, self.downloads_text_edit, self.errors_text_edit]
        self.tabs_list = [self.initialization_tab, self.downloads_tab, self.errors_tab]

        # Set downloads_tab for current tab
        self.log_tabWidget.setCurrentWidget(self.downloads_tab)

        # read logs
        for index, file in enumerate(self.log_files_list):

            text = ''
            f = open(file, 'r')
            f_lines = f.readlines()
            f.close()

            for line in f_lines:
                text = text + str(line) + '\n'

            self.text_widgets_list[index].insertPlainText(text)

            self.text_widgets_list[index].copyAvailable.connect(
                self.copyAvailableSignalHandler)

        # signals and slots
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
        # Empty log files
        for index, file in enumerate(self.log_files_list):

            # erase files
            f = open(file, 'w')
            f.close()

            # clear text editors
            self.text_widgets_list[index].clear()

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
        # find current active tab
        index = self.log_tabWidget.currentIndex()
        for tab_index, tab in enumerate(self.tabs_list):
            if self.log_tabWidget.indexOf(tab) == index:
                # copy text
                self.text_widgets_list[tab_index].copy()

    # this method is refresh log messages in text_edit
    def refreshLogPushButtonPressed(self, button):
        # read logs
        for index, file in enumerate(self.log_files_list):

            f = open(file, 'r')
            f_lines = f.readlines()
            f.close()

            text = 'Log file:\n'
            for line in f_lines:
                text = text + str(line) + '\n'

            self.text_widgets_list[index].clear()
            self.text_widgets_list[index].insertPlainText(text)

    # close window with ESC key
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def closeEvent(self, event):
        self.layout().setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.setMinimumSize(QSize(self.width(), self.minimum_height))
        self.resize(QSize(self.width(), self.minimum_height))

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
