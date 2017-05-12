
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
from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtGui import QIcon
import ast
import os
from src.scripts.newopen import Open

home_address = os.path.expanduser("~")


class ProgressWindow_Ui(QWidget):
    def __init__(self, persepolis_setting):
        super().__init__()
        self.persepolis_setting = persepolis_setting
        icons = ':/' + str(persepolis_setting.value('settings/icons')) + '/'

# window
        self.setMinimumSize(QtCore.QSize(595, 284))

        self.setWindowIcon(QIcon.fromTheme('persepolis', QIcon(':/icon.svg')))
        self.setWindowTitle("Persepolis Download Manager")

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.verticalLayout = QtWidgets.QVBoxLayout()
# progress_tabWidget
        self.progress_tabWidget = QtWidgets.QTabWidget(self)
# informations_tab
        self.informations_tab = QWidget()
        self.informations_verticalLayout = QtWidgets.QVBoxLayout(
            self.informations_tab)
# link_label
        self.link_label = QtWidgets.QLabel(self.informations_tab)
        self.informations_verticalLayout.addWidget(self.link_label)

# status_label
        self.status_label = QtWidgets.QLabel(self.informations_tab)
        self.informations_verticalLayout.addWidget(self.status_label)
# downloaded_label
        self.downloaded_label = QtWidgets.QLabel(self.informations_tab)
        self.informations_verticalLayout.addWidget(self.downloaded_label)
# save_label
        self.save_label = QtWidgets.QLabel(self.informations_tab)
        self.informations_verticalLayout.addWidget(self.save_label)
# rate_label
        self.rate_label = QtWidgets.QLabel(self.informations_tab)
        self.informations_verticalLayout.addWidget(self.rate_label)
# time_label
        self.time_label = QtWidgets.QLabel(self.informations_tab)
        self.informations_verticalLayout.addWidget(self.time_label)

        self.connections_label = QtWidgets.QLabel(self.informations_tab)
        self.informations_verticalLayout.addWidget(self.connections_label)

        self.progress_tabWidget.addTab(self.informations_tab, "")
# options_tab
        self.options_tab = QtWidgets.QWidget()
        self.widget = QtWidgets.QWidget(self.options_tab)
        self.widget.setGeometry(QtCore.QRect(30, 7, 511, 151))

        self.options_gridLayout = QtWidgets.QGridLayout(self.widget)
        self.options_gridLayout.setContentsMargins(0, 0, 0, 0)
# limit_checkBox
        self.limit_checkBox = QtWidgets.QCheckBox(self.widget)
        self.options_gridLayout.addWidget(self.limit_checkBox, 0, 0, 1, 1)
# after_checkBox
        self.after_checkBox = QtWidgets.QCheckBox(self.widget)
        self.options_gridLayout.addWidget(self.after_checkBox, 0, 1, 1, 1)
# limit_frame
        self.limit_frame = QtWidgets.QFrame(self.widget)
        self.limit_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.limit_frame.setFrameShadow(QtWidgets.QFrame.Raised)

        self.widget1 = QtWidgets.QWidget(self.limit_frame)
        self.widget1.setGeometry(QtCore.QRect(44, 27, 151, 62))
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widget1)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
# limit_spinBox
        self.limit_spinBox = QtWidgets.QSpinBox(self.widget1)
        self.limit_spinBox.setMinimum(1)
        self.limit_spinBox.setMaximum(1023)
        self.horizontalLayout.addWidget(self.limit_spinBox)
# limit_comboBox
        self.limit_comboBox = QtWidgets.QComboBox(self.widget1)
        self.limit_comboBox.addItem("")
        self.limit_comboBox.addItem("")
        self.horizontalLayout.addWidget(self.limit_comboBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
# limit_pushButton
        self.limit_pushButton = QtWidgets.QPushButton(self.widget1)
        self.verticalLayout_2.addWidget(self.limit_pushButton)
        self.options_gridLayout.addWidget(self.limit_frame, 1, 0, 1, 1)
# after_frame
        self.after_frame = QtWidgets.QFrame(self.widget)
        self.after_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.after_frame.setFrameShadow(QtWidgets.QFrame.Raised)
# after_comboBox
        self.widget = QtWidgets.QWidget(self.after_frame)
        self.widget.setGeometry(QtCore.QRect(77, 28, 150, 60))

        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)

        self.after_comboBox = QtWidgets.QComboBox(self.after_frame)
        self.after_comboBox.setGeometry(QtCore.QRect(73, 46, 111, 26))
        self.after_comboBox.addItem("")

        self.verticalLayout_3.addWidget(self.after_comboBox)
# after_pushButton
        self.after_pushButton = QtWidgets.QPushButton(self.widget)
        self.verticalLayout_3.addWidget(self.after_pushButton)

        self.options_gridLayout.addWidget(self.after_frame, 1, 1, 1, 1)
        self.progress_tabWidget.addTab(self.options_tab, "")
        self.verticalLayout.addWidget(self.progress_tabWidget)


# download_progressBar
        self.download_progressBar = QtWidgets.QProgressBar(self)
        self.verticalLayout.addWidget(self.download_progressBar)

        self.button_horizontalLayout = QtWidgets.QHBoxLayout()
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.button_horizontalLayout.addItem(spacerItem)
# resume_pushButton
        self.resume_pushButton = QtWidgets.QPushButton(self)
        self.button_horizontalLayout.addWidget(self.resume_pushButton)
        self.resume_pushButton.setIcon(QIcon(icons + 'play'))
# pause_pushButton
        self.pause_pushButton = QtWidgets.QPushButton(self)
        self.button_horizontalLayout.addWidget(self.pause_pushButton)
        self.pause_pushButton.setIcon(QIcon(icons + 'pause'))
# stop_pushButton
        self.stop_pushButton = QtWidgets.QPushButton(self)
        self.button_horizontalLayout.addWidget(self.stop_pushButton)
        self.verticalLayout.addLayout(self.button_horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.stop_pushButton.setIcon(QIcon(icons + 'stop'))

        self.progress_tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)
# labels
        self.link_label.setText("Link :")
        self.status_label.setText("Status : ")
        self.downloaded_label.setText("Downloaded :")
        self.save_label.setText("Save as : ")
        self.rate_label.setText("Transfer rate : ")
        self.time_label.setText("Estimate time left :")
        self.connections_label.setText("Number of connections : ")
        self.progress_tabWidget.setTabText(self.progress_tabWidget.indexOf(
            self.informations_tab),  "Download informations")
        self.limit_checkBox.setText("Limit Speed")
        self.after_checkBox.setText("After download")
        self.limit_comboBox.setItemText(0,  "KB/S")
        self.limit_comboBox.setItemText(1,  "MB/S")
        self.limit_pushButton.setText("Apply")

        self.after_comboBox.setItemText(0,  "Shut Down")

        self.progress_tabWidget.setTabText(
            self.progress_tabWidget.indexOf(self.options_tab),  "Download Options")
        self.resume_pushButton.setText("Resume")
        self.pause_pushButton.setText("Pause")
        self.stop_pushButton.setText("Stop")
        self.after_pushButton.setText("Apply")

    def changeIcon(self, icons):
        icons = ':/' + str(icons) + '/'

        self.resume_pushButton.setIcon(QIcon(icons + 'play'))
        self.pause_pushButton.setIcon(QIcon(icons + 'pause'))
        self.stop_pushButton.setIcon(QIcon(icons + 'stop'))
