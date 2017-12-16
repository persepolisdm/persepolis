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
from PyQt5.QtWidgets import QDateTimeEdit, QCheckBox, QVBoxLayout, QHBoxLayout, QFrame, QWidget, QLabel, QLineEdit, QTabWidget, QSpinBox, QPushButton, QDial, QComboBox, QFontComboBox, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QIcon
from persepolis.scripts.newopen import Open
from persepolis.gui import icons_resource



class Setting_Ui(QWidget):
    def __init__(self, persepolis_setting):
        super().__init__()
        icon = QtGui.QIcon()
        self.setWindowIcon(QIcon.fromTheme('persepolis', QIcon(':/persepolis.svg')))
        self.setWindowTitle('Preferences')

        global icons
        icons = ':/' + str(persepolis_setting.value('settings/icons')) + '/'

        self.verticalLayout_2 = QVBoxLayout(self)
        self.setting_tabWidget = QTabWidget(self)
# download_options_tab
        self.download_options_tab = QWidget()
        self.layoutWidget = QWidget(self.download_options_tab)
        self.download_options_verticalLayout = QVBoxLayout(self.layoutWidget)
        self.download_options_verticalLayout.setContentsMargins(21, 21, 0, 0)
        self.download_options_verticalLayout.setObjectName(
            "download_options_verticalLayout")
        self.horizontalLayout_5 = QHBoxLayout()
# tries_label
        self.tries_label = QLabel(self.layoutWidget)
        self.horizontalLayout_5.addWidget(self.tries_label)
# tries_spinBox
        self.tries_spinBox = QSpinBox(self.layoutWidget)
        self.tries_spinBox.setMinimum(1)

        self.horizontalLayout_5.addWidget(self.tries_spinBox)
        self.download_options_verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_4 = QHBoxLayout()
# wait_label
        self.wait_label = QLabel(self.layoutWidget)
        self.horizontalLayout_4.addWidget(self.wait_label)
# wait_spinBox
        self.wait_spinBox = QSpinBox(self.layoutWidget)
        self.horizontalLayout_4.addWidget(self.wait_spinBox)

        self.download_options_verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_3 = QHBoxLayout()
# time_out_label
        self.time_out_label = QLabel(self.layoutWidget)
        self.horizontalLayout_3.addWidget(self.time_out_label)
# time_out_spinBox
        self.time_out_spinBox = QSpinBox(self.layoutWidget)
        self.horizontalLayout_3.addWidget(self.time_out_spinBox)

        self.download_options_verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2 = QHBoxLayout()
# connections_label
        self.connections_label = QLabel(self.layoutWidget)
        self.horizontalLayout_2.addWidget(self.connections_label)
# connections_spinBox
        self.connections_spinBox = QSpinBox(self.layoutWidget)
        self.connections_spinBox.setMinimum(1)
        self.connections_spinBox.setMaximum(16)
        self.horizontalLayout_2.addWidget(self.connections_spinBox)

        self.download_options_verticalLayout.addLayout(self.horizontalLayout_2)
# rpc_port_label
        self.rpc_port_label = QLabel(self.layoutWidget)
        self.rpc_horizontalLayout = QHBoxLayout()
        self.rpc_horizontalLayout.addWidget(self.rpc_port_label)
# rpc_port_spinbox
        self.rpc_port_spinbox = QSpinBox(self.layoutWidget)
        self.rpc_port_spinbox.setMinimum(1024)
        self.rpc_port_spinbox.setMaximum(65535)
        self.rpc_horizontalLayout.addWidget(self.rpc_port_spinbox)

        self.download_options_verticalLayout.addLayout(
            self.rpc_horizontalLayout)


# wait_queue
        wait_queue_horizontalLayout = QHBoxLayout() 

        self.wait_queue_label = QLabel(self.layoutWidget)
        wait_queue_horizontalLayout.addWidget(self.wait_queue_label)

        self.wait_queue_time = QDateTimeEdit(self.layoutWidget)
        self.wait_queue_time.setDisplayFormat('H:mm')
        wait_queue_horizontalLayout.addWidget(self.wait_queue_time)
        
        self.download_options_verticalLayout.addLayout(
            wait_queue_horizontalLayout) 

# change aria2 path
        aria2_path_verticalLayout = QVBoxLayout()

        self.aria2_path_checkBox = QCheckBox(self.layoutWidget)
        aria2_path_verticalLayout.addWidget(self.aria2_path_checkBox)

        aria2_path_horizontalLayout = QHBoxLayout()

        self.aria2_path_lineEdit = QLineEdit(self.layoutWidget)
        aria2_path_horizontalLayout.addWidget(self.aria2_path_lineEdit)

        self.aria2_path_pushButton = QPushButton(self.layoutWidget)
        aria2_path_horizontalLayout.addWidget(self.aria2_path_pushButton)

        aria2_path_verticalLayout.addLayout(aria2_path_horizontalLayout)

        self.download_options_verticalLayout.addLayout(
                aria2_path_verticalLayout)

        self.setting_tabWidget.addTab(self.download_options_tab, "")
# save_as_tab
        self.save_as_tab = QWidget()

        self.layoutWidget1 = QWidget(self.save_as_tab)

        self.save_as_verticalLayout = QVBoxLayout(self.layoutWidget1)
        self.save_as_verticalLayout.setContentsMargins(20, 30, 0, 0)

        self.download_folder_horizontalLayout = QHBoxLayout()
# download_folder_label
        self.download_folder_label = QLabel(self.layoutWidget1)
        self.download_folder_horizontalLayout.addWidget(
            self.download_folder_label)
# download_folder_lineEdit
        self.download_folder_lineEdit = QLineEdit(self.layoutWidget1)
        self.download_folder_horizontalLayout.addWidget(
            self.download_folder_lineEdit)
# download_folder_pushButton
        self.download_folder_pushButton = QPushButton(self.layoutWidget1)
        self.download_folder_horizontalLayout.addWidget(
            self.download_folder_pushButton)

        self.save_as_verticalLayout.addLayout(
            self.download_folder_horizontalLayout)
        self.temp_horizontalLayout = QHBoxLayout()
# temp_download_label
        self.temp_download_label = QLabel(self.layoutWidget1)
        self.temp_horizontalLayout.addWidget(self.temp_download_label)
# temp_download_lineEdit
        self.temp_download_lineEdit = QLineEdit(self.layoutWidget1)
        self.temp_horizontalLayout.addWidget(self.temp_download_lineEdit)
# temp_download_pushButton
        self.temp_download_pushButton = QPushButton(self.layoutWidget1)
        self.temp_horizontalLayout.addWidget(self.temp_download_pushButton)

        self.save_as_verticalLayout.addLayout(self.temp_horizontalLayout)

# create subfolder checkBox
        self.subfolder_checkBox = QCheckBox(self.layoutWidget1)
        self.save_as_verticalLayout.addWidget(self.subfolder_checkBox)
        
        self.setting_tabWidget.addTab(self.save_as_tab, "")
# notifications_tab
        self.notifications_tab = QWidget()
        self.layoutWidget2 = QWidget(self.notifications_tab)
        self.verticalLayout_4 = QVBoxLayout(self.layoutWidget2)
        self.verticalLayout_4.setContentsMargins(21, 21, 0, 0)
# enable_notifications_checkBox
        self.enable_notifications_checkBox = QCheckBox(self.layoutWidget2)
        self.verticalLayout_4.addWidget(self.enable_notifications_checkBox)
# sound_frame
        self.sound_frame = QFrame(self.layoutWidget2)
        self.sound_frame.setFrameShape(QFrame.StyledPanel)
        self.sound_frame.setFrameShadow(QFrame.Raised)

        self.verticalLayout = QVBoxLayout(self.sound_frame)
# volume_label
        self.volume_label = QLabel(self.sound_frame)
        self.verticalLayout.addWidget(self.volume_label)
# volume_dial
        self.volume_dial = QDial(self.sound_frame)
        self.volume_dial.setProperty("value", 100)
        self.verticalLayout.addWidget(self.volume_dial)

        self.verticalLayout_4.addWidget(self.sound_frame)
        self.setting_tabWidget.addTab(self.notifications_tab, "")
# style_tab
        self.style_tab = QWidget()
        self.layoutWidget3 = QWidget(self.style_tab)
        self.verticalLayout_3 = QVBoxLayout(self.layoutWidget3)
        self.verticalLayout_3.setContentsMargins(21, 21, 0, 0)
        self.horizontalLayout_8 = QHBoxLayout()
# style_label
        self.style_label = QLabel(self.layoutWidget3)
        self.horizontalLayout_8.addWidget(self.style_label)
# style_comboBox
        self.style_comboBox = QComboBox(self.layoutWidget3)
        self.horizontalLayout_8.addWidget(self.style_comboBox)

        self.verticalLayout_3.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_7 = QHBoxLayout()
# color_label
        self.color_label = QLabel(self.layoutWidget3)
        self.horizontalLayout_7.addWidget(self.color_label)
# color_comboBox
        self.color_comboBox = QComboBox(self.layoutWidget3)
        self.horizontalLayout_7.addWidget(self.color_comboBox)

        self.verticalLayout_3.addLayout(self.horizontalLayout_7)
# icon_label
        self.horizontalLayout_12 = QHBoxLayout()
        self.icon_label = QLabel(self.layoutWidget3)
        self.horizontalLayout_12.addWidget(self.icon_label)

# icon_comboBox
        self.icon_comboBox = QComboBox(self.layoutWidget3)
        self.horizontalLayout_12.addWidget(self.icon_comboBox)

        self.verticalLayout_3.addLayout(self.horizontalLayout_12)

# icons_size_comboBox
        self.icons_size_horizontalLayout = QHBoxLayout()
        self.icons_size_label = QLabel(self.layoutWidget3)
        self.icons_size_horizontalLayout.addWidget(self.icons_size_label)

        self.icons_size_comboBox = QComboBox(self.layoutWidget3)
        self.icons_size_horizontalLayout.addWidget(self.icons_size_comboBox)

        self.verticalLayout_3.addLayout(self.icons_size_horizontalLayout)

       

        self.horizontalLayout_6 = QHBoxLayout()
# notification_label
        self.horizontalLayout_13 = QHBoxLayout()
        self.notification_label = QLabel(self.layoutWidget3)
        self.horizontalLayout_13.addWidget(self.notification_label)
# notification_comboBox
        self.notification_comboBox = QComboBox(self.layoutWidget3)
        self.horizontalLayout_13.addWidget(self.notification_comboBox)
        self.verticalLayout_3.addLayout(self.horizontalLayout_13)
# font_checkBox
        self.font_checkBox = QCheckBox(self.layoutWidget3)
        self.horizontalLayout_6.addWidget(self.font_checkBox)
# fontComboBox
        self.fontComboBox = QFontComboBox(self.layoutWidget3)
        self.horizontalLayout_6.addWidget(self.fontComboBox)
# font_size_label
        self.font_size_label = QLabel(self.layoutWidget3)
        self.horizontalLayout_6.addWidget(self.font_size_label)
# font_size_spinBox
        self.font_size_spinBox = QSpinBox(self.layoutWidget3)
        self.font_size_spinBox.setMinimum(1)
        self.horizontalLayout_6.addWidget(self.font_size_spinBox)

        self.verticalLayout_3.addLayout(self.horizontalLayout_6)
        self.setting_tabWidget.addTab(self.style_tab, "")
        self.verticalLayout_2.addWidget(self.setting_tabWidget)
        self.horizontalLayout = QHBoxLayout()
        spacerItem = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
# Enable system tray icon
        self.enable_system_tray_checkBox = QCheckBox(self.layoutWidget3)
        self.verticalLayout_3.addWidget(self.enable_system_tray_checkBox)
# after_download dialog
        self.after_download_checkBox = QCheckBox()
        self.verticalLayout_3.addWidget(self.after_download_checkBox)

# show_menubar_checkbox
        self.show_menubar_checkbox = QCheckBox()
        self.verticalLayout_3.addWidget(self.show_menubar_checkbox)

# show_sidepanel_checkbox
        self.show_sidepanel_checkbox = QCheckBox()
        self.verticalLayout_3.addWidget(self.show_sidepanel_checkbox)

# hide progress window
        self.show_progress_window_checkbox = QCheckBox()
        self.verticalLayout_3.addWidget(self.show_progress_window_checkbox)

# add persepolis to startup
        self.startup_checkbox = QCheckBox()
        self.verticalLayout_3.addWidget(self.startup_checkbox)

# keep system awake
        self.keep_awake_checkBox = QCheckBox()
        self.verticalLayout_3.addWidget(self.keep_awake_checkBox)

# columns_tab
        self.columns_tab = QWidget()
        layoutWidget4 = QWidget(self.columns_tab)

        column_verticalLayout = QVBoxLayout(layoutWidget4)
        column_verticalLayout.setContentsMargins(21, 21, 0, 0)

        # creating checkBox for columns
        self.show_column_label = QLabel()
        self.column0_checkBox = QCheckBox()
        self.column1_checkBox = QCheckBox()
        self.column2_checkBox = QCheckBox()
        self.column3_checkBox = QCheckBox()
        self.column4_checkBox = QCheckBox()
        self.column5_checkBox = QCheckBox()
        self.column6_checkBox = QCheckBox()
        self.column7_checkBox = QCheckBox()
        self.column10_checkBox = QCheckBox()
        self.column11_checkBox = QCheckBox()
        self.column12_checkBox = QCheckBox()

        column_verticalLayout.addWidget(self.show_column_label) 
        column_verticalLayout.addWidget(self.column0_checkBox) 
        column_verticalLayout.addWidget(self.column1_checkBox) 
        column_verticalLayout.addWidget(self.column2_checkBox) 
        column_verticalLayout.addWidget(self.column3_checkBox) 
        column_verticalLayout.addWidget(self.column4_checkBox) 
        column_verticalLayout.addWidget(self.column5_checkBox) 
        column_verticalLayout.addWidget(self.column6_checkBox) 
        column_verticalLayout.addWidget(self.column7_checkBox) 
        column_verticalLayout.addWidget(self.column10_checkBox) 
        column_verticalLayout.addWidget(self.column11_checkBox) 
        column_verticalLayout.addWidget(self.column12_checkBox) 

        self.setting_tabWidget.addTab(self.columns_tab, '')
# defaults_pushButton
        self.defaults_pushButton = QPushButton(self)
        self.horizontalLayout.addWidget(self.defaults_pushButton)
# cancel_pushButton
        self.cancel_pushButton = QPushButton(self)
        self.cancel_pushButton.setIcon(QIcon(icons + 'remove'))
        self.horizontalLayout.addWidget(self.cancel_pushButton)
# ok_pushButton
        self.ok_pushButton = QPushButton(self)
        self.ok_pushButton.setIcon(QIcon(icons + 'ok'))
        self.horizontalLayout.addWidget(self.ok_pushButton)

        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.setting_tabWidget.setCurrentIndex(3)

        self.setWindowTitle("Preferences")

        self.tries_label.setToolTip(
            "<html><head/><body><p>Set number of tries if download failed.</p></body></html>")
        self.tries_label.setText("Number of tries : ")
        self.tries_spinBox.setToolTip(
            "<html><head/><body><p>Set number of tries if download failed.</p></body></html>")

        self.wait_label.setToolTip(
            "<html><head/><body><p>Set the seconds to wait between retries. Download manager will  retry  downloads  when  the  HTTP  server  returns  a  503 response.</p></body></html>")
        self.wait_label.setText("Wait between retries (seconds) : ")
        self.wait_spinBox.setToolTip(
            "<html><head/><body><p>Set the seconds to wait between retries. Download manager will  retry  downloads  when  the  HTTP  server  returns  a  503 response.</p></body></html>")

        self.time_out_label.setToolTip(
            "<html><head/><body><p>Set timeout in seconds. </p></body></html>")
        self.time_out_label.setText("Time out (seconds) : ")
        self.time_out_spinBox.setToolTip(
            "<html><head/><body><p>Set timeout in seconds. </p></body></html>")

        self.connections_label.setToolTip(
            "<html><head/><body><p>Using multiple connections can help speed up your download.</p></body></html>")
        self.connections_label.setText("Number of connections : ")
        self.connections_spinBox.setToolTip(
            "<html><head/><body><p>Using multiple connections can help speed up your download.</p></body></html>")

        self.rpc_port_label.setText("RPC port number : ")
        self.rpc_port_spinbox.setToolTip(
            "<html><head/><body><p> Specify a port number for JSON-RPC/XML-RPC server to listen to. Possible Values: 1024 - 65535 Default: 6801 </p></body></html>")

        self.wait_queue_label.setText('Wait between every downloads in queue:')

        self.aria2_path_checkBox.setText('Change aria2 default path')
        self.aria2_path_pushButton.setText('Change')
        aria2_path_tooltip ="<html><head/><body><p>Attention: Wrong path may have caused problem! Do it carefully or don't change default setting!</p></body></html>" 
        self.aria2_path_checkBox.setToolTip(aria2_path_tooltip)
        self.aria2_path_lineEdit.setToolTip(aria2_path_tooltip)
        self.aria2_path_pushButton.setToolTip(aria2_path_tooltip)

        self.setting_tabWidget.setTabText(self.setting_tabWidget.indexOf(
            self.download_options_tab),  "Download Options")

        self.download_folder_label.setText("Download Folder : ")
        self.download_folder_pushButton.setText("Change")

        self.temp_download_label.setText("Temporary Download Folder : ")
        self.temp_download_pushButton.setText("Change")

        self.subfolder_checkBox.setText("Create subfolders for Music,Videos,... in default download folder")

        self.setting_tabWidget.setTabText(
            self.setting_tabWidget.indexOf(self.save_as_tab),  "Save as")

        self.enable_notifications_checkBox.setText(
            "Enable notification sounds")

        self.volume_label.setText("Volume : ")

        self.setting_tabWidget.setTabText(self.setting_tabWidget.indexOf(
            self.notifications_tab),  "Notifications")

        self.style_label.setText("Style : ")
        self.color_label.setText("Color scheme : ")
        self.icon_label.setText("Icons : ")

        self.icons_size_label.setText("ToolBar's icons size : ")

        self.notification_label.setText("Notification type : ")

        self.font_checkBox.setText("Font : ")
        self.font_size_label.setText("Size : ")

        self.enable_system_tray_checkBox.setText("Enable system tray icon.")
        self.after_download_checkBox.setText(
            "Show download complete dialog,when download has finished.")

        self.show_menubar_checkbox.setText("Show menubar.")
        self.show_sidepanel_checkbox.setText("Show side panel.")
        self.show_progress_window_checkbox.setText(
            "Show download's progress window")

        self.startup_checkbox.setText("Run Persepolis at startup")

        self.keep_awake_checkBox.setText("Keep system awake!")
        self.keep_awake_checkBox.setToolTip(
            "<html><head/><body><p>This option is preventing system from going to sleep.\
            This is necessary if your power manager is suspending system automatically. </p></body></html>")
 
        self.wait_queue_time.setToolTip(
                "<html><head/><body><p>Format HH:MM</p></body></html>")
 
        self.setting_tabWidget.setTabText(
            self.setting_tabWidget.indexOf(self.style_tab),  "Preferences")

# columns_tab
        self.show_column_label.setText('Show this columns:')
        self.column0_checkBox.setText('File Name')
        self.column1_checkBox.setText('Status')
        self.column2_checkBox.setText('Size')
        self.column3_checkBox.setText('Downloaded')
        self.column4_checkBox.setText('Percentage')
        self.column5_checkBox.setText('Connections')
        self.column6_checkBox.setText('Transfer rate')
        self.column7_checkBox.setText('Estimate time left')
        self.column10_checkBox.setText('First try date')
        self.column11_checkBox.setText('Last try date')
        self.column12_checkBox.setText('Category')

        self.setting_tabWidget.setTabText(
            self.setting_tabWidget.indexOf(self.columns_tab), "Columns customization")


# window buttons
        self.defaults_pushButton.setText("Defaults")
        self.cancel_pushButton.setText("Cancel")
        self.ok_pushButton.setText("OK")
