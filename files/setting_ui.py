#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QCheckBox , QVBoxLayout , QHBoxLayout , QFrame , QWidget , QLabel ,QLineEdit , QTabWidget , QSpinBox , QPushButton , QDial , QComboBox , QFontComboBox , QSpacerItem , QSizePolicy
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



class Setting_Ui(QWidget):
    def __init__(self,parent=None):
        super().__init__()
        self.resize(578, 465)
        icon = QtGui.QIcon()
        self.setWindowIcon(QIcon.fromTheme('persepolis',QIcon(':/icon.svg') ))
        self.setWindowTitle('Preferences')

        self.verticalLayout_2 = QVBoxLayout(self)
        self.setting_tabWidget = QTabWidget(self)
#download_options_tab    
        self.download_options_tab = QWidget()
        self.layoutWidget = QWidget(self.download_options_tab)
        self.download_options_verticalLayout = QVBoxLayout(self.layoutWidget)
        self.download_options_verticalLayout.setContentsMargins(21, 21, 0, 0)
        self.download_options_verticalLayout.setObjectName("download_options_verticalLayout")
        self.horizontalLayout_5 = QHBoxLayout()
#tries_label
        self.tries_label = QLabel(self.layoutWidget)
        self.horizontalLayout_5.addWidget(self.tries_label)
#tries_spinBox
        self.tries_spinBox = QSpinBox(self.layoutWidget)
        self.tries_spinBox.setMinimum(1)

        self.horizontalLayout_5.addWidget(self.tries_spinBox)
        self.download_options_verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_4 = QHBoxLayout()
#wait_label
        self.wait_label = QLabel(self.layoutWidget)
        self.horizontalLayout_4.addWidget(self.wait_label)
#wait_spinBox
        self.wait_spinBox = QSpinBox(self.layoutWidget)
        self.horizontalLayout_4.addWidget(self.wait_spinBox)

        self.download_options_verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_3 = QHBoxLayout()
#time_out_label
        self.time_out_label = QLabel(self.layoutWidget)
        self.horizontalLayout_3.addWidget(self.time_out_label)
#time_out_spinBox
        self.time_out_spinBox = QSpinBox(self.layoutWidget)
        self.horizontalLayout_3.addWidget(self.time_out_spinBox)

        self.download_options_verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2 = QHBoxLayout()
#connections_label
        self.connections_label = QLabel(self.layoutWidget)
        self.horizontalLayout_2.addWidget(self.connections_label)
#connections_spinBox
        self.connections_spinBox = QSpinBox(self.layoutWidget)
        self.connections_spinBox.setMinimum(1)
        self.connections_spinBox.setMaximum(16)
        self.horizontalLayout_2.addWidget(self.connections_spinBox)

        self.download_options_verticalLayout.addLayout(self.horizontalLayout_2)
#rpc_port_label
        self.rpc_port_label = QLabel(self.layoutWidget)
        self.rpc_horizontalLayout = QHBoxLayout()
        self.rpc_horizontalLayout.addWidget(self.rpc_port_label)
#rpc_port_spinbox
        self.rpc_port_spinbox = QSpinBox(self.layoutWidget)
        self.rpc_port_spinbox.setMinimum(1024)
        self.rpc_port_spinbox.setMaximum(65535)
        self.rpc_horizontalLayout.addWidget(self.rpc_port_spinbox)
        self.download_options_verticalLayout.addLayout(self.rpc_horizontalLayout) 
        


        self.setting_tabWidget.addTab(self.download_options_tab, "")
#save_as_tab
        self.save_as_tab = QWidget()

        self.layoutWidget1 = QWidget(self.save_as_tab)

        self.save_as_verticalLayout = QVBoxLayout(self.layoutWidget1)
        self.save_as_verticalLayout.setContentsMargins(20, 30, 0, 0)

        self.download_folder_horizontalLayout = QHBoxLayout()
#download_folder_label
        self.download_folder_label = QLabel(self.layoutWidget1)
        self.download_folder_horizontalLayout.addWidget(self.download_folder_label)
#download_folder_lineEdit
        self.download_folder_lineEdit = QLineEdit(self.layoutWidget1)
        self.download_folder_horizontalLayout.addWidget(self.download_folder_lineEdit)
#download_folder_pushButton
        self.download_folder_pushButton = QPushButton(self.layoutWidget1)
        self.download_folder_horizontalLayout.addWidget(self.download_folder_pushButton)

        self.save_as_verticalLayout.addLayout(self.download_folder_horizontalLayout)
        self.temp_horizontalLayout = QHBoxLayout()
#temp_download_label
        self.temp_download_label = QLabel(self.layoutWidget1)
        self.temp_horizontalLayout.addWidget(self.temp_download_label)
#temp_download_lineEdit
        self.temp_download_lineEdit = QLineEdit(self.layoutWidget1)
        self.temp_horizontalLayout.addWidget(self.temp_download_lineEdit)
#temp_download_pushButton
        self.temp_download_pushButton = QPushButton(self.layoutWidget1)
        self.temp_horizontalLayout.addWidget(self.temp_download_pushButton)

        self.save_as_verticalLayout.addLayout(self.temp_horizontalLayout)
        self.setting_tabWidget.addTab(self.save_as_tab, "")
#notifications_tab
        self.notifications_tab = QWidget()
        self.layoutWidget2 = QWidget(self.notifications_tab)
        self.verticalLayout_4 = QVBoxLayout(self.layoutWidget2)
        self.verticalLayout_4.setContentsMargins(21, 21, 0, 0)
#enable_notifications_checkBox
        self.enable_notifications_checkBox = QCheckBox(self.layoutWidget2)
        self.verticalLayout_4.addWidget(self.enable_notifications_checkBox)
#sound_frame
        self.sound_frame = QFrame(self.layoutWidget2)
        self.sound_frame.setFrameShape(QFrame.StyledPanel)
        self.sound_frame.setFrameShadow(QFrame.Raised)

        self.verticalLayout = QVBoxLayout(self.sound_frame)
#volume_label
        self.volume_label = QLabel(self.sound_frame)
        self.verticalLayout.addWidget(self.volume_label)
#volume_dial
        self.volume_dial = QDial(self.sound_frame)
        self.volume_dial.setProperty("value", 100)
        self.verticalLayout.addWidget(self.volume_dial)

        self.verticalLayout_4.addWidget(self.sound_frame)
        self.setting_tabWidget.addTab(self.notifications_tab, "")
#style_tab
        self.style_tab = QWidget()
        self.layoutWidget3 = QWidget(self.style_tab)
        self.verticalLayout_3 = QVBoxLayout(self.layoutWidget3)
        self.verticalLayout_3.setContentsMargins(21, 21, 0, 0)
        self.horizontalLayout_8 = QHBoxLayout()
#style_label
        self.style_label = QLabel(self.layoutWidget3)
        self.horizontalLayout_8.addWidget(self.style_label)
#style_comboBox
        self.style_comboBox = QComboBox(self.layoutWidget3)
        self.horizontalLayout_8.addWidget(self.style_comboBox)

        self.verticalLayout_3.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_7 = QHBoxLayout()
#color_label
        self.color_label = QLabel(self.layoutWidget3)
        self.horizontalLayout_7.addWidget(self.color_label)
#color_comboBox
        self.color_comboBox = QComboBox(self.layoutWidget3)
        self.horizontalLayout_7.addWidget(self.color_comboBox)

        self.verticalLayout_3.addLayout(self.horizontalLayout_7)
#icon_label
        self.horizontalLayout_12 = QHBoxLayout()
        self.icon_label = QLabel(self.layoutWidget3)
        self.horizontalLayout_12.addWidget(self.icon_label)
#icon_comboBox
        self.icon_comboBox = QComboBox(self.layoutWidget3)
        self.horizontalLayout_12.addWidget(self.icon_comboBox)

        self.verticalLayout_3.addLayout(self.horizontalLayout_12)
        self.horizontalLayout_6 = QHBoxLayout()
#notification_label
        self.horizontalLayout_13 = QHBoxLayout()
        self.notification_label = QLabel(self.layoutWidget3)
        self.horizontalLayout_13.addWidget(self.notification_label)
#notification_comboBox
        self.notification_comboBox = QComboBox(self.layoutWidget3)
        self.horizontalLayout_13.addWidget(self.notification_comboBox)
        self.verticalLayout_3.addLayout(self.horizontalLayout_13)
#font_label
        self.font_label = QLabel(self.layoutWidget3)
        self.horizontalLayout_6.addWidget(self.font_label)
#fontComboBox
        self.fontComboBox = QFontComboBox(self.layoutWidget3)
        self.horizontalLayout_6.addWidget(self.fontComboBox)
#font_size_label
        self.font_size_label = QLabel(self.layoutWidget3)
        self.horizontalLayout_6.addWidget(self.font_size_label)
#font_size_spinBox
        self.font_size_spinBox = QSpinBox(self.layoutWidget3)
        self.font_size_spinBox.setMinimum(1)
        self.horizontalLayout_6.addWidget(self.font_size_spinBox)

        self.verticalLayout_3.addLayout(self.horizontalLayout_6)
        self.setting_tabWidget.addTab(self.style_tab, "")
        self.verticalLayout_2.addWidget(self.setting_tabWidget)
        self.horizontalLayout = QHBoxLayout()
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
#Enable system tray icon
        self.enable_system_tray_checkBox = QCheckBox(self.layoutWidget3)
        self.verticalLayout_3.addWidget(self.enable_system_tray_checkBox)
#after_download dialog
        self.after_download_checkBox = QCheckBox()    
        self.verticalLayout_3.addWidget(self.after_download_checkBox)

#defaults_pushButton
        self.defaults_pushButton = QPushButton(self)
        self.horizontalLayout.addWidget(self.defaults_pushButton)
#cancel_pushButton
        self.cancel_pushButton = QPushButton(self)
        self.cancel_pushButton.setIcon(QIcon(icons + 'remove'))
        self.horizontalLayout.addWidget(self.cancel_pushButton)
#ok_pushButton
        self.ok_pushButton = QPushButton(self)
        self.ok_pushButton.setIcon(QIcon(icons + 'ok'))
        self.horizontalLayout.addWidget(self.ok_pushButton)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.setting_tabWidget.setCurrentIndex(3)

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
        self.rpc_port_label.setText("RPC port number : ")
        self.rpc_port_spinbox.setToolTip("<html><head/><body><p> Specify a port number for JSON-RPC/XML-RPC server to listen to. Possible Values: 1024 - 65535 Default: 6801 </p></body></html>")
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
        self.notification_label.setText("Notification type : ")
        self.font_label.setText( "Font : ")
        self.font_size_label.setText( "Size : ")
        self.enable_system_tray_checkBox.setText("Enable system tray icon.")
        self.after_download_checkBox.setText("Show download complete dialog,when download finished.")
        self.setting_tabWidget.setTabText(self.setting_tabWidget.indexOf(self.style_tab),  "Appearance")
        self.defaults_pushButton.setText( "Defaults")
        self.cancel_pushButton.setText( "Cancel")
        self.ok_pushButton.setText( "OK")

