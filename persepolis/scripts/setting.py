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
try:
    from PySide6.QtCore import Qt, QEvent, QTime, QSize, QPoint, QDir, QTranslator, QCoreApplication, QLocale
    from PySide6.QtWidgets import QFileDialog, QStyleFactory, QMessageBox, QTableWidgetItem
    from PySide6.QtGui import QFont, QKeySequence
except:
    from PyQt5.QtCore import Qt, QEvent, QTime, QSize, QPoint, QDir, QTranslator, QCoreApplication, QLocale
    from PyQt5.QtWidgets import QFileDialog, QStyleFactory, QMessageBox, QTableWidgetItem
    from PyQt5.QtGui import QFont, QKeySequence


from persepolis.constants import OS
from persepolis.gui.setting_ui import Setting_Ui, KeyCapturingWindow_Ui
from persepolis.scripts.useful_tools import returnDefaultSettings
from persepolis.scripts import osCommands
from persepolis.scripts import startup
import platform
import copy
import sys
import os

home_address = os.path.expanduser("~")
os_type = platform.system()


class KeyCapturingWindow(KeyCapturingWindow_Ui):
    def __init__(self, callback, persepolis_setting):
        super().__init__(persepolis_setting)
        self.persepolis_setting = persepolis_setting
        self.callback = callback

        self.ok_pushButton.clicked.connect(self.okPushButtonPressed)
        self.cancel_pushButton.clicked.connect(self.close)

        self.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress:
            if event.key():
                # show new keys in window
                self.capturedKeyLabel.setText(str(QKeySequence(event.modifiers() | event.key()).toString()))
        return super(KeyCapturingWindow, self).eventFilter(source, event)

    def okPushButtonPressed(self, button):
        # return new keys
        self.callback(self.capturedKeyLabel.text())
        self.close()

    def closeEvent(self, event):
        event.accept()


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

        if str(self.persepolis_setting.value('dont-check-certificate')) == 'yes':
            self.dont_check_certificate_checkBox.setChecked(True)
        else:
            self.dont_check_certificate_checkBox.setChecked(False)


        # add support for other languages
        locale = str(self.persepolis_setting.value('settings/locale'))
        QLocale.setDefault(QLocale(locale))
        self.translator = QTranslator()
        if self.translator.load(':/translations/locales/ui_' + locale, 'ts'):
            QCoreApplication.installTranslator(self.translator)

        # wait_queue
        wait_queue_list = self.persepolis_setting.value('wait-queue')
        try:
            q_time = QTime(int(wait_queue_list[0]), int(wait_queue_list[1]))
        except:
            q_time = QTime(0, 0)

        self.wait_queue_time.setTime(q_time)

        # change aria2 path
        self.aria2_path_pushButton.clicked.connect(self.changeAria2Path)
        self.aria2_path_checkBox.toggled.connect(self.ariaCheckBoxToggled)
        aria2_path = self.persepolis_setting.value('settings/aria2_path')

        self.aria2_path_lineEdit.setEnabled(False)
        if aria2_path != None:
            self.aria2_path_checkBox.setChecked(True)
            self.aria2_path_lineEdit.setText(str(aria2_path))

        self.ariaCheckBoxToggled('aria2')

        if os_type in OS.UNIX_LIKE:
            for widget in self.aria2_path_checkBox, self.aria2_path_lineEdit, self.aria2_path_pushButton:
                widget.hide()

        # save_as_tab
        self.download_folder_lineEdit.setText(
            str(self.persepolis_setting.value('download_path')))
        self.temp_download_lineEdit.setText(
            str(self.persepolis_setting.value('download_path_temp')))

        # subfolder
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
        # find available styles(It's depends on operating system and desktop environments).
        available_styles = QStyleFactory.keys()
        for style in available_styles:

            # 'bb10dark', 'GTK', 'gtk' styles may cause to crashing! Eliminate them!
            style_black_list = ['bb10dark', 'bb10bright', 'GTK', 'gtk', 'gtk2']

            if style not in style_black_list:
                self.style_comboBox.addItem(style)

        # System >> for system default style
        # when user select System for style section, the default system style is using.
        self.style_comboBox.addItem('System')

        current_style_index = self.style_comboBox.findText(
            str(self.persepolis_setting.value('style')))
        if current_style_index != -1:
            self.style_comboBox.setCurrentIndex(current_style_index)

        # available language
        available_language = ['en_US', 'fa_IR', 'ar', 'zh_CN', 'fr_FR', 'pl_PL', 'nl_NL', 'pt_BR', 'es_ES', 'hu', 'tr', 'tr_TR']
        for lang in available_language:
            self.lang_comboBox.addItem(str(QLocale(lang).nativeLanguageName()), lang)

        current_locale = self.lang_comboBox.findData(
            str(self.persepolis_setting.value('locale')))
        self.lang_comboBox.setCurrentIndex(current_locale)

        self.current_icon = self.persepolis_setting.value('icons')

        # icon size
        size = ['128', '64', '48', '32', '24', '16']

        self.icons_size_comboBox.addItems(size)
        current_icons_size_index = self.icons_size_comboBox.findText(
            str(self.persepolis_setting.value('toolbar_icon_size')))

        self.icons_size_comboBox.setCurrentIndex(current_icons_size_index)

        # call setDarkLightIcon if index is changed
        self.icons_size_comboBox.currentIndexChanged.connect(self.setDarkLightIcon)

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

        # start_persepolis_if_browser_executed_checkBox
        if str(self.persepolis_setting.value('browser-persepolis')) == 'yes':
            self.start_persepolis_if_browser_executed_checkBox.setChecked(True)
        else:
            self.start_persepolis_if_browser_executed_checkBox.setChecked(False)

        # hide window
        if str(self.persepolis_setting.value('hide-window')) == 'yes':
            self.hide_window_checkBox.setChecked(True)
        else:
            self.hide_window_checkBox.setChecked(False)

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

        # font_checkBox
        if str(self.persepolis_setting.value('custom-font')) == 'yes':
            self.font_checkBox.setChecked(True)
        else:
            self.font_checkBox.setChecked(False)

        self.fontCheckBoxState(self.font_checkBox)

        # keep_awake_checkBox
        if str(self.persepolis_setting.value('awake')) == 'yes':
            self.keep_awake_checkBox.setChecked(True)
        else:
            self.keep_awake_checkBox.setChecked(False)

        # columns_tab
        if str(self.persepolis_setting.value('column0')) == 'yes':
            self.column0_checkBox.setChecked(True)
        else:
            self.column0_checkBox.setChecked(False)

        if str(self.persepolis_setting.value('column1')) == 'yes':
            self.column1_checkBox.setChecked(True)
        else:
            self.column1_checkBox.setChecked(False)

        if str(self.persepolis_setting.value('column2')) == 'yes':
            self.column2_checkBox.setChecked(True)
        else:
            self.column2_checkBox.setChecked(False)

        if str(self.persepolis_setting.value('column3')) == 'yes':
            self.column3_checkBox.setChecked(True)
        else:
            self.column3_checkBox.setChecked(False)

        if str(self.persepolis_setting.value('column4')) == 'yes':
            self.column4_checkBox.setChecked(True)
        else:
            self.column4_checkBox.setChecked(False)

        if str(self.persepolis_setting.value('column5')) == 'yes':
            self.column5_checkBox.setChecked(True)
        else:
            self.column5_checkBox.setChecked(False)

        if str(self.persepolis_setting.value('column6')) == 'yes':
            self.column6_checkBox.setChecked(True)
        else:
            self.column6_checkBox.setChecked(False)

        if str(self.persepolis_setting.value('column7')) == 'yes':
            self.column7_checkBox.setChecked(True)
        else:
            self.column7_checkBox.setChecked(False)

        if str(self.persepolis_setting.value('column10')) == 'yes':
            self.column10_checkBox.setChecked(True)
        else:
            self.column10_checkBox.setChecked(False)

        if str(self.persepolis_setting.value('column11')) == 'yes':
            self.column11_checkBox.setChecked(True)
        else:
            self.column11_checkBox.setChecked(False)

        if str(self.persepolis_setting.value('column12')) == 'yes':
            self.column12_checkBox.setChecked(True)
        else:
            self.column12_checkBox.setChecked(False)

        # video_finder
        try:  # Integer casting may raise exception.
            self.max_links_spinBox.setValue(int(persepolis_setting.value('video_finder/max_links', 3)))
        except:
            pass

        # shortcuts
        self.qshortcuts_list = [self.parent.exitAction_shortcut,
                                self.parent.minimizeAction_shortcut,
                                self.parent.removeSelectedAction_shortcut,
                                self.parent.deleteSelectedAction_shortcut,
                                self.parent.moveUpSelectedAction_shortcut,
                                self.parent.moveDownSelectedAction_shortcut,
                                self.parent.addlinkAction_shortcut,
                                self.parent.videoFinderAddLinkAction_shortcut,
                                self.parent.addtextfileAction_shortcut]

        self.shortcuts_list = [self.parent.exitAction_shortcut.key().toString(),
                               self.parent.minimizeAction_shortcut.key().toString(),
                               self.parent.removeSelectedAction_shortcut.key().toString(),
                               self.parent.deleteSelectedAction_shortcut.key().toString(),
                               self.parent.moveUpSelectedAction_shortcut.key().toString(),
                               self.parent.moveDownSelectedAction_shortcut.key().toString(),
                               self.parent.addlinkAction_shortcut.key().toString(),
                               self.parent.videoFinderAddLinkAction_shortcut.key().toString(),
                               self.parent.addtextfileAction_shortcut.key().toString()]

        # add shortcuts to the shortcut_table
        j = 0
        for shortcut in self.shortcuts_list:
            item = QTableWidgetItem(shortcut)

            # align center
            item.setTextAlignment(0x0004 | 0x0080)

            # insert item in shortcut_table
            self.shortcut_table.setItem(j, 1, item)

            j = j + 1

        # If user doubleclicks on a row, then run showCaptureKeyboardWindow method
        self.shortcut_table.itemDoubleClicked.connect(self.showCaptureKeyboardWindow)

        # ok cancel default button
        self.cancel_pushButton.clicked.connect(self.close)
        self.defaults_pushButton.clicked.connect(
            self.defaultsPushButtonPressed)
        self.ok_pushButton.clicked.connect(self.okPushButtonPressed)

        # font_checkBox connect
        self.font_checkBox.stateChanged.connect(self.fontCheckBoxState)

        # saving initial value of self.persepolis_setting in self.first_key_value_dict
        # at the end! in the okPushButtonPressed method, first_key_value_dict will compared with second_key_value_dict.
        # if any thing changed , then a message box notify user about "some changes take effect after restarting persepolis".
        self.first_key_value_dict = {}
        for member in self.persepolis_setting.allKeys():
            self.first_key_value_dict[member] = str(self.persepolis_setting.value(member))


        # if style_comboBox is changed, self.styleComboBoxChanged is called.
        self.style_comboBox.currentIndexChanged.connect(self.styleComboBoxChanged)

        self.styleComboBoxChanged()

        self.color_comboBox.currentIndexChanged.connect(self.setDarkLightIcon)

        self.persepolis_setting.endGroup()

        # setting window size and position
        size = self.persepolis_setting.value(
            'PreferencesWindow/size', QSize(578, 565))
        position = self.persepolis_setting.value(
            'PreferencesWindow/position', QPoint(300, 300))

        self.resize(size)
        self.move(position)


    # run this method if user doubleclicks on an item in shortcut_table
    def showCaptureKeyboardWindow(self):

        # show KeyCapturingWindow
        keyboard_capture_window = KeyCapturingWindow(self.callBack, self.persepolis_setting)

        self.parent.capturekeywindows_list.append(keyboard_capture_window)
        self.parent.capturekeywindows_list[len(self.parent.capturekeywindows_list) - 1].show()

    def callBack(self, keys):
        # do nothing if keys is empty
        if not(keys):
            return

        # check that if shortcut used before.
        if keys in self.shortcuts_list:
            self.msgBox = QMessageBox()
            self.msgBox.setText(QCoreApplication.translate("setting_src_ui_tr", "<b><center>This shortcut has been used before!\
                    Use another one!</center></b>"))
            self.msgBox.setIcon(QMessageBox.Warning)
            reply = self.msgBox.exec_()

        # set new shortcut
        else:
            selected_row = self.shortcut_table.selectionModel().selectedRows()[0].row()

            item = QTableWidgetItem(keys)

            # align center
            item.setTextAlignment(0x0004 | 0x0080)

            # insert item in shortcut_table
            self.shortcut_table.setItem(selected_row, 1, item)

            # set keys in shortcuts_list
            self.shortcuts_list[selected_row] = keys

    # active color_comboBox only when user is select "Fusion" style.
    def styleComboBoxChanged(self, index=None):
        # clear color_comboBox
        self.color_comboBox.clear()

        # get current style
        selected_style = self.style_comboBox.currentText()

        if selected_style != 'Fusion':
            # color_comboBox item
            color_scheme = ['System']

            # add item
            self.color_comboBox.addItems(color_scheme)

            # set 'System' for color_scheme
            current_color_index = self.color_comboBox.findText('System')
            self.color_comboBox.setCurrentIndex(current_color_index)

            # disable color_comboBox
            self.color_comboBox.setEnabled(False)
        else:
            # enable color_comboBox
            self.color_comboBox.setEnabled(True)

            # color_comboBox items
            color_scheme = ['Dark Fusion', 'Light Fusion'] 

            # add items
            self.color_comboBox.addItems(color_scheme)

            current_color_index = self.color_comboBox.findText(
                str(self.persepolis_setting.value('color-scheme')))

            # it means user's preferred color_scheme is not valid in color_comboBox.
            if current_color_index == -1:
                current_color_index = 0

            self.color_comboBox.setCurrentIndex(current_color_index)

        self.setDarkLightIcon()

    # this method sets dark icons for dark color schemes
    # and light icons for light color schemes.
    def setDarkLightIcon(self, index=None):

        dark_theme = None

        # find selected style
        selected_style = self.style_comboBox.currentText()

        # clear icon_comboBox
        self.icon_comboBox.clear()

        # Papirus icons can be used with small sizes(smaller than 48)
        # get user's selected icons size
        selected_size = int(self.icons_size_comboBox.currentText())

        if selected_style == 'Fusion':
            if self.color_comboBox.currentText() == 'Dark Fusion':
                dark_theme = True
            else:
                dark_theme = False

        elif selected_style == 'Adwaita-Dark':
            dark_theme = True

        elif selected_style == 'Adwaita' or selected_style == 'macintosh':
            dark_theme = False

        if dark_theme == True:
            self.icon_comboBox.clear()

            if selected_size < 48:
                icons = ['Breeze-Dark', 'Papirus-Dark']
            else:
                icons = ['Breeze-Dark']
 
            self.icon_comboBox.addItems(icons)

            # current_icons_index is -1, if findText couldn't find icon index.
            current_icons_index = self.icon_comboBox.findText(
                str(self.persepolis_setting.value('icons', self.current_icon)))

            if current_icons_index == -1:
                current_icons_index = 0

            self.icon_comboBox.setCurrentIndex(current_icons_index)

        elif dark_theme == False:

            if selected_size < 48:
                icons = ['Breeze', 'Papirus', 'Papirus-Light']
            else:
                icons = ['Breeze', 'Papirus']


            self.icon_comboBox.addItems(icons)

            # current_icons_index is -1, if findText couldn't find icon index.
            current_icons_index = self.icon_comboBox.findText(
                str(self.persepolis_setting.value('icons', self.current_icon)))

            if current_icons_index == -1:
                current_icons_index = 0

            self.icon_comboBox.setCurrentIndex(current_icons_index)


        else:
            if selected_size < 48:
                icons = ['Breeze', 'Breeze-Dark', 'Papirus',
                        'Papirus-Dark', 'Papirus-Light']
            else:
                icons = ['Breeze', 'Breeze-Dark', 'Papirus']
 
            self.icon_comboBox.addItems(icons)

            # current_icons_index is -1, if findText couldn't find icon index.
            current_icons_index = self.icon_comboBox.findText(
                str(self.persepolis_setting.value('icons', self.current_icon)))

            if current_icons_index == -1:
                current_icons_index = 0

            self.icon_comboBox.setCurrentIndex(current_icons_index)


    def fontCheckBoxState(self, checkBox):

        # deactivate fontComboBox and font_size_spinBox if font_checkBox not checked!
        if self.font_checkBox.isChecked():
            self.fontComboBox.setEnabled(True)
            self.font_size_spinBox.setEnabled(True)
        else:
            self.fontComboBox.setEnabled(False)
            self.font_size_spinBox.setEnabled(False)

    # close window with ESC key
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


    def closeEvent(self, event):

        # saving window size and position
        self.persepolis_setting.setValue('PreferencesWindow/size', self.size())
        self.persepolis_setting.setValue(
            'PreferencesWindow/position', self.pos())
        self.persepolis_setting.sync()
        event.accept()

        if self.parent.isVisible() == False:
            self.parent.minMaxTray(event)
        self.close()

    def soundFrame(self, checkBox):

        if self.enable_notifications_checkBox.isChecked():
            self.sound_frame.setEnabled(True)
        else:
            self.sound_frame.setEnabled(False)

    def ariaCheckBoxToggled(self, checkBox):

        if self.aria2_path_checkBox.isChecked():
            self.aria2_path_pushButton.setEnabled(True)
        else:
            self.aria2_path_pushButton.setEnabled(False)

    def changeAria2Path(self, button):

        cwd = sys.argv[0]
        cwd = os.path.dirname(cwd)

        f_path, filters = QFileDialog.getOpenFileName(
            self, 'Select aria2 path', cwd)

        # if path is correct:
        if os.path.isfile(str(f_path)):
            self.aria2_path_lineEdit.setText(str(f_path))
        else:
            self.aria2_path_checkBox.setChecked(False)

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

        self.setting_dict = returnDefaultSettings()

        self.tries_spinBox.setValue(int(self.setting_dict['max-tries']))
        self.wait_spinBox.setValue(int(self.setting_dict['retry-wait']))
        self.time_out_spinBox.setValue(int(self.setting_dict['timeout']))
        self.connections_spinBox.setValue(
            int(self.setting_dict['connections']))

        self.rpc_port_spinbox.setValue(int(self.setting_dict['rpc-port']))
        self.aria2_path_lineEdit.setText('')
        self.aria2_path_checkBox.setChecked(False)

        # wait-queue
        wait_queue_list = self.setting_dict['wait-queue']
        q_time = QTime(wait_queue_list[0], wait_queue_list[1])
        self.wait_queue_time.setTime(q_time)

        # dont_check_certificate_checkBox
        self.dont_check_certificate_checkBox.setChecked(False)

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

        # set language
        current_locale = self.lang_comboBox.findData(
            str(self.setting_dict['locale']))
        self.lang_comboBox.setCurrentIndex(current_locale)

        # set color_scheme
        current_color_index = self.color_comboBox.findText(
            str(self.setting_dict['color-scheme']))
        self.color_comboBox.setCurrentIndex(current_color_index)

        # set icons
        current_icons_index = self.icon_comboBox.findText(
            str(self.setting_dict['icons']))
        self.icon_comboBox.setCurrentIndex(current_icons_index)

        # set icons size
        current_icons_size_index = self.icons_size_comboBox.findText(
            str(self.setting_dict['toolbar_icon_size']))
        self.icons_size_comboBox.setCurrentIndex(current_icons_size_index)

        # set notification
        current_notification_index = self.notification_comboBox.findText(
            str(self.setting_dict['notification']))
        self.notification_comboBox.setCurrentIndex(current_notification_index)

        # set font
        self.font_checkBox.setChecked(False)
        font_setting = QFont()
        font_setting.setFamily(str(self.setting_dict['font']))
        self.fontComboBox.setCurrentFont(font_setting)

        self.font_size_spinBox.setValue(int(self.setting_dict['font-size']))

        # sound frame
        self.enable_notifications_checkBox.setChecked(True)

        # start_persepolis_if_browser_executed_checkBox
        self.start_persepolis_if_browser_executed_checkBox.setChecked(True)

        # hide window
        self.hide_window_checkBox.setChecked(True)

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

        # keep_awake_checkBox
        self.keep_awake_checkBox.setChecked(False)

        # columns_tab
        self.column0_checkBox.setChecked(True)
        self.column1_checkBox.setChecked(True)
        self.column2_checkBox.setChecked(True)
        self.column3_checkBox.setChecked(True)
        self.column4_checkBox.setChecked(True)
        self.column5_checkBox.setChecked(True)
        self.column6_checkBox.setChecked(True)
        self.column7_checkBox.setChecked(True)
        self.column10_checkBox.setChecked(True)
        self.column11_checkBox.setChecked(True)
        self.column12_checkBox.setChecked(True)

        # video finder
        self.max_links_spinBox.setValue(3)

        # shortcuts
        self.shortcuts_list = [self.setting_dict['shortcuts/quit_shortcut'],
                               self.setting_dict['shortcuts/hide_window_shortcut'],
                               self.setting_dict['shortcuts/remove_shortcut'],
                               self.setting_dict['shortcuts/delete_shortcut'],
                               self.setting_dict['shortcuts/move_up_selection_shortcut'],
                               self.setting_dict['shortcuts/move_down_selection_shortcut'],
                               self.setting_dict['shortcuts/add_new_download_shortcut'],
                               self.setting_dict['shortcuts/video_finder_shortcut'],
                               self.setting_dict['shortcuts/import_text_shortcut']]

        # add shortcuts to the shortcut_table
        j = 0
        for shortcut in self.shortcuts_list:
            item = QTableWidgetItem(shortcut)

            # align center
            item.setTextAlignment(0x0004 | 0x0080)

            # insert item in shortcut_table
            self.shortcut_table.setItem(j, 1, item)

            j = j + 1

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
        self.persepolis_setting.setValue(
            'wait-queue', self.wait_queue_time.text().split(':'))

        # change aria2_path
        if self.aria2_path_checkBox.isChecked():
            self.persepolis_setting.setValue('settings/aria2_path', str(self.aria2_path_lineEdit.text()))

        # don't check certificate
        if self.dont_check_certificate_checkBox.isChecked():
            self.persepolis_setting.setValue('dont-check-certificate', 'yes')
        else:
            self.persepolis_setting.setValue('dont-check-certificate', 'no')



        # changing icons

        icons = self.icon_comboBox.currentText()
        self.persepolis_setting.setValue('icons', icons)

        if icons != self.current_icon:  # it means icons changed
            for windows_list in [self.parent.logwindow_list, self.parent.about_window_list,
                                 self.parent.addlinkwindows_list, self.parent.propertieswindows_list,
                                 self.parent.afterdownload_list, self.parent.text_queue_window_list,
                                 self.parent.progress_window_list, self.parent.plugin_queue_window_list]:

                for window in windows_list:
                    window.changeIcon(icons)

            self.parent.changeIcon(icons)

        # icons size
        icons_size = self.icons_size_comboBox.currentText()
        self.persepolis_setting.setValue('toolbar_icon_size', icons_size)

        icons_size = int(icons_size)
        self.parent.toolBar.setIconSize(QSize(icons_size, icons_size))
        self.parent.toolBar2.setIconSize(QSize(icons_size, icons_size))

        # style
        style = str(self.style_comboBox.currentText())
        self.persepolis_setting.setValue('style', style)

        # language
        locale = str(self.lang_comboBox.itemData(self.lang_comboBox.currentIndex()))
        self.persepolis_setting.setValue('locale', locale)

        # color_scheme
        color_scheme = self.color_comboBox.currentText()
        self.persepolis_setting.setValue('color-scheme', color_scheme)

        # font and font size
        current_font = self.fontComboBox.currentFont()
        current_font = current_font.key()
        current_font = current_font.split(',')
        font = str(current_font[0])
        self.persepolis_setting.setValue('font', font)

        font_size = self.font_size_spinBox.value()
        self.persepolis_setting.setValue('font-size', font_size)

        if self.font_checkBox.isChecked():
            custom_font = 'yes'
        else:
            custom_font = 'no'

        self.persepolis_setting.setValue('custom-font', custom_font)

        # if user select qt notification  >> enable_system_tray icon
        if self.persepolis_setting.value('notification') == 'QT notification':
            self.enable_system_tray_checkBox.setChecked(True)

        # start_persepolis_if_browser_executed_checkBox
        if self.start_persepolis_if_browser_executed_checkBox.isChecked():
            self.persepolis_setting.setValue('browser-persepolis', 'yes')
        else:
            self.persepolis_setting.setValue('browser-persepolis', 'no')

        # hide_window_checkBox
        if self.hide_window_checkBox.isChecked():
            self.persepolis_setting.setValue('hide-window', 'yes')
        else:
            self.persepolis_setting.setValue('hide-window', 'no')

        # enable_system_tray_checkBox
        if self.enable_system_tray_checkBox.isChecked():
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
        if self.after_download_checkBox.isChecked():
            self.persepolis_setting.setValue('after-dialog', 'yes')
        else:
            self.persepolis_setting.setValue('after-dialog', 'no')

        # show_menubar_checkbox
        if self.show_menubar_checkbox.isChecked():
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
        if self.show_sidepanel_checkbox.isChecked():
            self.persepolis_setting.setValue('show-sidepanel', 'yes')
            self.parent.category_tree_qwidget.show()
        else:
            self.persepolis_setting.setValue('show-sidepanel', 'no')
            self.parent.category_tree_qwidget.hide()

        # show_progress_window_checkbox
        if self.show_progress_window_checkbox.isChecked():
            self.persepolis_setting.setValue('show-progress', 'yes')
        else:
            self.persepolis_setting.setValue('show-progress', 'no')

        if self.startup_checkbox.isChecked():
            self.persepolis_setting.setValue('startup', 'yes')

            if not(startup.checkstartup()):  # checking existence of Persepolis in  system's startup

                startup.addstartup()  # adding Persepolis to system's startup
        else:
            self.persepolis_setting.setValue('startup', 'no')

            if startup.checkstartup():  # checking existence of Persepolis in  system's startup

                startup.removestartup()  # removing Persepolis from system's startup

        # keep_awake_checkBox
        if self.keep_awake_checkBox.isChecked():
            self.persepolis_setting.setValue('awake', 'yes')
            self.parent.keep_awake_checkBox.setChecked(True)
        else:
            self.persepolis_setting.setValue('awake', 'no')
            self.parent.keep_awake_checkBox.setChecked(False)

        # this section  creates temporary download folder and download folder and
        # download sub folders if they did not existed.

        download_path_temp = self.persepolis_setting.value(
            'download_path_temp')
        download_path = self.persepolis_setting.value('download_path')

        folder_list = [download_path_temp, download_path]

        if self.subfolder_checkBox.isChecked():
            self.persepolis_setting.setValue('subfolder', 'yes')

            for folder in ['Audios', 'Videos', 'Others', 'Documents', 'Compressed', 'Programs']:
                folder_list.append(os.path.join(download_path, folder))

        else:
            self.persepolis_setting.setValue('subfolder', 'no')

        for folder in folder_list:
            osCommands.makeDirs(folder)

        if self.enable_notifications_checkBox.isChecked():
            self.persepolis_setting.setValue('sound', 'yes')
        else:
            self.persepolis_setting.setValue('sound', 'no')

        # columns_tab
        if self.column0_checkBox.isChecked():
            self.persepolis_setting.setValue('column0', 'yes')
            self.parent.download_table.setColumnHidden(0, False)

            if self.parent.download_table.isColumnHidden(0):
                self.parent.download_table.setColumnWidth(0, 100)

        else:
            self.persepolis_setting.setValue('column0', 'no')
            self.parent.download_table.setColumnHidden(0, True)

        if self.column1_checkBox.isChecked():
            self.persepolis_setting.setValue('column1', 'yes')
            self.parent.download_table.setColumnHidden(1, False)

            if self.parent.download_table.isColumnHidden(1):
                self.parent.download_table.setColumnWidth(1, 100)

        else:
            self.persepolis_setting.setValue('column1', 'no')
            self.parent.download_table.setColumnHidden(1, True)

        if self.column2_checkBox.isChecked():
            self.persepolis_setting.setValue('column2', 'yes')
            self.parent.download_table.setColumnHidden(2, False)

            if self.parent.download_table.isColumnHidden(2):
                self.parent.download_table.setColumnWidth(2, 100)

        else:
            self.persepolis_setting.setValue('column2', 'no')
            self.parent.download_table.setColumnHidden(2, True)

        if self.column3_checkBox.isChecked():
            self.persepolis_setting.setValue('column3', 'yes')
            self.parent.download_table.setColumnHidden(3, False)

            if self.parent.download_table.isColumnHidden(3):
                self.parent.download_table.setColumnWidth(3, 100)

        else:
            self.persepolis_setting.setValue('column3', 'no')
            self.parent.download_table.setColumnHidden(3, True)

        if self.column4_checkBox.isChecked():
            self.persepolis_setting.setValue('column4', 'yes')
            self.parent.download_table.setColumnHidden(4, False)

            if self.parent.download_table.isColumnHidden(4):
                self.parent.download_table.setColumnWidth(4, 100)

        else:
            self.persepolis_setting.setValue('column4', 'no')
            self.parent.download_table.setColumnHidden(4, True)

        if self.column5_checkBox.isChecked():
            self.persepolis_setting.setValue('column5', 'yes')
            self.parent.download_table.setColumnHidden(5, False)

            if self.parent.download_table.isColumnHidden(5):
                self.parent.download_table.setColumnWidth(5, 100)

        else:
            self.persepolis_setting.setValue('column5', 'no')
            self.parent.download_table.setColumnHidden(5, True)

        if self.column6_checkBox.isChecked():
            self.persepolis_setting.setValue('column6', 'yes')
            self.parent.download_table.setColumnHidden(6, False)

            if self.parent.download_table.isColumnHidden(6):
                self.parent.download_table.setColumnWidth(6, 100)

        else:
            self.persepolis_setting.setValue('column6', 'no')
            self.parent.download_table.setColumnHidden(6, True)

        if self.column7_checkBox.isChecked():
            self.persepolis_setting.setValue('column7', 'yes')
            self.parent.download_table.setColumnHidden(7, False)

            if self.parent.download_table.isColumnHidden(7):
                self.parent.download_table.setColumnWidth(7, 100)

        else:
            self.persepolis_setting.setValue('column7', 'no')
            self.parent.download_table.setColumnHidden(7, True)

        if self.column10_checkBox.isChecked():
            self.persepolis_setting.setValue('column10', 'yes')
            self.parent.download_table.setColumnHidden(10, False)

            if self.parent.download_table.isColumnHidden(10):
                self.parent.download_table.setColumnWidth(10, 100)

        else:
            self.persepolis_setting.setValue('column10', 'no')
            self.parent.download_table.setColumnHidden(10, True)

        if self.column11_checkBox.isChecked():
            self.persepolis_setting.setValue('column11', 'yes')
            self.parent.download_table.setColumnHidden(11, False)

            if self.parent.download_table.isColumnHidden(11):
                self.parent.download_table.setColumnWidth(11, 100)

        else:
            self.persepolis_setting.setValue('column11', 'no')
            self.parent.download_table.setColumnHidden(11, True)

        if self.column12_checkBox.isChecked():
            self.persepolis_setting.setValue('column12', 'yes')
            self.parent.download_table.setColumnHidden(12, False)

            if self.parent.download_table.isColumnHidden(12):
                self.parent.download_table.setColumnWidth(12, 100)

        else:
            self.persepolis_setting.setValue('column12', 'no')
            self.parent.download_table.setColumnHidden(12, True)

        # shortcuts
        # set new shortcuts
        i = 0
        for qshortcut in self.qshortcuts_list:
            # set keys for QShortcut
            qshortcut.setKey(self.shortcuts_list[i])

            i = i + 1

        # video_finder
        self.persepolis_setting.setValue('video_finder/max_links', self.max_links_spinBox.value())

        # saving value of persepolis_setting in second_key_value_dict.
        self.second_key_value_dict = {}
        for member in self.persepolis_setting.allKeys():
            self.second_key_value_dict[member] = str(self.persepolis_setting.value(member))

        # comparing first_key_value_dict with second_key_value_dict
        show_message_box = False
        for key in self.first_key_value_dict.keys():
            if self.first_key_value_dict[key] != self.second_key_value_dict[key]:
                if key in ['locale', 'aria2_path', 'download_path_temp', 'download_path', 'custom-font', 'rpc-port', 'max-tries', 'retry-wait', 'timeout', 'connections', 'style', 'font', 'font-size', 'color-scheme']:
                    show_message_box = True

        # if any thing changed that needs restarting, then notify user about "Some changes take effect after restarting persepolis"
        if show_message_box:
            restart_messageBox = QMessageBox()
            restart_messageBox.setText(QCoreApplication.translate(
                "setting_src_ui_tr", '<b><center>Restart Persepolis Please!</center></b><br><center>Some changes take effect after restarting Persepolis</center>'))
            restart_messageBox.setWindowTitle(QCoreApplication.translate("setting_src_ui_tr", 'Restart Persepolis!'))
            restart_messageBox.exec_()

        # applying changes
        self.persepolis_setting.endGroup()
        self.persepolis_setting.sync()

        self.close()
