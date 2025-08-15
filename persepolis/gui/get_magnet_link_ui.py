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

from PySide6.QtWidgets import QHBoxLayout, QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QSizePolicy, QSpacerItem
from PySide6.QtCore import Qt, QTranslator, QCoreApplication, QLocale
from PySide6 import QtCore
from PySide6.QtGui import QIcon

from persepolis.gui import resources


class GetMagnetLinkWindow_Ui(QDialog):
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

        # get icons name
        icons = ':/' + \
            str(self.persepolis_setting.value('settings/icons')) + '/'

        self.setMinimumSize(QtCore.QSize(200, 100))
        self.setWindowIcon(QIcon.fromTheme('persepolis', QIcon(':/com.github.persepolisdm.persepolis.svg')))

        self.setWindowTitle(QCoreApplication.translate("get_magnet_link_ui_tr", "Enter Magnet Link"))
        self.setGeometry(100, 100, 300, 150)

        # Create layout
        layout = QVBoxLayout()

        # Create a label
        self.label = QLabel(self)
        layout.addWidget(self.label)

        # Create a QLineEdit for the magnet link
        self.line_edit = QLineEdit(self)
        # Set a minimum width for the QLineEdit
        self.line_edit.setMinimumWidth(350)

        layout.addWidget(self.line_edit)
        # Add spacing between QLineEdit and buttons
        layout.addSpacing(10)  # Add 10 pixels of spacing

        # Create OK and Cancel buttons
        # Create a horizontal layout for the buttons
        button_layout = QHBoxLayout()
        # Create a spacer item to push buttons to the right
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        button_layout.addItem(spacer)

        self.ok_pushButton = QPushButton(self)
        self.ok_pushButton.setIcon(QIcon(icons + 'ok'))

        button_layout.addWidget(self.ok_pushButton)

        self.cancel_pushButton = QPushButton(self)
        self.cancel_pushButton.setIcon(QIcon(icons + 'remove'))

        button_layout.addWidget(self.cancel_pushButton)
        layout.addLayout(button_layout)

        # Set the layout for the dialog
        self.setLayout(layout)

        # Texts
        self.label.setText(QCoreApplication.translate("get_magnet_link_ui_tr", "Please enter the magnet link:"))
        self.label.setAlignment(Qt.AlignCenter)  # Center the text
        self.ok_pushButton.setText(QCoreApplication.translate("get_magnet_link_ui_tr", "OK"))
        self.cancel_pushButton.setText(QCoreApplication.translate("get_magnet_link_ui_tr", "Cancel"))
