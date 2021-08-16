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

from PySide6.QtWidgets import QCheckBox, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit
from PySide6.QtCore import Qt, QTranslator, QCoreApplication, QLocale
from persepolis.gui import resources
from PySide6.QtGui import QIcon


class AfterDownloadWindow_Ui(QWidget):
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

        icons = ':/' + str(self.persepolis_setting.value('settings/icons')) + '/'

        self.setWindowIcon(QIcon.fromTheme('persepolis', QIcon(':/persepolis.svg')))
        self.setWindowTitle(QCoreApplication.translate("after_download_ui_tr", "Persepolis Download Manager"))

        # complete_label
        window_verticalLayout = QVBoxLayout()
        window_verticalLayout.setContentsMargins(21, 21, 21, 21)

        self.complete_label = QLabel()
        window_verticalLayout.addWidget(self.complete_label)

        # file_name_label
        self.file_name_label = QLabel()
        window_verticalLayout.addWidget(self.file_name_label)

        # size_label
        self.size_label = QLabel()
        window_verticalLayout.addWidget(self.size_label)

        # link
        self.link_label = QLabel()
        window_verticalLayout.addWidget(self.link_label)

        self.link_lineEdit = QLineEdit()
        window_verticalLayout.addWidget(self.link_lineEdit)

        # save_as
        self.save_as_label = QLabel()
        window_verticalLayout.addWidget(self.save_as_label)
        self.save_as_lineEdit = QLineEdit()
        window_verticalLayout.addWidget(self.save_as_lineEdit)

        # open_pushButtun
        button_horizontalLayout = QHBoxLayout()
        button_horizontalLayout.setContentsMargins(10, 10, 10, 10)

        button_horizontalLayout.addStretch(1)
        self.open_pushButtun = QPushButton()
        self.open_pushButtun.setIcon(QIcon(icons + 'file'))
        button_horizontalLayout.addWidget(self.open_pushButtun)

        # open_folder_pushButtun
        self.open_folder_pushButtun = QPushButton()
        self.open_folder_pushButtun.setIcon(QIcon(icons + 'folder'))
        button_horizontalLayout.addWidget(self.open_folder_pushButtun)

        # ok_pushButton
        self.ok_pushButton = QPushButton()
        self.ok_pushButton.setIcon(QIcon(icons + 'ok'))
        button_horizontalLayout.addWidget(self.ok_pushButton)

        window_verticalLayout.addLayout(button_horizontalLayout)

        # dont_show_checkBox
        self.dont_show_checkBox = QCheckBox()
        window_verticalLayout.addWidget(self.dont_show_checkBox)

        window_verticalLayout.addStretch(1)

        self.setLayout(window_verticalLayout)

        # labels
        self.open_pushButtun.setText(QCoreApplication.translate("after_download_ui_tr", "  Open File  "))
        self.open_folder_pushButtun.setText(QCoreApplication.translate("after_download_ui_tr", "Open Download Folder"))
        self.ok_pushButton.setText(QCoreApplication.translate("after_download_ui_tr", "   OK   "))
        self.dont_show_checkBox.setText(QCoreApplication.translate(
            "after_download_ui_tr", "Don't show this message again."))
        self.complete_label.setText(QCoreApplication.translate("after_download_ui_tr", "<b>Download Completed!</b>"))
        self.save_as_label.setText(QCoreApplication.translate("after_download_ui_tr", "<b>Save as</b>: "))
        self.link_label.setText(QCoreApplication.translate("after_download_ui_tr", "<b>Link</b>: "))
