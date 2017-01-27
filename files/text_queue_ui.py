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

from PyQt5 import QtWidgets , QtGui , QtCore
from PyQt5.QtWidgets import QPushButton , QApplication , QWidget , QTabWidget , QVBoxLayout , QTableWidget , QAbstractItemView , QLabel , QLineEdit , QHBoxLayout , QSpinBox , QComboBox , QFrame , QCheckBox , QGridLayout
from PyQt5.QtGui import QIcon
from newopen import Open
import os , ast
import sys

home_address = os.path.expanduser("~")


class TextQueue_Ui(QWidget):
    def __init__(self,persepolis_setting):
        super().__init__()

        self.persepolis_setting = persepolis_setting
        icons = ':/' + str(self.persepolis_setting.value('settings/icons')) + '/'


        self.setWindowIcon(QIcon.fromTheme('persepolis' ,QIcon(':/icon.svg')))
        window_verticalLayout = QVBoxLayout()
        self.setLayout(window_verticalLayout)
#queue_tabWidget
        self.queue_tabWidget = QTabWidget(self)
        window_verticalLayout.addWidget(self.queue_tabWidget)
#links_tab 
        self.links_tab = QWidget()
        links_tab_verticalLayout = QVBoxLayout(self.links_tab)
#link table
        self.links_table = QTableWidget(self.links_tab)
        links_tab_verticalLayout.addWidget(self.links_table)

        self.links_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.links_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.links_table.verticalHeader().hide()

        self.links_table.setColumnCount(3)
        links_table_header_labels = [ 'File Name'  , 'Download Link' , 'dictionary'] 
        self.links_table.setHorizontalHeaderLabels(links_table_header_labels)
        self.links_table.setColumnHidden(2 , True)

        
        self.links_table.horizontalHeader().setSectionResizeMode(0)
        self.links_table.horizontalHeader().setStretchLastSection(True)


#add_queue 
        add_queue_horizontalLayout = QHBoxLayout()

        self.select_all_pushButton = QPushButton(self.links_tab)
        add_queue_horizontalLayout.addWidget(self.select_all_pushButton)

        self.deselect_all_pushButton = QPushButton(self.links_tab)
        add_queue_horizontalLayout.addWidget(self.deselect_all_pushButton)

        add_queue_horizontalLayout.addStretch(1)


        self.add_queue_label = QLabel(self.links_tab)
        add_queue_horizontalLayout.addWidget(self.add_queue_label)

        self.add_queue_comboBox = QComboBox(self.links_tab)
        add_queue_horizontalLayout.addWidget(self.add_queue_comboBox)

        links_tab_verticalLayout.addLayout(add_queue_horizontalLayout)
        self.queue_tabWidget.addTab(self.links_tab , "")


#options_tab
        self.options_tab = QWidget()
        options_tab_verticalLayout = QVBoxLayout(self.options_tab)

#proxy
        proxy_verticalLayout = QVBoxLayout()

        self.proxy_checkBox = QCheckBox(self.options_tab)
        proxy_verticalLayout.addWidget(self.proxy_checkBox)

        self.proxy_frame = QFrame(self.options_tab)
        self.proxy_frame.setFrameShape(QFrame.StyledPanel)
        self.proxy_frame.setFrameShadow(QFrame.Raised)

        proxy_gridLayout = QGridLayout(self.proxy_frame)

        self.ip_lineEdit = QLineEdit(self.proxy_frame)
        self.ip_lineEdit.setInputMethodHints(QtCore.Qt.ImhNone)
        proxy_gridLayout.addWidget(self.ip_lineEdit, 0, 1, 1, 1)

        self.proxy_pass_label = QLabel(self.proxy_frame)
        proxy_gridLayout.addWidget(self.proxy_pass_label, 2, 2, 1, 1)

        self.proxy_pass_lineEdit = QLineEdit(self.proxy_frame)
        self.proxy_pass_lineEdit.setEchoMode(QLineEdit.Password)
        proxy_gridLayout.addWidget(self.proxy_pass_lineEdit, 2, 3, 1, 1)

        self.ip_label = QLabel(self.proxy_frame)
        proxy_gridLayout.addWidget(self.ip_label, 0, 0, 1, 1)

        self.proxy_user_lineEdit = QLineEdit(self.proxy_frame)
        proxy_gridLayout.addWidget(self.proxy_user_lineEdit, 0, 3, 1, 1)

        self.proxy_user_label = QLabel(self.proxy_frame)
        proxy_gridLayout.addWidget(self.proxy_user_label, 0, 2, 1, 1)

        self.port_label = QLabel(self.proxy_frame)
        proxy_gridLayout.addWidget(self.port_label, 2, 0, 1, 1)

        self.port_spinBox = QSpinBox(self.proxy_frame)
        self.port_spinBox.setMaximum(9999)
        self.port_spinBox.setSingleStep(1)
        proxy_gridLayout.addWidget(self.port_spinBox, 2, 1, 1, 1)
        proxy_verticalLayout.addWidget(self.proxy_frame)
        options_tab_verticalLayout.addLayout(proxy_verticalLayout)

#download UserName & Password
        download_horizontalLayout = QHBoxLayout()
        download_horizontalLayout.setContentsMargins(-1, 10, -1, -1)

        download_verticalLayout = QVBoxLayout()
        self.download_checkBox = QCheckBox(self.options_tab)
        download_verticalLayout.addWidget(self.download_checkBox)

        self.download_frame = QFrame(self.options_tab)
        self.download_frame.setFrameShape(QFrame.StyledPanel)
        self.download_frame.setFrameShadow(QFrame.Raised)

        download_gridLayout = QGridLayout(self.download_frame)

        self.download_user_lineEdit = QLineEdit(self.download_frame)
        download_gridLayout.addWidget(self.download_user_lineEdit, 0, 1, 1, 1)

        self.download_user_label = QLabel(self.download_frame)
        download_gridLayout.addWidget(self.download_user_label, 0, 0, 1, 1)

        self.download_pass_label = QLabel(self.download_frame)
        download_gridLayout.addWidget(self.download_pass_label, 1, 0, 1, 1)

        self.download_pass_lineEdit = QLineEdit(self.download_frame)
        self.download_pass_lineEdit.setEchoMode(QLineEdit.Password)
        download_gridLayout.addWidget(self.download_pass_lineEdit, 1, 1, 1, 1)
        download_verticalLayout.addWidget(self.download_frame)
        download_horizontalLayout.addLayout(download_verticalLayout)
#select folder
        self.folder_frame = QFrame(self.options_tab)
        self.folder_frame.setFrameShape(QFrame.StyledPanel)
        self.folder_frame.setFrameShadow(QFrame.Raised)

        folder_gridLayout = QGridLayout(self.folder_frame)

        self.download_folder_lineEdit = QLineEdit(self.folder_frame)
        folder_gridLayout.addWidget(self.download_folder_lineEdit, 2, 0, 1, 1)

        self.folder_pushButton = QPushButton(self.folder_frame)
        folder_gridLayout.addWidget(self.folder_pushButton, 3, 0, 1, 1)
        self.folder_pushButton.setIcon(QIcon(icons + 'folder'))

        self.folder_label = QLabel(self.folder_frame)
        self.folder_label.setAlignment(QtCore.Qt.AlignCenter)
        folder_gridLayout.addWidget(self.folder_label, 1, 0, 1, 1)
        download_horizontalLayout.addWidget(self.folder_frame)
        options_tab_verticalLayout.addLayout(download_horizontalLayout)

        self.queue_tabWidget.addTab(self.options_tab , '')


#limit Speed
        limit_verticalLayout = QVBoxLayout()

        self.limit_checkBox = QCheckBox(self.options_tab)
        limit_verticalLayout.addWidget(self.limit_checkBox)

        self.limit_frame = QFrame(self.options_tab)
        self.limit_frame.setFrameShape(QFrame.StyledPanel)
        self.limit_frame.setFrameShadow(QFrame.Raised)

        limit_horizontalLayout = QHBoxLayout(self.limit_frame)

        self.limit_spinBox = QSpinBox(self.limit_frame)
        self.limit_spinBox.setMinimum(1)
        self.limit_spinBox.setMaximum(1023)
        limit_horizontalLayout.addWidget(self.limit_spinBox)

        self.limit_comboBox = QComboBox(self.limit_frame)
        self.limit_comboBox.addItem("KB/S")
        self.limit_comboBox.addItem("MB/S")
        limit_horizontalLayout.addWidget(self.limit_comboBox)

        limit_verticalLayout.addWidget(self.limit_frame)

        limit_connections_horizontalLayout = QHBoxLayout()
        limit_connections_horizontalLayout.addLayout(limit_verticalLayout)


#number of connections
        connections_horizontalLayout = QHBoxLayout()
        connections_horizontalLayout.setContentsMargins(-1, 10, -1, -1)

        self.connections_frame = QFrame(self.options_tab)
        self.connections_frame.setFrameShape(QFrame.StyledPanel)
        self.connections_frame.setFrameShadow(QFrame.Raised)

        horizontalLayout_3 = QHBoxLayout(self.connections_frame)
        self.connections_label = QLabel(self.connections_frame)
        horizontalLayout_3.addWidget(self.connections_label)

        self.connections_spinBox = QSpinBox(self.connections_frame)
        self.connections_spinBox.setMinimum(1)
        self.connections_spinBox.setMaximum(16)
        self.connections_spinBox.setProperty("value", 16)

        horizontalLayout_3.addWidget(self.connections_spinBox)
        connections_horizontalLayout.addWidget(self.connections_frame)

        limit_connections_horizontalLayout.addLayout(connections_horizontalLayout)

        options_tab_verticalLayout.addLayout(limit_connections_horizontalLayout)


#buttons 
        buttons_horizontalLayout = QHBoxLayout()
        buttons_horizontalLayout.addStretch(1)
#ok_pushButton
        self.ok_pushButton = QPushButton(self)
        self.ok_pushButton.setIcon(QIcon(icons + 'ok'))
        buttons_horizontalLayout.addWidget(self.ok_pushButton)
#cancel_pushButton
        self.cancel_pushButton = QPushButton(self)
        self.cancel_pushButton.setIcon(QIcon(icons + 'remove'))
        buttons_horizontalLayout.addWidget(self.cancel_pushButton)

        window_verticalLayout.addLayout(buttons_horizontalLayout)

#labels
        self.setWindowTitle("Persepolis Download Manager")

        self.queue_tabWidget.setTabText(self.queue_tabWidget.indexOf(self.links_tab) , 'Links' )
        self.queue_tabWidget.setTabText(self.queue_tabWidget.indexOf(self.options_tab) , 'Download options')

        self.select_all_pushButton.setText('Select All')
        self.deselect_all_pushButton.setText('Deselect All')

        self.add_queue_label.setText('Add to queue : ')

        self.proxy_checkBox.setText('Proxy')
        self.proxy_pass_label.setText( "Proxy PassWord : ")
        self.ip_label.setText( "IP  :")
        self.proxy_user_label.setText( "Proxy UserName : ")
        self.port_label.setText( "Port:")

        self.download_checkBox.setText( "Download UserName and PassWord")
        self.download_user_label.setText( "Download UserName : ")
        self.download_pass_label.setText( "Download PassWord : ")

        self.folder_pushButton.setText( "Change Download Folder")
        self.folder_label.setText( "Download Folder : ")

        self.limit_checkBox.setText( "Limit Speed")

        self.connections_label.setText( "Number Of Connections :")

        self.ok_pushButton.setText('OK')
        self.cancel_pushButton.setText('Cancel')


    def changeIcon(self , icons ):
        icons = ':/' + str(icons) + '/'

        self.ok_pushButton.setIcon(QIcon(icons + 'ok'))
        self.cancel_pushButton.setIcon(QIcon(icons + 'remove'))
        self.folder_pushButton.setIcon(QIcon(icons + 'folder'))

