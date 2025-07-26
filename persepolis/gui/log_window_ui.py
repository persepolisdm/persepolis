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

try:
    from PySide6.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget
    from PySide6.QtCore import Qt, QTranslator, QCoreApplication, QLocale
    from PySide6.QtGui import QIcon
    from PySide6 import QtCore
except ImportError:
    from PyQt5.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget
    from PyQt5.QtCore import Qt, QTranslator, QCoreApplication, QLocale
    from PyQt5.QtGui import QIcon
    from PyQt5 import QtCore

from persepolis.gui import resources


class LogWindow_Ui(QWidget):
    def __init__(self, persepolis_setting):
        super().__init__()

        self.persepolis_setting = persepolis_setting

        # add support for other languages
        locale = str(self.persepolis_setting.value('settings/locale'))
        QLocale.setDefault(QLocale(locale))
        self.translator = QTranslator()
        if self.translator.load(':/translations/locales/ui_' + locale, 'ts'):
            QCoreApplication.installTranslator(self.translator)

        # set ui direction
        ui_direction = self.persepolis_setting.value('ui_direction')

        if ui_direction == 'rtl':
            self.setLayoutDirection(Qt.RightToLeft)

        elif ui_direction in 'ltr':
            self.setLayoutDirection(Qt.LeftToRight)

        icons = ':/' + \
            str(self.persepolis_setting.value('settings/icons')) + '/'

        # finding windows_size
        self.setMinimumSize(QtCore.QSize(620, 300))
        self.setWindowIcon(QIcon.fromTheme('persepolis', QIcon(':/com.github.persepolisdm.persepolis.svg')))

        verticalLayout = QVBoxLayout(self)
        horizontalLayout = QHBoxLayout()
        horizontalLayout.addStretch(1)

        # Define tabwidget
        self.log_tabWidget = QTabWidget(self)
        verticalLayout.addWidget(self.log_tabWidget)

        # Initialization tab
        self.initialization_tab = QWidget()
        initialization_tab_verticalLayout = QVBoxLayout(self.initialization_tab)

        # text_edit
        self.initialization_text_edit = QTextEdit(self.initialization_tab)
        self.initialization_text_edit.setReadOnly(True)

        initialization_tab_verticalLayout.addWidget(self.initialization_text_edit)

        # downloads tab
        self.downloads_tab = QWidget()
        downloads_tab_verticalLayout = QVBoxLayout(self.downloads_tab)

        # text_edit
        self.downloads_text_edit = QTextEdit(self.downloads_tab)
        self.downloads_text_edit.setReadOnly(True)

        downloads_tab_verticalLayout.addWidget(self.downloads_text_edit)

        # errors tab
        self.errors_tab = QWidget()
        errors_tab_verticalLayout = QVBoxLayout(self.errors_tab)

        # text_edit
        self.errors_text_edit = QTextEdit(self.errors_tab)
        self.errors_text_edit.setReadOnly(True)

        errors_tab_verticalLayout.addWidget(self.errors_text_edit)

        self.log_tabWidget.addTab(self.initialization_tab, '')
        self.log_tabWidget.addTab(self.downloads_tab, '')
        self.log_tabWidget.addTab(self.errors_tab, '')

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
        self.close_pushButton.setText(QCoreApplication.translate("log_window_ui_tr", 'Close'))
        self.copy_log_pushButton.setText(QCoreApplication.translate("log_window_ui_tr", 'Copy Selected to Clipboard'))
        self.report_pushButton.setText(QCoreApplication.translate("log_window_ui_tr", "Report Issue"))
        self.refresh_log_pushButton.setText(QCoreApplication.translate("log_window_ui_tr", 'Refresh Log Messages'))
        self.clear_log_pushButton.setText(QCoreApplication.translate("log_window_ui_tr", 'Clear Log Messages'))

        self.log_tabWidget.setTabText(self.log_tabWidget.indexOf(
            self.initialization_tab), QCoreApplication.translate("log_window_ui_tr", "Initialization and information"))
        self.log_tabWidget.setTabText(self.log_tabWidget.indexOf(
            self.downloads_tab), QCoreApplication.translate("log_window_ui_tr", "Downloads"))
        self.log_tabWidget.setTabText(self.log_tabWidget.indexOf(
            self.errors_tab), QCoreApplication.translate("log_window_ui_tr", "Errors and warnings"))
