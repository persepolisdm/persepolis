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
    from PySide6.QtWidgets import QAbstractItemView, QTableWidget, QTableWidgetItem, QCheckBox, QVBoxLayout, QHBoxLayout, QFrame, QWidget, QLabel, QLineEdit, QTabWidget, QSpinBox, QPushButton, QDial, QComboBox, QFontComboBox, QSpacerItem, QSizePolicy
    from PySide6.QtCore import Qt, QTranslator, QCoreApplication, QLocale
    from PySide6.QtGui import QIcon
except:
    from PyQt5.QtWidgets import QAbstractItemView, QTableWidget, QTableWidgetItem, QCheckBox, QVBoxLayout, QHBoxLayout, QFrame, QWidget, QLabel, QLineEdit, QTabWidget, QSpinBox, QPushButton, QDial, QComboBox, QFontComboBox, QSpacerItem, QSizePolicy
    from PyQt5.QtCore import Qt, QTranslator, QCoreApplication, QLocale
    from PyQt5.QtGui import QIcon

from persepolis.gui.customized_widgets import MyQDateTimeEdit
from persepolis.gui import resources

class KeyCapturingWindow_Ui(QWidget):
    def __init__(self, persepolis_setting):
        super().__init__()
        icon = QIcon()

        self.persepolis_setting = persepolis_setting

        # add support for other languages
        locale = str(self.persepolis_setting.value('settings/locale'))
        QLocale.setDefault(QLocale(locale))
        self.translator = QTranslator()
        if self.translator.load(':/translations/locales/ui_' + locale, 'ts'):
            QCoreApplication.installTranslator(self.translator)

        self.setWindowIcon(QIcon.fromTheme('persepolis', QIcon(':/com.github.persepolisdm.persepolis.svg')))
        self.setWindowTitle(QCoreApplication.translate("setting_ui_tr", 'Preferences'))

        # set ui direction
        ui_direction = self.persepolis_setting.value('ui_direction')

        if ui_direction == 'rtl':
            self.setLayoutDirection(Qt.RightToLeft)

        elif ui_direction in 'ltr':
            self.setLayoutDirection(Qt.LeftToRight)

        global icons
        icons = ':/' + str(self.persepolis_setting.value('settings/icons')) + '/'

        window_verticalLayout = QVBoxLayout(self)

        self.pressKeyLabel = QLabel(self)
        window_verticalLayout.addWidget(self.pressKeyLabel)

        self.capturedKeyLabel = QLabel(self)
        window_verticalLayout.addWidget(self.capturedKeyLabel)

        # window buttons
        buttons_horizontalLayout = QHBoxLayout()
        buttons_horizontalLayout.addStretch(1)

        self.cancel_pushButton = QPushButton(self)
        self.cancel_pushButton.setIcon(QIcon(icons + 'remove'))
        buttons_horizontalLayout.addWidget(self.cancel_pushButton)

        self.ok_pushButton = QPushButton(self)
        self.ok_pushButton.setIcon(QIcon(icons + 'ok'))
        buttons_horizontalLayout.addWidget(self.ok_pushButton)

        window_verticalLayout.addLayout(buttons_horizontalLayout)

        # labels
        self.pressKeyLabel.setText(QCoreApplication.translate("setting_ui_tr", "Press new keys"))
        self.cancel_pushButton.setText(QCoreApplication.translate("setting_ui_tr", "Cancel"))
        self.ok_pushButton.setText(QCoreApplication.translate("setting_ui_tr", "OK"))


class Setting_Ui(QWidget):
    def __init__(self, persepolis_setting):
        super().__init__()
        icon = QIcon()

        self.persepolis_setting = persepolis_setting

        # add support for other languages
        locale = str(self.persepolis_setting.value('settings/locale'))
        QLocale.setDefault(QLocale(locale))
        self.translator = QTranslator()
        if self.translator.load(':/translations/locales/ui_' + locale, 'ts'):
            QCoreApplication.installTranslator(self.translator)

        self.setWindowIcon(QIcon.fromTheme('persepolis', QIcon(':/com.github.persepolisdm.persepolis.svg')))
        self.setWindowTitle(QCoreApplication.translate("setting_ui_tr", 'Preferences'))

        # set ui direction
        ui_direction = self.persepolis_setting.value('ui_direction')

        if ui_direction == 'rtl':
            self.setLayoutDirection(Qt.RightToLeft)

        elif ui_direction in 'ltr':
            self.setLayoutDirection(Qt.LeftToRight)

        global icons
        icons = ':/' + str(self.persepolis_setting.value('settings/icons')) + '/'

        # main layout
        window_verticalLayout = QVBoxLayout(self)

        # setting_tabWidget
        self.setting_tabWidget = QTabWidget(self)

        # download_options_tab
        self.download_options_tab = QWidget()
        download_options_tab_verticalLayout = QVBoxLayout(self.download_options_tab)
        download_options_tab_verticalLayout.setContentsMargins(21, 21, 0, 0)

        # tries
        tries_horizontalLayout = QHBoxLayout()

        self.tries_label = QLabel(self.download_options_tab)
        tries_horizontalLayout.addWidget(self.tries_label)

        self.tries_spinBox = QSpinBox(self.download_options_tab)
        self.tries_spinBox.setMinimum(1)

        tries_horizontalLayout.addWidget(self.tries_spinBox)
        download_options_tab_verticalLayout.addLayout(tries_horizontalLayout)

        # wait
        wait_horizontalLayout = QHBoxLayout()

        self.wait_label = QLabel(self.download_options_tab)
        wait_horizontalLayout.addWidget(self.wait_label)

        self.wait_spinBox = QSpinBox(self.download_options_tab)
        wait_horizontalLayout.addWidget(self.wait_spinBox)

        download_options_tab_verticalLayout.addLayout(wait_horizontalLayout)

        # time_out
        time_out_horizontalLayout = QHBoxLayout()

        self.time_out_label = QLabel(self.download_options_tab)
        time_out_horizontalLayout.addWidget(self.time_out_label)

        self.time_out_spinBox = QSpinBox(self.download_options_tab)
        time_out_horizontalLayout.addWidget(self.time_out_spinBox)

        download_options_tab_verticalLayout.addLayout(time_out_horizontalLayout)

        # connections
        connections_horizontalLayout = QHBoxLayout()

        self.connections_label = QLabel(self.download_options_tab)
        connections_horizontalLayout.addWidget(self.connections_label)

        self.connections_spinBox = QSpinBox(self.download_options_tab)
        self.connections_spinBox.setMinimum(1)
        self.connections_spinBox.setMaximum(16)
        connections_horizontalLayout.addWidget(self.connections_spinBox)

        download_options_tab_verticalLayout.addLayout(connections_horizontalLayout)

        # rpc_port
        self.rpc_port_label = QLabel(self.download_options_tab)
        self.rpc_horizontalLayout = QHBoxLayout()
        self.rpc_horizontalLayout.addWidget(self.rpc_port_label)

        self.rpc_port_spinbox = QSpinBox(self.download_options_tab)
        self.rpc_port_spinbox.setMinimum(1024)
        self.rpc_port_spinbox.setMaximum(65535)
        self.rpc_horizontalLayout.addWidget(self.rpc_port_spinbox)

        download_options_tab_verticalLayout.addLayout(
            self.rpc_horizontalLayout)

        # wait_queue
        wait_queue_horizontalLayout = QHBoxLayout()

        self.wait_queue_label = QLabel(self.download_options_tab)
        wait_queue_horizontalLayout.addWidget(self.wait_queue_label)

        self.wait_queue_time = MyQDateTimeEdit(self.download_options_tab)
        self.wait_queue_time.setDisplayFormat('H:mm')
        wait_queue_horizontalLayout.addWidget(self.wait_queue_time)

        download_options_tab_verticalLayout.addLayout(
            wait_queue_horizontalLayout)

        # don't check certificate checkBox
        self.dont_check_certificate_checkBox = QCheckBox(self.download_options_tab)
        download_options_tab_verticalLayout.addWidget(self.dont_check_certificate_checkBox)

        # change aria2 path
        aria2_path_verticalLayout = QVBoxLayout()

        self.aria2_path_checkBox = QCheckBox(self.download_options_tab)
        aria2_path_verticalLayout.addWidget(self.aria2_path_checkBox)

        aria2_path_horizontalLayout = QHBoxLayout()

        self.aria2_path_lineEdit = QLineEdit(self.download_options_tab)
        aria2_path_horizontalLayout.addWidget(self.aria2_path_lineEdit)

        self.aria2_path_pushButton = QPushButton(self.download_options_tab)
        aria2_path_horizontalLayout.addWidget(self.aria2_path_pushButton)

        aria2_path_verticalLayout.addLayout(aria2_path_horizontalLayout)

        download_options_tab_verticalLayout.addLayout(aria2_path_verticalLayout)

        download_options_tab_verticalLayout.addStretch(1)

        self.setting_tabWidget.addTab(self.download_options_tab, "")

        # save_as_tab
        self.save_as_tab = QWidget()

        save_as_tab_verticalLayout = QVBoxLayout(self.save_as_tab)
        save_as_tab_verticalLayout.setContentsMargins(20, 30, 0, 0)

        # download_folder
        self.download_folder_horizontalLayout = QHBoxLayout()

        self.download_folder_label = QLabel(self.save_as_tab)
        self.download_folder_horizontalLayout.addWidget(
            self.download_folder_label)

        self.download_folder_lineEdit = QLineEdit(self.save_as_tab)
        self.download_folder_horizontalLayout.addWidget(self.download_folder_lineEdit)

        self.download_folder_pushButton = QPushButton(self.save_as_tab)
        self.download_folder_horizontalLayout.addWidget(self.download_folder_pushButton)

        save_as_tab_verticalLayout.addLayout(self.download_folder_horizontalLayout)

        # temp_download_folder
        self.temp_horizontalLayout = QHBoxLayout()

        self.temp_download_label = QLabel(self.save_as_tab)
        self.temp_horizontalLayout.addWidget(self.temp_download_label)

        self.temp_download_lineEdit = QLineEdit(self.save_as_tab)
        self.temp_horizontalLayout.addWidget(self.temp_download_lineEdit)

        self.temp_download_pushButton = QPushButton(self.save_as_tab)
        self.temp_horizontalLayout.addWidget(self.temp_download_pushButton)

        save_as_tab_verticalLayout.addLayout(self.temp_horizontalLayout)

        # create subfolder
        self.subfolder_checkBox = QCheckBox(self.save_as_tab)
        save_as_tab_verticalLayout.addWidget(self.subfolder_checkBox)

        save_as_tab_verticalLayout.addStretch(1)

        self.setting_tabWidget.addTab(self.save_as_tab, "")

        # notifications_tab
        self.notifications_tab = QWidget()
        notification_tab_verticalLayout = QVBoxLayout(self.notifications_tab)
        notification_tab_verticalLayout.setContentsMargins(21, 21, 0, 0)

        self.enable_notifications_checkBox = QCheckBox(self.notifications_tab)
        notification_tab_verticalLayout.addWidget(self.enable_notifications_checkBox)

        self.sound_frame = QFrame(self.notifications_tab)
        self.sound_frame.setFrameShape(QFrame.StyledPanel)
        self.sound_frame.setFrameShadow(QFrame.Raised)

        verticalLayout = QVBoxLayout(self.sound_frame)

        self.volume_label = QLabel(self.sound_frame)
        verticalLayout.addWidget(self.volume_label)

        self.volume_dial = QDial(self.sound_frame)
        self.volume_dial.setProperty("value", 100)
        verticalLayout.addWidget(self.volume_dial)

        notification_tab_verticalLayout.addWidget(self.sound_frame)

        # message_notification
        message_notification_horizontalLayout = QHBoxLayout()
        self.notification_label = QLabel(self.notifications_tab)
        message_notification_horizontalLayout.addWidget(self.notification_label)

        self.notification_comboBox = QComboBox(self.notifications_tab)
        message_notification_horizontalLayout.addWidget(self.notification_comboBox)
        notification_tab_verticalLayout.addLayout(message_notification_horizontalLayout)

        notification_tab_verticalLayout.addStretch(1)

        self.setting_tabWidget.addTab(self.notifications_tab, "")

        # style_tab
        self.style_tab = QWidget()
        style_tab_verticalLayout = QVBoxLayout(self.style_tab)
        style_tab_verticalLayout.setContentsMargins(21, 21, 0, 0)

        # style
        style_horizontalLayout = QHBoxLayout()

        self.style_label = QLabel(self.style_tab)
        style_horizontalLayout.addWidget(self.style_label)

        self.style_comboBox = QComboBox(self.style_tab)
        style_horizontalLayout.addWidget(self.style_comboBox)

        style_tab_verticalLayout.addLayout(style_horizontalLayout)

        # language
        language_horizontalLayout = QHBoxLayout()

        self.lang_label = QLabel(self.style_tab)
        language_horizontalLayout.addWidget(self.lang_label)
        self.lang_comboBox = QComboBox(self.style_tab)
        language_horizontalLayout.addWidget(self.lang_comboBox)

        style_tab_verticalLayout.addLayout(language_horizontalLayout)
        language_horizontalLayout = QHBoxLayout()
        self.lang_label.setText(QCoreApplication.translate("setting_ui_tr", "Language: "))

        # color scheme
        self.color_label = QLabel(self.style_tab)
        language_horizontalLayout.addWidget(self.color_label)

        self.color_comboBox = QComboBox(self.style_tab)
        language_horizontalLayout.addWidget(self.color_comboBox)

        style_tab_verticalLayout.addLayout(language_horizontalLayout)

        # icons
        icons_horizontalLayout = QHBoxLayout()
        self.icon_label = QLabel(self.style_tab)
        icons_horizontalLayout.addWidget(self.icon_label)

        self.icon_comboBox = QComboBox(self.style_tab)
        icons_horizontalLayout.addWidget(self.icon_comboBox)

        style_tab_verticalLayout.addLayout(icons_horizontalLayout)

        self.icons_size_horizontalLayout = QHBoxLayout()
        self.icons_size_label = QLabel(self.style_tab)
        self.icons_size_horizontalLayout.addWidget(self.icons_size_label)

        self.icons_size_comboBox = QComboBox(self.style_tab)
        self.icons_size_horizontalLayout.addWidget(self.icons_size_comboBox)

        style_tab_verticalLayout.addLayout(self.icons_size_horizontalLayout)

        # font
        font_horizontalLayout = QHBoxLayout()
        self.font_checkBox = QCheckBox(self.style_tab)
        font_horizontalLayout.addWidget(self.font_checkBox)

        self.fontComboBox = QFontComboBox(self.style_tab)
        font_horizontalLayout.addWidget(self.fontComboBox)

        self.font_size_label = QLabel(self.style_tab)
        font_horizontalLayout.addWidget(self.font_size_label)

        self.font_size_spinBox = QSpinBox(self.style_tab)
        self.font_size_spinBox.setMinimum(1)
        font_horizontalLayout.addWidget(self.font_size_spinBox)

        style_tab_verticalLayout.addLayout(font_horizontalLayout)
        self.setting_tabWidget.addTab(self.style_tab, "")
        window_verticalLayout.addWidget(self.setting_tabWidget)

        # start persepolis in system tray if browser executed
        self.start_persepolis_if_browser_executed_checkBox = QCheckBox(self.style_tab)
        style_tab_verticalLayout.addWidget(self.start_persepolis_if_browser_executed_checkBox)

        # hide window if close button clicked
        self.hide_window_checkBox = QCheckBox(self.style_tab)
        style_tab_verticalLayout.addWidget(self.hide_window_checkBox)

        # Enable system tray icon
        self.enable_system_tray_checkBox = QCheckBox(self.style_tab)
        style_tab_verticalLayout.addWidget(self.enable_system_tray_checkBox)

        # after_download dialog
        self.after_download_checkBox = QCheckBox()
        style_tab_verticalLayout.addWidget(self.after_download_checkBox)

        # show_menubar_checkbox
        self.show_menubar_checkbox = QCheckBox()
        style_tab_verticalLayout.addWidget(self.show_menubar_checkbox)

        # show_sidepanel_checkbox
        self.show_sidepanel_checkbox = QCheckBox()
        style_tab_verticalLayout.addWidget(self.show_sidepanel_checkbox)

        # hide progress window
        self.show_progress_window_checkbox = QCheckBox()
        style_tab_verticalLayout.addWidget(self.show_progress_window_checkbox)

        # add persepolis to startup
        self.startup_checkbox = QCheckBox()
        style_tab_verticalLayout.addWidget(self.startup_checkbox)

        # keep system awake
        self.keep_awake_checkBox = QCheckBox()
        style_tab_verticalLayout.addWidget(self.keep_awake_checkBox)

        style_tab_verticalLayout.addStretch(1)

        # columns_tab
        self.columns_tab = QWidget()

        columns_tab_verticalLayout = QVBoxLayout(self.columns_tab)
        columns_tab_verticalLayout.setContentsMargins(21, 21, 0, 0)

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

        columns_tab_verticalLayout.addWidget(self.show_column_label)
        columns_tab_verticalLayout.addWidget(self.column0_checkBox)
        columns_tab_verticalLayout.addWidget(self.column1_checkBox)
        columns_tab_verticalLayout.addWidget(self.column2_checkBox)
        columns_tab_verticalLayout.addWidget(self.column3_checkBox)
        columns_tab_verticalLayout.addWidget(self.column4_checkBox)
        columns_tab_verticalLayout.addWidget(self.column5_checkBox)
        columns_tab_verticalLayout.addWidget(self.column6_checkBox)
        columns_tab_verticalLayout.addWidget(self.column7_checkBox)
        columns_tab_verticalLayout.addWidget(self.column10_checkBox)
        columns_tab_verticalLayout.addWidget(self.column11_checkBox)
        columns_tab_verticalLayout.addWidget(self.column12_checkBox)

        columns_tab_verticalLayout.addStretch(1)

        self.setting_tabWidget.addTab(self.columns_tab, '')

        # video_finder_tab
        self.video_finder_tab = QWidget()

        video_finder_layout = QVBoxLayout(self.video_finder_tab)
        video_finder_layout.setContentsMargins(21, 21, 0, 0)

        video_finder_tab_verticalLayout = QVBoxLayout()

        max_links_horizontalLayout = QHBoxLayout()

        # max_links_label
        self.max_links_label = QLabel(self.video_finder_tab)

        max_links_horizontalLayout.addWidget(self.max_links_label)

        # max_links_spinBox
        self.max_links_spinBox = QSpinBox(self.video_finder_tab)
        self.max_links_spinBox.setMinimum(1)
        self.max_links_spinBox.setMaximum(16)
        max_links_horizontalLayout.addWidget(self.max_links_spinBox)
        video_finder_tab_verticalLayout.addLayout(max_links_horizontalLayout)

        self.video_finder_dl_path_horizontalLayout = QHBoxLayout()

        self.video_finder_frame = QFrame(self.video_finder_tab)
        self.video_finder_frame.setLayout(video_finder_tab_verticalLayout)

        video_finder_tab_verticalLayout.addStretch(1)

        video_finder_layout.addWidget(self.video_finder_frame)

        self.setting_tabWidget.addTab(self.video_finder_tab, "")

        # shortcut tab
        self.shortcut_tab = QWidget()
        shortcut_tab_verticalLayout = QVBoxLayout(self.shortcut_tab)
        shortcut_tab_verticalLayout.setContentsMargins(21, 21, 0, 0)

        # shortcut_table
        self.shortcut_table = QTableWidget(self)
        self.shortcut_table.setColumnCount(2)
        self.shortcut_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.shortcut_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.shortcut_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.shortcut_table.verticalHeader().hide()

        shortcut_table_header = [QCoreApplication.translate("setting_ui_tr", 'Action'),
                                 QCoreApplication.translate("setting_ui_tr", 'Shortcut')]

        self.shortcut_table.setHorizontalHeaderLabels(shortcut_table_header)

        shortcut_tab_verticalLayout.addWidget(self.shortcut_table)

        self.setting_tabWidget.addTab(self.shortcut_tab, QCoreApplication.translate("setting_ui_tr", "Shortcuts"))

        # Actions
        actions_list = [QCoreApplication.translate('setting_ui_tr', 'Quit'),
                        QCoreApplication.translate('setting_ui_tr', 'Minimize to System Tray'),
                        QCoreApplication.translate('setting_ui_tr', 'Remove Download Items'),
                        QCoreApplication.translate('setting_ui_tr', 'Delete Download Items'),
                        QCoreApplication.translate('setting_ui_tr', 'Move Selected Items Up'),
                        QCoreApplication.translate('setting_ui_tr', 'Move Selected Items Down'),
                        QCoreApplication.translate('setting_ui_tr', 'Add New Download Link'),
                        QCoreApplication.translate('setting_ui_tr', 'Add New Video Link'),
                        QCoreApplication.translate('setting_ui_tr', 'Import Links from Text File')]

        # add actions to the shortcut_table
        j = 0
        for action in actions_list:
            item = QTableWidgetItem(str(action))

            # align center
            item.setTextAlignment(0x0004 | 0x0080)

            # insert item in shortcut_table
            self.shortcut_table.insertRow(j)
            self.shortcut_table.setItem(j, 0, item)

            j = j + 1

        self.shortcut_table.resizeColumnsToContents()

        # window buttons
        buttons_horizontalLayout = QHBoxLayout()
        buttons_horizontalLayout.addStretch(1)

        self.defaults_pushButton = QPushButton(self)
        buttons_horizontalLayout.addWidget(self.defaults_pushButton)

        self.cancel_pushButton = QPushButton(self)
        self.cancel_pushButton.setIcon(QIcon(icons + 'remove'))
        buttons_horizontalLayout.addWidget(self.cancel_pushButton)

        self.ok_pushButton = QPushButton(self)
        self.ok_pushButton.setIcon(QIcon(icons + 'ok'))
        buttons_horizontalLayout.addWidget(self.ok_pushButton)

        window_verticalLayout.addLayout(buttons_horizontalLayout)

        # set style_tab for default
        self.setting_tabWidget.setCurrentIndex(3)

        # labels and translations
        self.setWindowTitle(QCoreApplication.translate("setting_ui_tr", "Preferences"))

        self.tries_label.setToolTip(
            QCoreApplication.translate("setting_ui_tr", "<html><head/><body><p>Set number of tries if download failed.</p></body></html>"))
        self.tries_label.setText(QCoreApplication.translate("setting_ui_tr", "Number of tries: "))
        self.tries_spinBox.setToolTip(
            QCoreApplication.translate("setting_ui_tr", "<html><head/><body><p>Set number of tries if download failed.</p></body></html>"))

        self.wait_label.setToolTip(
            QCoreApplication.translate("setting_ui_tr", "<html><head/><body><p>Set the seconds to wait between retries. Download manager will  retry  downloads  when  the  HTTP  server  returns  a  503 response.</p></body></html>"))
        self.wait_label.setText(QCoreApplication.translate("setting_ui_tr", "Wait period between retries (seconds): "))
        self.wait_spinBox.setToolTip(
            QCoreApplication.translate("setting_ui_tr", "<html><head/><body><p>Set the seconds to wait between retries. Download manager will  retry  downloads  when  the  HTTP  server  returns  a  503 response.</p></body></html>"))

        self.time_out_label.setToolTip(
            QCoreApplication.translate("setting_ui_tr", "<html><head/><body><p>Set timeout in seconds. </p></body></html>"))
        self.time_out_label.setText(QCoreApplication.translate("setting_ui_tr", "Timeout (seconds): "))
        self.time_out_spinBox.setToolTip(
            QCoreApplication.translate("setting_ui_tr", "<html><head/><body><p>Set timeout in seconds. </p></body></html>"))

        self.connections_label.setToolTip(
            QCoreApplication.translate("setting_ui_tr", "<html><head/><body><p>Using multiple connections can help speed up your download.</p></body></html>"))
        self.connections_label.setText(QCoreApplication.translate("setting_ui_tr", "Number of connections: "))
        self.connections_spinBox.setToolTip(
            QCoreApplication.translate("setting_ui_tr", "<html><head/><body><p>Using multiple connections can help speed up your download.</p></body></html>"))

        self.rpc_port_label.setText(QCoreApplication.translate("setting_ui_tr", "RPC port number: "))
        self.rpc_port_spinbox.setToolTip(
            QCoreApplication.translate("setting_ui_tr", "<html><head/><body><p> Specify a port number for JSON-RPC/XML-RPC server to listen to. Possible Values: 1024 - 65535 Default: 6801 </p></body></html>"))

        self.wait_queue_label.setText(QCoreApplication.translate(
            "setting_ui_tr", 'Wait period between each download in queue:'))

        self.dont_check_certificate_checkBox.setText(QCoreApplication.translate("setting_ui_tr", "Don't use certificate to verify the peers"))
        self.dont_check_certificate_checkBox.setToolTip(
                QCoreApplication.translate("setting_ui_tr", "<html><head/><body><p>This option avoids SSL/TLS handshake failure. But use it at your own risk!</p></body></html>"))

        self.aria2_path_checkBox.setText(QCoreApplication.translate("setting_ui_tr", 'Change Aria2 default path'))
        self.aria2_path_pushButton.setText(QCoreApplication.translate("setting_ui_tr", 'Change'))
        aria2_path_tooltip = QCoreApplication.translate(
            "setting_ui_tr", "<html><head/><body><p>Attention: Wrong path may cause problems! Do it carefully or don't change default setting!</p></body></html>")
        self.aria2_path_checkBox.setToolTip(aria2_path_tooltip)
        self.aria2_path_lineEdit.setToolTip(aria2_path_tooltip)
        self.aria2_path_pushButton.setToolTip(aria2_path_tooltip)

        self.setting_tabWidget.setTabText(self.setting_tabWidget.indexOf(
            self.download_options_tab),  QCoreApplication.translate("setting_ui_tr", "Download Options"))

        self.download_folder_label.setText(QCoreApplication.translate("setting_ui_tr", "Download folder: "))
        self.download_folder_pushButton.setText(QCoreApplication.translate("setting_ui_tr", "Change"))

        self.temp_download_label.setText(QCoreApplication.translate("setting_ui_tr", "Temporary download folder: "))
        self.temp_download_pushButton.setText(QCoreApplication.translate("setting_ui_tr", "Change"))

        self.subfolder_checkBox.setText(QCoreApplication.translate(
            "setting_ui_tr", "Create subfolders for Music,Videos, ... in default download folder"))

        self.setting_tabWidget.setTabText(
            self.setting_tabWidget.indexOf(self.save_as_tab),  QCoreApplication.translate("setting_ui_tr", "Save As"))

        self.enable_notifications_checkBox.setText(
            QCoreApplication.translate("setting_ui_tr", "Enable Notification Sounds"))

        self.volume_label.setText(QCoreApplication.translate("setting_ui_tr", "Volume: "))

        self.setting_tabWidget.setTabText(self.setting_tabWidget.indexOf(
            self.notifications_tab),  QCoreApplication.translate("setting_ui_tr", "Notifications"))

        self.style_label.setText(QCoreApplication.translate("setting_ui_tr", "Style: "))
        self.color_label.setText(QCoreApplication.translate("setting_ui_tr", "Color scheme: "))
        self.icon_label.setText(QCoreApplication.translate("setting_ui_tr", "Icons: "))

        self.icons_size_label.setText(QCoreApplication.translate("setting_ui_tr", "Toolbar icons size: "))

        self.notification_label.setText(QCoreApplication.translate("setting_ui_tr", "Notification type: "))

        self.font_checkBox.setText(QCoreApplication.translate("setting_ui_tr", "Font: "))
        self.font_size_label.setText(QCoreApplication.translate("setting_ui_tr", "Size: "))

        self.hide_window_checkBox.setText(QCoreApplication.translate(
            "setting_ui_tr", "Hide main window if close button clicked."))
        self.hide_window_checkBox.setToolTip(
            QCoreApplication.translate("setting_ui_tr", "<html><head/><body><p>This feature may not work in your operating system.</p></body></html>"))

        self.start_persepolis_if_browser_executed_checkBox.setText(
            QCoreApplication.translate('setting_ui_tr', 'If browser is opened, start Persepolis in system tray'))

        self.enable_system_tray_checkBox.setText(
            QCoreApplication.translate("setting_ui_tr", "Enable system tray icon"))

        self.after_download_checkBox.setText(
            QCoreApplication.translate("setting_ui_tr", "Show download complete dialog when download is finished"))

        self.show_menubar_checkbox.setText(QCoreApplication.translate("setting_ui_tr", "Show menubar"))
        self.show_sidepanel_checkbox.setText(QCoreApplication.translate("setting_ui_tr", "Show side panel"))
        self.show_progress_window_checkbox.setText(
            QCoreApplication.translate("setting_ui_tr", "Show download progress window"))

        self.startup_checkbox.setText(QCoreApplication.translate("setting_ui_tr", "Run Persepolis at startup"))

        self.keep_awake_checkBox.setText(QCoreApplication.translate("setting_ui_tr", "Keep system awake!"))
        self.keep_awake_checkBox.setToolTip(
            QCoreApplication.translate("setting_ui_tr", "<html><head/><body><p>This option will prevent the system from going to sleep.\
            It is necessary if your power manager is suspending the system automatically. </p></body></html>"))

        self.wait_queue_time.setToolTip(
            QCoreApplication.translate("setting_ui_tr", "<html><head/><body><p>Format HH:MM</p></body></html>"))

        self.setting_tabWidget.setTabText(
            self.setting_tabWidget.indexOf(self.style_tab),  QCoreApplication.translate("setting_ui_tr", "Preferences"))

# columns_tab
        self.show_column_label.setText(QCoreApplication.translate("setting_ui_tr", 'Show these columns:'))
        self.column0_checkBox.setText(QCoreApplication.translate("setting_ui_tr", 'File Name'))
        self.column1_checkBox.setText(QCoreApplication.translate("setting_ui_tr", 'Status'))
        self.column2_checkBox.setText(QCoreApplication.translate("setting_ui_tr", 'Size'))
        self.column3_checkBox.setText(QCoreApplication.translate("setting_ui_tr", 'Downloaded'))
        self.column4_checkBox.setText(QCoreApplication.translate("setting_ui_tr", 'Percentage'))
        self.column5_checkBox.setText(QCoreApplication.translate("setting_ui_tr", 'Connections'))
        self.column6_checkBox.setText(QCoreApplication.translate("setting_ui_tr", 'Transfer Rate'))
        self.column7_checkBox.setText(QCoreApplication.translate("setting_ui_tr", 'Estimated Time Left'))
        self.column10_checkBox.setText(QCoreApplication.translate("setting_ui_tr", 'First Try Date'))
        self.column11_checkBox.setText(QCoreApplication.translate("setting_ui_tr", 'Last Try Date'))
        self.column12_checkBox.setText(QCoreApplication.translate("setting_ui_tr", 'Category'))

        self.setting_tabWidget.setTabText(
            self.setting_tabWidget.indexOf(self.columns_tab), QCoreApplication.translate("setting_ui_tr", "Columns Customization"))

# Video Finder options tab
        self.setting_tabWidget.setTabText(self.setting_tabWidget.indexOf(
            self.video_finder_tab), QCoreApplication.translate("setting_ui_tr",  "Video Finder Options"))

        self.max_links_label.setText(QCoreApplication.translate("setting_ui_tr", 'Maximum number of links to capture:<br/>'
                                                                '<small>(If browser sends multiple video links at a time)</small>'))

# window buttons
        self.defaults_pushButton.setText(QCoreApplication.translate("setting_ui_tr", "Defaults"))
        self.cancel_pushButton.setText(QCoreApplication.translate("setting_ui_tr", "Cancel"))
        self.ok_pushButton.setText(QCoreApplication.translate("setting_ui_tr", "OK"))
