#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget , QPushButton , QComboBox , QSpinBox ,QVBoxLayout, QHBoxLayout , QLabel , QApplication , QWidget , QFileDialog, QMessageBox , QSizePolicy , QGridLayout , QCheckBox , QFrame , QLineEdit , QPushButton
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

icons =':/' + str(setting_dict['icons']) + '/'



class AddLinkWindow_Ui(QWidget):
    def __init__(self):
        super().__init__()
#window
        self.resize(475, 465)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QtCore.QSize(475, 465))
        self.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.setWindowIcon(QIcon(':/icon'))

        self.widget = QWidget(self)
        self.widget.setGeometry(QtCore.QRect(9, 9, 454, 442))

        self.verticalLayout = QVBoxLayout(self)
 
        self.addlink_verticalLayout = QVBoxLayout()
        self.addlink_verticalLayout.setContentsMargins(0, 0, 0, 0)

        self.link_frame = QFrame(self)
        self.link_frame.setFrameShape(QFrame.StyledPanel)
        self.link_frame.setFrameShadow(QFrame.Raised)

        self.horizontalLayout_2 = QHBoxLayout(self.link_frame)

        self.link_verticalLayout = QVBoxLayout()
#link
        self.link_horizontalLayout = QHBoxLayout() 
        self.link_label = QLabel(self.link_frame)
        self.link_horizontalLayout.addWidget(self.link_label)

        self.link_lineEdit = QLineEdit(self.link_frame)
        self.link_horizontalLayout.addWidget(self.link_lineEdit)

        self.link_verticalLayout.addLayout(self.link_horizontalLayout)

        self.horizontalLayout_2.addLayout(self.link_verticalLayout)
        self.addlink_verticalLayout.addWidget(self.link_frame)

#proxy
        self.proxy_verticalLayout = QVBoxLayout()

        self.proxy_checkBox = QCheckBox(self.widget)
        self.proxy_verticalLayout.addWidget(self.proxy_checkBox)

        self.proxy_frame = QFrame(self.widget)
        self.proxy_frame.setFrameShape(QFrame.StyledPanel)
        self.proxy_frame.setFrameShadow(QFrame.Raised)

        self.gridLayout = QGridLayout(self.proxy_frame)

        self.ip_lineEdit = QLineEdit(self.proxy_frame)
        self.ip_lineEdit.setInputMethodHints(QtCore.Qt.ImhNone)
        self.gridLayout.addWidget(self.ip_lineEdit, 0, 1, 1, 1)

        self.proxy_pass_label = QLabel(self.proxy_frame)
        self.gridLayout.addWidget(self.proxy_pass_label, 2, 2, 1, 1)

        self.proxy_pass_lineEdit = QLineEdit(self.proxy_frame)
        self.proxy_pass_lineEdit.setEchoMode(QLineEdit.Password)
        self.gridLayout.addWidget(self.proxy_pass_lineEdit, 2, 3, 1, 1)

        self.ip_label = QLabel(self.proxy_frame)
        self.gridLayout.addWidget(self.ip_label, 0, 0, 1, 1)

        self.proxy_user_lineEdit = QLineEdit(self.proxy_frame)
        self.gridLayout.addWidget(self.proxy_user_lineEdit, 0, 3, 1, 1)

        self.proxy_user_label = QLabel(self.proxy_frame)
        self.gridLayout.addWidget(self.proxy_user_label, 0, 2, 1, 1)

        self.port_label = QLabel(self.proxy_frame)
        self.gridLayout.addWidget(self.port_label, 2, 0, 1, 1)

        self.port_spinBox = QSpinBox(self.proxy_frame)
        self.port_spinBox.setMaximum(9999)
        self.port_spinBox.setSingleStep(1)
        self.gridLayout.addWidget(self.port_spinBox, 2, 1, 1, 1)
        self.proxy_verticalLayout.addWidget(self.proxy_frame)
        self.addlink_verticalLayout.addLayout(self.proxy_verticalLayout)
#download UserName & Password
        self.download_horizontalLayout = QHBoxLayout()
        self.download_horizontalLayout.setContentsMargins(-1, 10, -1, -1)

        self.download_verticalLayout = QVBoxLayout()
        self.download_checkBox = QCheckBox(self.widget)
        self.download_verticalLayout.addWidget(self.download_checkBox)

        self.download_frame = QFrame(self.widget)
        self.download_frame.setFrameShape(QFrame.StyledPanel)
        self.download_frame.setFrameShadow(QFrame.Raised)

        self.gridLayout_2 = QGridLayout(self.download_frame)

        self.download_user_lineEdit = QLineEdit(self.download_frame)
        self.gridLayout_2.addWidget(self.download_user_lineEdit, 0, 1, 1, 1)

        self.download_user_label = QLabel(self.download_frame)
        self.gridLayout_2.addWidget(self.download_user_label, 0, 0, 1, 1)

        self.download_pass_label = QLabel(self.download_frame)
        self.gridLayout_2.addWidget(self.download_pass_label, 1, 0, 1, 1)

        self.download_pass_lineEdit = QLineEdit(self.download_frame)
        self.download_pass_lineEdit.setEchoMode(QLineEdit.Password)
        self.gridLayout_2.addWidget(self.download_pass_lineEdit, 1, 1, 1, 1)
        self.download_verticalLayout.addWidget(self.download_frame)
        self.download_horizontalLayout.addLayout(self.download_verticalLayout)
#select folder
        self.folder_frame = QFrame(self.widget)
        self.folder_frame.setFrameShape(QFrame.StyledPanel)
        self.folder_frame.setFrameShadow(QFrame.Raised)

        self.gridLayout_3 = QGridLayout(self.folder_frame)

        self.download_folder_lineEdit = QLineEdit(self.folder_frame)
        self.gridLayout_3.addWidget(self.download_folder_lineEdit, 2, 0, 1, 1)

        self.folder_pushButton = QPushButton(self.folder_frame)
        self.gridLayout_3.addWidget(self.folder_pushButton, 3, 0, 1, 1)
        self.folder_pushButton.setIcon(QIcon(icons + 'folder'))

        self.folder_label = QLabel(self.folder_frame)
        self.folder_label.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout_3.addWidget(self.folder_label, 1, 0, 1, 1)
        self.download_horizontalLayout.addWidget(self.folder_frame)
        self.addlink_verticalLayout.addLayout(self.download_horizontalLayout)
#start time
        self.time_limit_horizontalLayout = QHBoxLayout()
        self.time_limit_horizontalLayout.setContentsMargins(-1, 10, -1, -1)

        self.start_verticalLayout = QVBoxLayout()
        self.start_checkBox = QCheckBox(self.widget)
        self.start_verticalLayout.addWidget(self.start_checkBox)

        self.start_frame = QFrame(self.widget)
        self.start_frame.setFrameShape(QFrame.StyledPanel)
        self.start_frame.setFrameShadow(QFrame.Raised)

        self.horizontalLayout_5 = QHBoxLayout(self.start_frame)
        self.start_hour_spinBox = QSpinBox(self.start_frame)
        self.start_hour_spinBox.setMaximum(23)
        self.horizontalLayout_5.addWidget(self.start_hour_spinBox)

        self.start_label = QLabel(self.start_frame)
        self.horizontalLayout_5.addWidget(self.start_label)

        self.start_minute_spinBox = QSpinBox(self.start_frame)
        self.start_minute_spinBox.setMaximum(59)
        self.horizontalLayout_5.addWidget(self.start_minute_spinBox)
        self.start_verticalLayout.addWidget(self.start_frame)
        self.time_limit_horizontalLayout.addLayout(self.start_verticalLayout)
#end time
        self.end_verticalLayout = QVBoxLayout()

        self.end_checkBox = QCheckBox(self.widget)
        self.end_verticalLayout.addWidget(self.end_checkBox)

        self.end_frame = QFrame(self.widget)
        self.end_frame.setFrameShape(QFrame.StyledPanel)
        self.end_frame.setFrameShadow(QFrame.Raised)

        self.horizontalLayout_6 = QHBoxLayout(self.end_frame)

        self.end_hour_spinBox = QSpinBox(self.end_frame)
        self.end_hour_spinBox.setMaximum(23)
        self.horizontalLayout_6.addWidget(self.end_hour_spinBox)

        self.end_label = QLabel(self.end_frame)
        self.horizontalLayout_6.addWidget(self.end_label)

        self.end_minute_spinBox = QSpinBox(self.end_frame)
        self.end_minute_spinBox.setMaximum(59)
        self.horizontalLayout_6.addWidget(self.end_minute_spinBox)
        self.end_verticalLayout.addWidget(self.end_frame)
        self.time_limit_horizontalLayout.addLayout(self.end_verticalLayout)
#limit Speed
        self.limit_verticalLayout = QVBoxLayout()

        self.limit_checkBox = QCheckBox(self.widget)
        self.limit_verticalLayout.addWidget(self.limit_checkBox)

        self.limit_frame = QFrame(self.widget)
        self.limit_frame.setFrameShape(QFrame.StyledPanel)
        self.limit_frame.setFrameShadow(QFrame.Raised)

        self.horizontalLayout_4 = QHBoxLayout(self.limit_frame)

        self.limit_spinBox = QSpinBox(self.limit_frame)
        self.limit_spinBox.setMinimum(1)
        self.limit_spinBox.setMaximum(1023)
        self.horizontalLayout_4.addWidget(self.limit_spinBox)

        self.limit_comboBox = QComboBox(self.limit_frame)
        self.limit_comboBox.addItem("")
        self.limit_comboBox.addItem("")
        self.horizontalLayout_4.addWidget(self.limit_comboBox)
        self.limit_verticalLayout.addWidget(self.limit_frame)
        self.time_limit_horizontalLayout.addLayout(self.limit_verticalLayout)
        self.addlink_verticalLayout.addLayout(self.time_limit_horizontalLayout)
#number of connections
        self.connections_horizontalLayout = QHBoxLayout()
        self.connections_horizontalLayout.setContentsMargins(-1, 10, -1, -1)

        self.connections_frame = QFrame(self.widget)
        self.connections_frame.setFrameShape(QFrame.StyledPanel)
        self.connections_frame.setFrameShadow(QFrame.Raised)

        self.horizontalLayout_3 = QHBoxLayout(self.connections_frame)
        self.connections_label = QLabel(self.connections_frame)
        self.horizontalLayout_3.addWidget(self.connections_label)

        self.connections_spinBox = QSpinBox(self.connections_frame)
        self.connections_spinBox.setMinimum(1)
        self.connections_spinBox.setMaximum(16)
        self.connections_spinBox.setProperty("value", 16)
        self.horizontalLayout_3.addWidget(self.connections_spinBox)
        self.connections_horizontalLayout.addWidget(self.connections_frame)

        self.buttons_horizontalLayout = QHBoxLayout()
#ok cancel buttons
        self.cancel_pushButton = QPushButton(self.widget)
        self.cancel_pushButton.setIcon(QIcon(icons + 'remove'))

        self.ok_pushButton = QPushButton(self.widget)
        self.ok_pushButton.setIcon(QIcon(icons + 'ok'))
        self.buttons_horizontalLayout.addWidget(self.ok_pushButton)
        self.buttons_horizontalLayout.addWidget(self.cancel_pushButton)
        self.connections_horizontalLayout.addLayout(self.buttons_horizontalLayout)
        self.addlink_verticalLayout.addLayout(self.connections_horizontalLayout)

        self.verticalLayout.addLayout(self.addlink_verticalLayout)

    
        self.proxy_checkBox.raise_()
        self.download_checkBox.raise_()
        self.folder_frame.raise_()
        self.download_frame.raise_()
        self.limit_checkBox.raise_()
        self.connections_frame.raise_()
        self.limit_frame.raise_()
        self.cancel_pushButton.raise_()
        self.ok_pushButton.raise_()
        self.link_frame.raise_()
        self.proxy_frame.raise_()
        self.start_checkBox.raise_()
        self.end_checkBox.raise_()
        self.start_frame.raise_()
        self.end_frame.raise_()

#labels
        self.setWindowTitle( "Enter Your Link")
        self.link_label.setText( "Download Link : ")
        self.proxy_checkBox.setText( "Proxy")
        self.proxy_pass_label.setText( "Proxy PassWord : ")
        self.ip_label.setText( "IP  :")
        self.proxy_user_label.setText( "Proxy UserName : ")
        self.port_label.setText( "Port:")
        self.download_checkBox.setText( "Download UserName and PassWord")
        self.download_user_label.setText( "Download UserName : ")
        self.download_pass_label.setText( "Download PassWord : ")
        self.folder_pushButton.setText( "Change Download Folder")
        self.folder_label.setText( "Download Folder : ")
        self.start_checkBox.setText( "Start Time")
        self.start_label.setText( ":")
        self.end_checkBox.setText( "End Time")
        self.end_label.setText( ":")
        self.limit_checkBox.setText( "Limit Speed")
        self.limit_comboBox.setItemText(0,  "KB/S")
        self.limit_comboBox.setItemText(1,  "MB/S")
        self.connections_label.setText( "Number Of Connections :")
        self.cancel_pushButton.setText( "Cancel")
        self.ok_pushButton.setText( "OK")



