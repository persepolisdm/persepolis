# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'about.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QIcon
import ast , os
from newopen import Open
import icons_resource

home_address = os.path.expanduser("~")
config_folder = str(home_address) + "/.config/persepolis_download_manager"

#setting
setting_file = config_folder + '/setting'
f = Open(setting_file)
setting_file_lines = f.readlines()
f.close()
setting_dict_str = str(setting_file_lines[0].strip())
setting_dict = ast.literal_eval(setting_dict_str) 

icons = ':/' + str(setting_dict['icons']) + '/'


class AboutWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowModality(QtCore.Qt.NonModal)
        self.resize(363, 157)
        self.setMinimumSize(QtCore.QSize(363, 157))
        self.setMaximumSize(QtCore.QSize(363, 157))
        self.setWindowIcon(QIcon(':/icon'))
        self.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.icon_label = QtWidgets.QLabel(self)
        self.icon_label.setMaximumSize(QtCore.QSize(100, 100))
        self.icon_label.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.icon_label.setText("")
        self.icon_label.setPixmap(QtGui.QPixmap(":/icon.svg"))
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
        self.site_label = QtWidgets.QLabel(self)
        self.site_label.setTextFormat(QtCore.Qt.RichText)
        self.site_label.setAlignment(QtCore.Qt.AlignCenter)
        self.site_label.setOpenExternalLinks(True)
        self.site_label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.verticalLayout.addWidget(self.site_label)
        self.telegram_label = QtWidgets.QLabel(self)
        self.telegram_label.setTextFormat(QtCore.Qt.RichText)
        self.telegram_label.setAlignment(QtCore.Qt.AlignCenter)
        self.telegram_label.setOpenExternalLinks(True)
        self.telegram_label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.verticalLayout.addWidget(self.telegram_label)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)

        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setIcon(QIcon(icons + 'ok'))
        self.pushButton.clicked.connect(self.close)

        self.horizontalLayout.addWidget(self.pushButton)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        QtCore.QMetaObject.connectSlotsByName(self)

        self.setWindowTitle( "About Persepolis")
        self.title_label.setText( "Persepolis Download Manager")
        self.version_label.setText( "Version 2.0.2 unstable")
        self.name_label.setText( "AliReza AmirSamimi")
        self.site_label.setText("<a href=http://amirsamimi.ir>http://amirsamimi.ir</a>" )
        self.telegram_label.setText( "<a href=https://telegram.me/persepolisdm>https://telegram.me/persepolisdm</a>" )
        self.pushButton.setText( "Ok")

