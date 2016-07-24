#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from PyQt5 import QtCore, QtGui, QtWidgets
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

icons = ':/' +  str(setting_dict['icons']) + '/'



class Setting_Ui(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super().__init__()
        self.resize(578, 465)
        icon = QtGui.QIcon()
        self.setWindowIcon(QIcon(':/icon'))
        self.setWindowTitle('Preferences')

        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self)
        self.setting_tabWidget = QtWidgets.QTabWidget(self)
#download_options_tab    
        self.download_options_tab = QtWidgets.QWidget()
        self.layoutWidget = QtWidgets.QWidget(self.download_options_tab)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 20, 273, 112))
        self.download_options_verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.download_options_verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.download_options_verticalLayout.setObjectName("download_options_verticalLayout")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
#tries_label
        self.tries_label = QtWidgets.QLabel(self.layoutWidget)
        self.horizontalLayout_5.addWidget(self.tries_label)
#tries_spinBox
        self.tries_spinBox = QtWidgets.QSpinBox(self.layoutWidget)
        self.tries_spinBox.setMinimum(1)

        self.horizontalLayout_5.addWidget(self.tries_spinBox)
        self.download_options_verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
#wait_label
        self.wait_label = QtWidgets.QLabel(self.layoutWidget)
        self.horizontalLayout_4.addWidget(self.wait_label)
#wait_spinBox
        self.wait_spinBox = QtWidgets.QSpinBox(self.layoutWidget)
        self.horizontalLayout_4.addWidget(self.wait_spinBox)

        self.download_options_verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
#time_out_label
        self.time_out_label = QtWidgets.QLabel(self.layoutWidget)
        self.horizontalLayout_3.addWidget(self.time_out_label)
#time_out_spinBox
        self.time_out_spinBox = QtWidgets.QSpinBox(self.layoutWidget)
        self.horizontalLayout_3.addWidget(self.time_out_spinBox)

        self.download_options_verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
#connections_label
        self.connections_label = QtWidgets.QLabel(self.layoutWidget)
        self.horizontalLayout_2.addWidget(self.connections_label)
#connections_spinBox
        self.connections_spinBox = QtWidgets.QSpinBox(self.layoutWidget)
        self.connections_spinBox.setMinimum(1)
        self.connections_spinBox.setMaximum(16)
        self.horizontalLayout_2.addWidget(self.connections_spinBox)

        self.download_options_verticalLayout.addLayout(self.horizontalLayout_2)
        self.setting_tabWidget.addTab(self.download_options_tab, "")
#save_as_tab
        self.save_as_tab = QtWidgets.QWidget()

        self.layoutWidget1 = QtWidgets.QWidget(self.save_as_tab)
        self.layoutWidget1.setGeometry(QtCore.QRect(20, 30, 428, 62))

        self.save_as_verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget1)
        self.save_as_verticalLayout.setContentsMargins(0, 0, 0, 0)

        self.download_folder_horizontalLayout = QtWidgets.QHBoxLayout()
#download_folder_label
        self.download_folder_label = QtWidgets.QLabel(self.layoutWidget1)
        self.download_folder_horizontalLayout.addWidget(self.download_folder_label)
#download_folder_lineEdit
        self.download_folder_lineEdit = QtWidgets.QLineEdit(self.layoutWidget1)
        self.download_folder_horizontalLayout.addWidget(self.download_folder_lineEdit)
#download_folder_pushButton
        self.download_folder_pushButton = QtWidgets.QPushButton(self.layoutWidget1)
        self.download_folder_horizontalLayout.addWidget(self.download_folder_pushButton)

        self.save_as_verticalLayout.addLayout(self.download_folder_horizontalLayout)
        self.temp_horizontalLayout = QtWidgets.QHBoxLayout()
#temp_download_label
        self.temp_download_label = QtWidgets.QLabel(self.layoutWidget1)
        self.temp_horizontalLayout.addWidget(self.temp_download_label)
#temp_download_lineEdit
        self.temp_download_lineEdit = QtWidgets.QLineEdit(self.layoutWidget1)
        self.temp_horizontalLayout.addWidget(self.temp_download_lineEdit)
#temp_download_pushButton
        self.temp_download_pushButton = QtWidgets.QPushButton(self.layoutWidget1)
        self.temp_horizontalLayout.addWidget(self.temp_download_pushButton)

        self.save_as_verticalLayout.addLayout(self.temp_horizontalLayout)
        self.setting_tabWidget.addTab(self.save_as_tab, "")
#notifications_tab
        self.notifications_tab = QtWidgets.QWidget()
        self.layoutWidget2 = QtWidgets.QWidget(self.notifications_tab)
        self.layoutWidget2.setGeometry(QtCore.QRect(21, 21, 198, 171))
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.layoutWidget2)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
#enable_notifications_checkBox
        self.enable_notifications_checkBox = QtWidgets.QCheckBox(self.layoutWidget2)
        self.verticalLayout_4.addWidget(self.enable_notifications_checkBox)
#sound_frame
        self.sound_frame = QtWidgets.QFrame(self.layoutWidget2)
        self.sound_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.sound_frame.setFrameShadow(QtWidgets.QFrame.Raised)

        self.verticalLayout = QtWidgets.QVBoxLayout(self.sound_frame)
#volume_label
        self.volume_label = QtWidgets.QLabel(self.sound_frame)
        self.verticalLayout.addWidget(self.volume_label)
#volume_dial
        self.volume_dial = QtWidgets.QDial(self.sound_frame)
        self.volume_dial.setProperty("value", 100)
        self.verticalLayout.addWidget(self.volume_dial)

        self.verticalLayout_4.addWidget(self.sound_frame)
        self.setting_tabWidget.addTab(self.notifications_tab, "")
#style_tab
        self.style_tab = QtWidgets.QWidget()
        self.layoutWidget3 = QtWidgets.QWidget(self.style_tab)
        self.layoutWidget3.setGeometry(QtCore.QRect(31, 21, 359, 112))
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.layoutWidget3)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
#style_label
        self.style_label = QtWidgets.QLabel(self.layoutWidget3)
        self.horizontalLayout_8.addWidget(self.style_label)
#style_comboBox
        self.style_comboBox = QtWidgets.QComboBox(self.layoutWidget3)
        self.horizontalLayout_8.addWidget(self.style_comboBox)

        self.verticalLayout_3.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
#color_label
        self.color_label = QtWidgets.QLabel(self.layoutWidget3)
        self.horizontalLayout_7.addWidget(self.color_label)
#color_comboBox
        self.color_comboBox = QtWidgets.QComboBox(self.layoutWidget3)
        self.horizontalLayout_7.addWidget(self.color_comboBox)

        self.verticalLayout_3.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
#icon_label
        self.icon_label = QtWidgets.QLabel(self.layoutWidget3)
        self.horizontalLayout_12.addWidget(self.icon_label)
#icon_comboBox
        self.icon_comboBox = QtWidgets.QComboBox(self.layoutWidget3)
        self.horizontalLayout_12.addWidget(self.icon_comboBox)

        self.verticalLayout_3.addLayout(self.horizontalLayout_12)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
#font_label
        self.font_label = QtWidgets.QLabel(self.layoutWidget3)
        self.horizontalLayout_6.addWidget(self.font_label)
#fontComboBox
        self.fontComboBox = QtWidgets.QFontComboBox(self.layoutWidget3)
        self.horizontalLayout_6.addWidget(self.fontComboBox)
#font_size_label
        self.font_size_label = QtWidgets.QLabel(self.layoutWidget3)
        self.horizontalLayout_6.addWidget(self.font_size_label)
#font_size_spinBox
        self.font_size_spinBox = QtWidgets.QSpinBox(self.layoutWidget3)
        self.font_size_spinBox.setMinimum(1)
        self.horizontalLayout_6.addWidget(self.font_size_spinBox)

        self.verticalLayout_3.addLayout(self.horizontalLayout_6)
        self.setting_tabWidget.addTab(self.style_tab, "")
        self.verticalLayout_2.addWidget(self.setting_tabWidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
#Enable system tray icon
        self.enable_system_tray_checkBox = QtWidgets.QCheckBox(self.layoutWidget3)
        self.verticalLayout_3.addWidget(self.enable_system_tray_checkBox)
        
#defaults_pushButton
        self.defaults_pushButton = QtWidgets.QPushButton(self)
        self.horizontalLayout.addWidget(self.defaults_pushButton)
#cancel_pushButton
        self.cancel_pushButton = QtWidgets.QPushButton(self)
        self.cancel_pushButton.setIcon(QIcon(icons + 'remove'))
        self.horizontalLayout.addWidget(self.cancel_pushButton)
#ok_pushButton
        self.ok_pushButton = QtWidgets.QPushButton(self)
        self.ok_pushButton.setIcon(QIcon(icons + 'ok'))
        self.horizontalLayout.addWidget(self.ok_pushButton)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.setting_tabWidget.setCurrentIndex(3)
#         QtCore.QMetaObject.connectSlotsByName(self)

        self.setWindowTitle( "Preferences")
        self.tries_label.setToolTip( "<html><head/><body><p>Set number of tries if download failed.</p></body></html>")
        self.tries_label.setText( "Number of tries : ")
        self.tries_spinBox.setToolTip( "<html><head/><body><p>Set number of tries if download failed.</p></body></html>")
        self.wait_label.setToolTip( "<html><head/><body><p>Set the seconds to wait between retries. Download manager will  retry  downloads  when  the  HTTP  server  returns  a  503 response.</p></body></html>")
        self.wait_label.setText( "Wait between retries (seconds) : ")
        self.wait_spinBox.setToolTip( "<html><head/><body><p>Set the seconds to wait between retries. Download manager will  retry  downloads  when  the  HTTP  server  returns  a  503 response.</p></body></html>")
        self.time_out_label.setToolTip( "<html><head/><body><p>Set timeout in seconds. </p></body></html>")
        self.time_out_label.setText( "Time out (seconds) : ")
        self.time_out_spinBox.setToolTip( "<html><head/><body><p>Set timeout in seconds. </p></body></html>")
        self.connections_label.setToolTip( "<html><head/><body><p>Using multiple connections can help speed up your download.</p></body></html>")
        self.connections_label.setText( "Number of connections : ")
        self.connections_spinBox.setToolTip( "<html><head/><body><p>Using multiple connections can help speed up your download.</p></body></html>")
        self.setting_tabWidget.setTabText(self.setting_tabWidget.indexOf(self.download_options_tab),  "Download Options")
        self.download_folder_label.setText( "Download Folder : ")
        self.download_folder_pushButton.setText( "Change")
        self.temp_download_label.setText( "Temporary Download Folder : ")
        self.temp_download_pushButton.setText( "Change")
        self.setting_tabWidget.setTabText(self.setting_tabWidget.indexOf(self.save_as_tab),  "Save as")
        self.enable_notifications_checkBox.setText( "Enable notification sounds")
        self.volume_label.setText( "Volume : ")
        self.setting_tabWidget.setTabText(self.setting_tabWidget.indexOf(self.notifications_tab),  "Notifications")
        self.style_label.setText( "Style : ")
        self.color_label.setText( "Color scheme : ")
        self.icon_label.setText( "Icons : ")
        self.font_label.setText( "Font : ")
        self.font_size_label.setText( "Size : ")
        self.enable_system_tray_checkBox.setText("Enable system tray icon")
        self.setting_tabWidget.setTabText(self.setting_tabWidget.indexOf(self.style_tab),  "Appearance")
        self.defaults_pushButton.setText( "Defaults")
        self.cancel_pushButton.setText( "Cancel")
        self.ok_pushButton.setText( "OK")

