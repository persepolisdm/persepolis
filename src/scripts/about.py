# -*- coding: utf-8 -*-
"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import ast
import platform

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, QPoint
from newopen import Open, readDict
import src.gui.icons_resource

home_address = os.path.expanduser("~")

#os_type >> Linux or Darwin(Mac osx) or Windows(Microsoft Windows) or FreeBSD or OpenBSD
os_type = platform.system()

# download manager config folder
if ((os_type == 'Linux') or (os_type == 'FreeBSD') or (os_type == 'OpenBSD')):
    config_folder = os.path.join(
        str(home_address), ".config/persepolis_download_manager")
elif (os_type == 'Darwin'):
    config_folder = os.path.join(
        str(home_address), "Library/Application Support/persepolis_download_manager")
elif (os_type == 'Windows'):
    config_folder = os.path.join(
        str(home_address), 'AppData', 'Local', 'persepolis_download_manager')


class AboutWindow(QWidget):
    def __init__(self,persepolis_setting):
        super().__init__()

        self.persepolis_setting = persepolis_setting

        icons = ':/' + \
            str(self.persepolis_setting.value('settings/icons')) + '/'

        self.setMinimumSize(QtCore.QSize(363, 300))
        self.setWindowIcon(QIcon.fromTheme('persepolis', QIcon(':/icon.svg')))
        self.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.icon_label = QtWidgets.QLabel(self)
        self.icon_label.setMaximumSize(QtCore.QSize(100, 100))
        self.icon_label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.icon_label.setText("")
        self.icon_label.setPixmap(QtGui.QPixmap(":/icon.png"))
        self.icon_label.setScaledContents(True)
        self.icon_label.setAlignment(QtCore.Qt.AlignCenter)
        self.horizontalLayout_2.addWidget(self.icon_label)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.title_label = QtWidgets.QLabel(self)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.title_label.setFont(font)
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.title_label)

        self.version_label = QtWidgets.QLabel(self)
        self.version_label.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.version_label)

        self.name_label = QtWidgets.QLabel(self)
        self.name_label.setAlignment(QtCore.Qt.AlignCenter)
        self.verticalLayout.addWidget(self.name_label)

        self.site2_label = QtWidgets.QLabel(self)
        self.site2_label.setTextFormat(QtCore.Qt.RichText)
        self.site2_label.setAlignment(QtCore.Qt.AlignCenter)
        self.site2_label.setOpenExternalLinks(True)
        self.site2_label.setTextInteractionFlags(
            QtCore.Qt.TextBrowserInteraction)
        self.verticalLayout.addWidget(self.site2_label)

        self.telegram_label = QtWidgets.QLabel(self)
        self.telegram_label.setTextFormat(QtCore.Qt.RichText)
        self.telegram_label.setAlignment(QtCore.Qt.AlignCenter)
        self.telegram_label.setOpenExternalLinks(True)
        self.telegram_label.setTextInteractionFlags(
            QtCore.Qt.TextBrowserInteraction)
        self.verticalLayout.addWidget(self.telegram_label)

        self.twitter_label = QtWidgets.QLabel(self)
        self.twitter_label.setTextFormat(QtCore.Qt.RichText)
        self.twitter_label.setAlignment(QtCore.Qt.AlignCenter)
        self.twitter_label.setOpenExternalLinks(True)
        self.twitter_label.setTextInteractionFlags(
            QtCore.Qt.TextBrowserInteraction)
        self.verticalLayout.addWidget(self.twitter_label)

        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)

        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setIcon(QIcon(icons + 'ok'))
        self.pushButton.clicked.connect(self.close)

        self.horizontalLayout.addWidget(self.pushButton)
        spacerItem1 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        QtCore.QMetaObject.connectSlotsByName(self)

        self.setWindowTitle("About Persepolis")
        self.title_label.setText("Persepolis Download Manager")
        self.version_label.setText("Version 2.4.2")
        self.name_label.setText(
            "\nAliReza AmirSamimi\nMohammadreza Abdollahzadeh\nSadegh Alirezaie\nMostafa Asadi\nMohammadAmin Vahedinia\nJafar Akhondali")
        self.site2_label.setText(
            "<a href=https://persepolisdm.github.io>https://persepolisdm.github.io</a>")
        self.telegram_label.setText(
            "<a href=https://telegram.me/persepolisdm>https://telegram.me/persepolisdm</a>")
        self.twitter_label.setText(
            "<a href=https://twitter.com/persepolisdm>https://twitter.com/persepolisdm</a>")
        self.pushButton.setText("Ok")

# setting window size and position
        size = self.persepolis_setting.value(
            'AboutWindow/size', QSize(363, 300))
        position = self.persepolis_setting.value(
            'AboutWindow/position', QPoint(300, 300))

        self.resize(size)
        self.move(position)

    def changeIcon(self, icons):
        icons = ':/' + str(icons) + '/'
        self.pushButton.setIcon(QIcon(icons + 'ok'))

    def closeEvent(self, event):
        # saving window size and position
        self.persepolis_setting.setValue('AboutWindow/size', self.size())
        self.persepolis_setting.setValue('AboutWindow/position', self.pos())
        self.persepolis_setting.sync()
        self.destroy()
