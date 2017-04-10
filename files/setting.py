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

from setting_ui import Setting_Ui
import ast
import os
import copy
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QStyleFactory, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QSize, QPoint, QDir
from newopen import Open, readDict
import osCommands
import platform
import startup

home_address = os.path.expanduser("~")
os_type = platform.system()

# config_folder
if os_type == 'Linux' or os_type == 'FreeBSD' or os_type == 'OpenBSD':
    config_folder = os.path.join(
        str(home_address), ".config/persepolis_download_manager")
elif os_type == 'Darwin':
    config_folder = os.path.join(
        str(home_address), "Library/Application Support/persepolis_download_manager")
elif os_type == 'Windows':
    config_folder = os.path.join(
        str(home_address), 'AppData', 'Local', 'persepolis_download_manager')


class PreferencesWindow(Setting_Ui):
    def __init__(self, parent, persepolis_setting):
        super().__init__(persepolis_setting)
        self.persepolis_setting = persepolis_setting
        self.parent = parent
        self.grandparent = parent.persepolis_main

        self.persepolis_setting.beginGroup('settings')

        # initialization
        self.tries_spinBox.setValue(
            int(self.persepolis_setting.value('max-tries')))
        self.wait_spinBox.setValue(
            int(self.persepolis_setting.value('retry-wait')))
        self.time_out_spinBox.setValue(
            int(self.persepolis_setting.value('timeout')))
        self.connections_spinBox.setValue(
            int(self.persepolis_setting.value('connections')))
        self.rpc_port_spinbox.setValue(
            int(self.persepolis_setting.value('rpc-port')))

# save_as_tab
        self.download_folder_lineEdit.setText(
            str(self.persepolis_setting.value('download_path')))
        self.temp_download_lineEdit.setText(
            str(self.persepolis_setting.value('download_path_temp')))

        if str(self.persepolis_setting.value('subfolder')) == 'yes':
            self.subfolder_checkBox.setChecked(True)
        else:
            self.subfolder_checkBox.setChecked(False)

# notifications_tab
        self.volume_label.setText(
            'Volume : ' + str(self.persepolis_setting.value('sound-volume')))
        self.volume_dial.setValue(
            int(self.persepolis_setting.value('sound-volume')))
# set style
        available_styles = QStyleFactory.keys()
        for style in available_styles:
            self.style_comboBox.addItem(style)

        self.style_comboBox.addItem('System')

        current_style_index = self.style_comboBox.findText(
            str(self.persepolis_setting.value('style')))
        if current_style_index != -1:
            self.style_comboBox.setCurrentIndex(current_style_index)
# set color_scheme
        color_scheme = ['System', 'Persepolis Dark Red', 'Persepolis Dark Blue', 'Persepolis ArcDark Red',
                        'Persepolis ArcDark Blue', 'Persepolis Light Red', 'Persepolis Light Blue']
        self.color_comboBox.addItems(color_scheme)

        current_color_index = self.color_comboBox.findText(
            str(self.persepolis_setting.value('color-scheme')))
        self.color_comboBox.setCurrentIndex(current_color_index)
# set icons
        icons = ['Archdroid-Red', 'Archdroid-Blue']
        self.icon_comboBox.addItems(icons)

        current_icons_index = self.icon_comboBox.findText(
            str(self.persepolis_setting.value('icons')))
        self.icon_comboBox.setCurrentIndex(current_icons_index)
        self.current_icon = str(self.icon_comboBox.currentText())
# set notification
        notifications = ['Native notification', 'QT notification']
        self.notification_comboBox.addItems(notifications)
        current_notification_index = self.notification_comboBox.findText(
            str(self.persepolis_setting.value('notification')))
        self.notification_comboBox.setCurrentIndex(current_notification_index)
# set font
        font_setting = QFont()
        font_setting.setFamily(str(self.persepolis_setting.value('font')))
        self.fontComboBox.setCurrentFont(font_setting)

        self.font_size_spinBox.setValue(
            int(self.persepolis_setting.value('font-size')))

# sound frame
        self.sound_frame.setEnabled(False)
        self.enable_notifications_checkBox.toggled.connect(self.soundFrame)
        if str(self.persepolis_setting.value('sound')) == 'yes':
            self.enable_notifications_checkBox.setChecked(True)
        else:
            self.enable_notifications_checkBox.setChecked(False)
# connect folder buttons
        self.download_folder_lineEdit.setEnabled(False)
        self.download_folder_pushButton.clicked.connect(
            self.downloadFolderPushButtonClicked)
        self.temp_download_lineEdit.setEnabled(False)
        self.temp_download_pushButton.clicked.connect(
            self.tempDownloadPushButtonClicked)


# dial
        self.volume_dial.setNotchesVisible(True)
        self.volume_dial.valueChanged.connect(self.dialChanged)

# tray icon

        if str(self.persepolis_setting.value('tray-icon')) == 'yes':
            self.enable_system_tray_checkBox.setChecked(True)
        else:
            self.enable_notifications_checkBox.setChecked(False)
# show_menubar
        if str(self.persepolis_setting.value('show-menubar')) == 'yes':
            self.show_menubar_checkbox.setChecked(True)
        else:
            self.show_menubar_checkbox.setChecked(False)

        if platform.system() == 'Darwin':
            self.show_menubar_checkbox.setChecked(True)
            self.show_menubar_checkbox.hide()
# show_sidepanel
        if str(self.persepolis_setting.value('show-sidepanel')) == 'yes':
            self.show_sidepanel_checkbox.setChecked(True)
        else:
            self.show_sidepanel_checkbox.setChecked(False)

# show ProgressWindow
        if str(self.persepolis_setting.value('show-progress')) == 'yes':
            self.show_progress_window_checkbox.setChecked(True)
        else:
            self.show_progress_window_checkbox.setChecked(False)

# after download dialog
        if str(self.persepolis_setting.value('after-dialog')) == 'yes':
            self.after_download_checkBox.setChecked(True)
        else:
            self.after_download_checkBox.setChecked(False)

# run persepolis at startup checkBox
        if str(self.persepolis_setting.value('startup')) == 'yes':
            self.startup_checkbox.setChecked(True)
        else:
            self.startup_checkbox.setChecked(False)


# ok cancel default button
        self.cancel_pushButton.clicked.connect(self.close)
        self.defaults_pushButton.clicked.connect(
            self.defaultsPushButtonPressed)
        self.ok_pushButton.clicked.connect(self.okPushButtonPressed)

# setting window size and position
        size = self.persepolis_setting.value(
            'PreferencesWindow/size', QSize(578, 465))
        position = self.persepolis_setting.value(
            'PreferencesWindow/position', QPoint(300, 300))

        self.resize(size)
        self.move(position)

        self.persepolis_setting.endGroup()

    def closeEvent(self, event):
        # saving window size and position
        self.persepolis_setting.setValue('PreferencesWindow/size', self.size())
        self.persepolis_setting.setValue(
            'PreferencesWindow/position', self.pos())
        self.persepolis_setting.sync()
        self.destroy()

        if self.parent.isVisible() == False:
            self.parent.minMaxTray(event)
        self.close()

    def soundFrame(self, checkBox):
        if self.enable_notifications_checkBox.isChecked() == True:
            self.sound_frame.setEnabled(True)
        else:
            self.sound_frame.setEnabled(False)

    def downloadFolderPushButtonClicked(self, button):
        download_path = str(
            self.persepolis_setting.value('settings/download_path'))
        fname = QFileDialog.getExistingDirectory(
            self, 'Select a directory', download_path)

        if fname:
            # Returns pathName with the '/' separators converted to separators that are appropriate for the underlying operating system.
            # On Windows, toNativeSeparators("c:/winnt/system32") returns
            # "c:\winnt\system32".
            fname = QDir.toNativeSeparators(fname)
            self.download_folder_lineEdit.setText(fname)
            self.persepolis_setting.setValue(
                'settings/download_path', str(fname))

    def tempDownloadPushButtonClicked(self, button):
        download_path_temp = str(
            self.persepolis_setting.value('settings/download_path_temp'))
        fname = QFileDialog.getExistingDirectory(
            self, 'Open f', download_path_temp)
        if fname:
            self.temp_download_lineEdit.setText(fname)
            self.persepolis_setting.setValue(
                'settings/download_path_temp', str(fname))

    def dialChanged(self, dial):
        self.volume_label.setText('Volume : ' + str(self.volume_dial.value()))

    def defaultsPushButtonPressed(self, button):
        self.persepolis_setting.beginGroup('settings')

        # persepolis temporary download folder
        if os_type != 'Windows':
            download_path_temp_default = str(home_address) + '/.persepolis'
        else:
            download_path_temp_default = os.path.join(
                str(home_address), 'AppData', 'Local', 'persepolis')

        download_path_default = os.path.join(
            str(home_address), 'Downloads', 'Persepolis')

        self.setting_dict = {'subfolder': 'yes', 'startup': 'no', 'show-progress': 'yes', 'show-menubar': 'no', 'show-sidepanel': 'yes', 'rpc-port': 6801, 'notification': 'Native notification', 'after-dialog': 'yes', 'tray-icon': 'yes', 'max-tries': 5, 'retry-wait': 0, 'timeout': 60,
                             'connections': 16, 'download_path_temp': download_path_temp_default, 'download_path': download_path_default, 'sound': 'yes', 'sound-volume': 100, 'style': 'Fusion', 'color-scheme': 'Persepolis Dark Red', 'icons': 'Archdroid-Red', 'font': 'Ubuntu', 'font-size': 9}

        # this loop is checking values in persepolis_setting . if value is not
        # valid then value replaced by default_setting_dict value
        for key in self.setting_dict.keys():
            self.persepolis_setting.setValue(key, self.setting_dict[key])

        self.tries_spinBox.setValue(int(self.setting_dict['max-tries']))
        self.wait_spinBox.setValue(int(self.setting_dict['retry-wait']))
        self.time_out_spinBox.setValue(int(self.setting_dict['timeout']))
        self.connections_spinBox.setValue(
            int(self.setting_dict['connections']))
        self.rpc_port_spinbox.setValue(int(self.setting_dict['rpc-port']))

# save_as_tab
        self.download_folder_lineEdit.setText(
            str(self.setting_dict['download_path']))
        self.temp_download_lineEdit.setText(
            str(self.setting_dict['download_path_temp']))

        self.subfolder_checkBox.setChecked(True)

# notifications_tab
        self.volume_label.setText(
            'Volume : ' + str(self.setting_dict['sound-volume']))
        self.volume_dial.setValue(int(self.setting_dict['sound-volume']))
# set style
        current_style_index = self.style_comboBox.findText(
            str(self.setting_dict['style']))
        self.style_comboBox.setCurrentIndex(current_style_index)
# set color_scheme
        current_color_index = self.color_comboBox.findText(
            str(self.setting_dict['color-scheme']))
        self.color_comboBox.setCurrentIndex(current_color_index)
# set icons
        current_icons_index = self.icon_comboBox.findText(
            str(self.setting_dict['icons']))
        self.icon_comboBox.setCurrentIndex(current_icons_index)
# set notification
        current_notification_index = self.notification_comboBox.findText(
            str(self.setting_dict['notification']))
        self.notification_comboBox.setCurrentIndex(current_notification_index)

# set font
        font_setting = QFont()
        font_setting.setFamily(str(self.setting_dict['font']))
        self.fontComboBox.setCurrentFont(font_setting)

        self.font_size_spinBox.setValue(int(self.setting_dict['font-size']))

# sound frame
        self.enable_notifications_checkBox.setChecked(True)
# tray icon
        self.enable_system_tray_checkBox.setChecked(True)
# after_download_checkBox
        self.after_download_checkBox.setChecked(True)
# hide menubar for linux
        if platform.system == 'Darwin':
            self.show_menubar_checkbox.setChecked(True)
        else:
            self.show_menubar_checkbox.setChecked(False)
# show side panel
        self.show_sidepanel_checkbox.setChecked(True)

# show progress window
        self.show_progress_window_checkbox.setChecked(True)

# run persepolis at startup checkBox
        self.startup_checkbox.setChecked(False)

        self.persepolis_setting.endGroup()

    def okPushButtonPressed(self, button):

        self.persepolis_setting.beginGroup('settings')

        self.persepolis_setting.setValue(
            'max-tries', self.tries_spinBox.value())
        self.persepolis_setting.setValue(
            'retry-wait', self.wait_spinBox.value())
        self.persepolis_setting.setValue(
            'timeout', self.time_out_spinBox.value())
        self.persepolis_setting.setValue(
            'connections', self.connections_spinBox.value())
        self.persepolis_setting.setValue(
            'rpc-port', self.rpc_port_spinbox.value())
        self.persepolis_setting.setValue(
            'download_path', self.download_folder_lineEdit.text())
        self.persepolis_setting.setValue(
            'download_path_temp', self.temp_download_lineEdit.text())
        self.persepolis_setting.setValue(
            'sound-volume', self.volume_dial.value())
        self.persepolis_setting.setValue(
            'notification', self.notification_comboBox.currentText())

# changing icons

        icons = self.icon_comboBox.currentText()
        self.persepolis_setting.setValue('icons', icons)

        if icons != self.current_icon:  # it means icons changed

            for list in [self.parent.browser_integration_window_list, self.parent.about_window_list, self.parent.addlinkwindows_list, self.parent.propertieswindows_list, self.parent.afterdownload_list, self.parent.text_queue_window_list, self.parent.progress_window_list]:
                for window in list:
                    window.changeIcon(icons)

            self.parent.changeIcon(icons)

# style
        style = str(self.style_comboBox.currentText())
        self.persepolis_setting.setValue('style', style)

        if style != self.grandparent.persepolis_style:  # if style changed,then set new style
            self.grandparent.setPersepolisStyle(style)

# color_scheme
        color_scheme = self.color_comboBox.currentText()
        self.persepolis_setting.setValue('color-scheme', color_scheme)

        # if color_scheme changed , then set new color_scheme
        if color_scheme != self.grandparent.persepolis_color_scheme:
            self.grandparent.setPersepolisColorScheme(color_scheme)

# font and font size
        current_font = self.fontComboBox.currentFont()
        current_font = current_font.key()
        current_font = current_font.split(',')
        font = str(current_font[0])
        self.persepolis_setting.setValue('font', font)

        font_size = self.font_size_spinBox.value()
        self.persepolis_setting.setValue('font-size', font_size)

        # if font or font_size changed,set new font , font_size
        if self.grandparent.persepolis_font != font or int(self.grandparent.persepolis_font_size) != int(font_size):
            self.grandparent.setPersepolisFont(font, int(font_size))
            self.grandparent.setPersepolisStyle(style)
            self.grandparent.setPersepolisColorScheme(color_scheme)

# if user select qt notification  >> enable_system_tray icon
        if self.persepolis_setting.value('notification') == 'QT notification':
            self.enable_system_tray_checkBox.setChecked(True)

# enable_system_tray_checkBox
        if self.enable_system_tray_checkBox.isChecked() == True:
            self.persepolis_setting.setValue('tray-icon', 'yes')
            self.parent.system_tray_icon.show()
            self.parent.minimizeAction.setEnabled(True)
            self.parent.trayAction.setChecked(True)
        else:
            self.persepolis_setting.setValue('tray-icon', 'no')
            self.parent.system_tray_icon.hide()
            self.parent.minimizeAction.setEnabled(False)
            self.parent.trayAction.setChecked(False)

# after_download_checkBox
        if self.after_download_checkBox.isChecked() == True:
            self.persepolis_setting.setValue('after-dialog', 'yes')
        else:
            self.persepolis_setting.setValue('after-dialog', 'no')

# show_menubar_checkbox
        if self.show_menubar_checkbox.isChecked() == True:
            self.persepolis_setting.setValue('show-menubar', 'yes')
            self.parent.menubar.show()
            self.parent.toolBar2.hide()
            self.parent.showMenuBarAction.setChecked(True)

        else:
            self.persepolis_setting.setValue('show-menubar', 'no')
            self.parent.menubar.hide()
            self.parent.toolBar2.show()
            self.parent.showMenuBarAction.setChecked(False)

# show_sidepanel_checkbox
        if self.show_sidepanel_checkbox.isChecked() == True:
            self.persepolis_setting.setValue('show_sidepanel', 'yes')
            self.parent.category_tree_qwidget.show()
        else:
            self.persepolis_setting.setValue('show_sidepanel', 'no')
            self.parent.category_tree_qwidget.hide()

# show_progress_window_checkbox
        if self.show_progress_window_checkbox.isChecked() == True:
            self.persepolis_setting.setValue('show-progress', 'yes')
        else:
            self.persepolis_setting.setValue('show-progress', 'no')

        if self.startup_checkbox.isChecked() == True:
            self.persepolis_setting.setValue('startup', 'yes')

            if not(startup.checkstartup()):  # checking existance of Persepolis in  system's startup

                startup.addstartup()  # adding Persepolis to system's startup
        else:
            self.persepolis_setting.setValue('startup', 'no')

            if startup.checkstartup():  # checking existance of Persepolis in  system's startup

                startup.removestartup()  # removing Persepolis from system's startup


# this section  creates temporary download folder and download folder and
# download sub folders if they did not existed.


        download_path_temp = self.persepolis_setting.value(
            'download_path_temp')
        download_path = self.persepolis_setting.value('download_path')

        folder_list = [download_path_temp, download_path]

        if self.subfolder_checkBox.isChecked():
            self.persepolis_setting.setValue('subfolder', 'yes')

            for folder in ['Audios', 'Videos', 'Others', 'Documents', 'Compressed']:
                folder_list.append(os.path.join(download_path, folder))

        else:
            self.persepolis_setting.setValue('subfolder', 'no')

        for folder in folder_list:
            osCommands.makeDirs(folder)

        if self.enable_notifications_checkBox.isChecked() == True:
            self.persepolis_setting.setValue('sound', 'yes')
        else:
            self.persepolis_setting.setValue('sound', 'no')

        # applying changes
        self.persepolis_setting.endGroup()
        self.persepolis_setting.sync()
        self.close()
