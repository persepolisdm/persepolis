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

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtGui import QIcon
from persepolis.gui import icons_resource
from PyQt5.QtCore import QTranslator, QCoreApplication
import pkg_resources



class LogWindow_Ui(QWidget):
    def __init__(self,persepolis_setting):
        super().__init__()

        self.persepolis_setting = persepolis_setting
        # add support for other languages
        # a) detect current value of locale in persepolis config file
        if str(self.persepolis_setting.value('settings/locale')) in (-1, 'en_US'):
            locale_dir = ''
        else:
            locale_dir = 'locales/' + str(self.persepolis_setting.value('settings/locale')) + '/ui.qm'
        locale_path = pkg_resources.resource_filename(__name__, locale_dir)
        # b) set translator to Qtranslator
        self.translator = QTranslator()
        self.translator.load(locale_path)
        QCoreApplication.installTranslator(self.translator)


        icons = ':/' + \
            str(self.persepolis_setting.value('settings/icons')) + '/'

# finding windows_size
        self.setMinimumSize(QtCore.QSize(620, 300))
        self.setWindowIcon(QIcon.fromTheme('persepolis', QIcon(':/persepolis.svg')))

        verticalLayout = QVBoxLayout(self)
        horizontalLayout = QHBoxLayout()
        horizontalLayout.addStretch(1)

# text_edit
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)

        verticalLayout.addWidget(self.text_edit)

# clear_log_pushButton
        self.clear_log_pushButton = QPushButton(self)
        horizontalLayout.addWidget(self.clear_log_pushButton)

# refresh_log_pushButton
        self.refresh_log_pushButton = QPushButton(self)
        self.refresh_log_pushButton.setIcon(QIcon(icons + 'refresh'))
        horizontalLayout.addWidget(self.refresh_log_pushButton)

# report_pushButton
        self.report_pushButton = QPushButton(self)
        self.report_pushButton.setIcon(QIcon(icons + 'about'))
        horizontalLayout.addWidget(self.report_pushButton)

        self.copy_log_pushButton = QPushButton(self)

# copy_log_pushButton
        self.copy_log_pushButton.setIcon(QIcon(icons + 'clipboard'))
        horizontalLayout.addWidget(self.copy_log_pushButton)

# close_pushButton
        self.close_pushButton = QPushButton(self)
        self.close_pushButton.setIcon(QIcon(icons + 'remove'))
        horizontalLayout.addWidget(self.close_pushButton)

        verticalLayout.addLayout(horizontalLayout)

# set labels

        self.setWindowTitle(QCoreApplication.translate("log_window_ui_tr", 'Persepolis Log'))
        self.close_pushButton.setText(QCoreApplication.translate("log_window_ui_tr", 'close'))
        self.copy_log_pushButton.setText(QCoreApplication.translate("log_window_ui_tr", 'Copy  selected to clipboard'))
        self.report_pushButton.setText(QCoreApplication.translate("log_window_ui_tr", "Report Issue"))
        self.refresh_log_pushButton.setText(QCoreApplication.translate("log_window_ui_tr", 'Refresh log messages'))
        self.clear_log_pushButton.setText(QCoreApplication.translate("log_window_ui_tr", 'Clear log messages'))
    def changeIcon(self, icons):
        icons = ':/' + str(icons) + '/'

        self.close_pushButton.setIcon(QIcon(icons + 'remove'))
        self.copy_log_pushButton.setIcon(QIcon(icons + 'clipboard'))
        self.report_pushButton.setIcon(QIcon(icons + 'about'))

