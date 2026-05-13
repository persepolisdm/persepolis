# -*- coding: utf-8 -*-
"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

try:
    from PySide6.QtWidgets import QTabWidget, QPushButton, QComboBox, QSpinBox, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QGridLayout, QCheckBox, QFrame, QLineEdit, QRadioButton, QButtonGroup

    from PySide6.QtCore import Qt, QTranslator, QCoreApplication, QLocale
    from PySide6 import QtCore
    from PySide6.QtGui import QIcon
except ImportError:
    from PyQt5.QtWidgets import QTabWidget, QPushButton, QComboBox, QSpinBox, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QGridLayout, QCheckBox, QFrame, QLineEdit, QRadioButton, QButtonGroup
    from PyQt5.QtCore import Qt, QTranslator, QCoreApplication, QLocale
    from PyQt5 import QtCore
    from PyQt5.QtGui import QIcon

from persepolis.gui import resources
from persepolis.gui.customized_widgets import MyQDateTimeEdit


class AddLinkWindow_Ui(QWidget):
    def __init__(self, persepolis_setting: object) -> None:
        super().__init__()
        self.persepolis_setting = persepolis_setting

        # language support
        locale: str = str(self.persepolis_setting.value('settings/locale'))
        QLocale.setDefault(QLocale(locale))
        self.translator: QTranslator = QTranslator()
        if self.translator.load(':/translations/locales/ui_' + locale, 'ts'):
            QCoreApplication.installTranslator(self.translator)

        # ui direction
        ui_direction: str = str(self.persepolis_setting.value('ui_direction'))
        if ui_direction == 'rtl':
            self.setLayoutDirection(Qt.RightToLeft)
        elif ui_direction == 'ltr':
            self.setLayoutDirection(Qt.LeftToRight)

        # icons path
        self.icons: str = '/:' + str(self.persepolis_setting.value('settings/icons')) + '/'

        self.setMinimumSize(QtCore.QSize(520, 425))
        self.setWindowIcon(QIcon.fromTheme('persepolis', QIcon(':/com.github.persepolisdm.persepolis.svg')))

        window_verticalLayout: QVBoxLayout = QVBoxLayout()

        self.add_link_tabWidget: QTabWidget = QTabWidget(self)
        window_verticalLayout.addWidget(self.add_link_tabWidget)

        self.__add_link_tab()
        self.__add_proxy_tab()
        self.__add_more_options_tab()
        self.__add_advance_options_tab()
        self.__add_action_buttons(window_verticalLayout)

        self.setLayout(window_verticalLayout)
        self.__apply_texts()

    def __add_link_tab(self) -> None:
        """Link URL, file rename and category selector."""
        self.link_tab: QWidget = QWidget()

        layout: QVBoxLayout = QVBoxLayout(self.link_tab)
        layout.setContentsMargins(21, 21, 21, 81)

        # link frame
        self.link_frame: QFrame = QFrame(self.link_tab)
        self.link_frame.setFrameShape(QFrame.StyledPanel)
        self.link_frame.setFrameShadow(QFrame.Raised)

        frame_layout: QHBoxLayout = QHBoxLayout(self.link_frame)
        link_vertical: QVBoxLayout = QVBoxLayout()

        link_row: QHBoxLayout = QHBoxLayout()
        self.link_label: QLabel = QLabel(self.link_frame)
        self.link_lineEdit: QLineEdit = QLineEdit(self.link_frame)
        link_row.addWidget(self.link_label)
        link_row.addWidget(self.link_lineEdit)
        link_vertical.addLayout(link_row)

        rename_row: QHBoxLayout = QHBoxLayout()
        self.change_name_checkBox: QCheckBox = QCheckBox(self.link_frame)
        self.change_name_lineEdit: QLineEdit = QLineEdit(self.link_frame)
        rename_row.addWidget(self.change_name_checkBox)
        rename_row.addWidget(self.change_name_lineEdit)
        link_vertical.addLayout(rename_row)

        frame_layout.addLayout(link_vertical)
        layout.addWidget(self.link_frame)

        # category row
        category_row: QHBoxLayout = QHBoxLayout()

        self.queue_frame: QFrame = QFrame(self)
        self.queue_frame.setFrameShape(QFrame.StyledPanel)
        self.queue_frame.setFrameShadow(QFrame.Raised)

        queue_row: QHBoxLayout = QHBoxLayout(self.queue_frame)
        self.add_queue_label: QLabel = QLabel(self.queue_frame)
        self.add_queue_comboBox: QComboBox = QComboBox(self.queue_frame)
        queue_row.addWidget(self.add_queue_label)
        queue_row.addWidget(self.add_queue_comboBox)

        self.size_label: QLabel = QLabel(self)
        category_row.addWidget(self.queue_frame)
        category_row.addStretch(1)
        category_row.addWidget(self.size_label)
        layout.addLayout(category_row)

        layout.addStretch(1)
        self.add_link_tabWidget.addTab(self.link_tab, '')

    def __add_more_options_tab(self) -> None:
        """Download credentials, folder, time limits and connections."""
        self.more_options_tab: QWidget = QWidget(self)
        layout: QVBoxLayout = QVBoxLayout(self.more_options_tab)

        self.__add_download_credentials(layout)
        self.__add_time_and_connections(layout)

        layout.addStretch(1)
        self.add_link_tabWidget.addTab(self.more_options_tab, '')

    def __add_download_credentials(self, layout: QVBoxLayout) -> None:
        """Download username/password + folder selector."""
        row: QHBoxLayout = QHBoxLayout()
        row.setContentsMargins(-1, 10, -1, -1)

        # credentials
        credentials_vertical: QVBoxLayout = QVBoxLayout()
        self.download_checkBox: QCheckBox = QCheckBox(self.more_options_tab)
        credentials_vertical.addWidget(self.download_checkBox)

        self.download_frame: QFrame = QFrame(self.more_options_tab)
        self.download_frame.setFrameShape(QFrame.StyledPanel)
        self.download_frame.setFrameShadow(QFrame.Raised)

        credentials_grid: QGridLayout = QGridLayout(self.download_frame)
        self.download_user_label: QLabel = QLabel(self.download_frame)
        self.download_user_lineEdit: QLineEdit = QLineEdit(self.download_frame)
        self.download_pass_label: QLabel = QLabel(self.download_frame)
        self.download_pass_lineEdit: QLineEdit = QLineEdit(self.download_frame)
        self.download_pass_lineEdit.setEchoMode(QLineEdit.Password)

        credentials_grid.addWidget(self.download_user_label, 0, 0)
        credentials_grid.addWidget(self.download_user_lineEdit, 0, 1)
        credentials_grid.addWidget(self.download_pass_label, 1, 0)
        credentials_grid.addWidget(self.download_pass_lineEdit, 1, 1)
        credentials_vertical.addWidget(self.download_frame)
        row.addLayout(credentials_vertical)

        # folder
        self.folder_frame: QFrame = QFrame(self.more_options_tab)
        self.folder_frame.setFrameShape(QFrame.StyledPanel)
        self.folder_frame.setFrameShadow(QFrame.Raised)

        folder_grid: QGridLayout = QGridLayout(self.folder_frame)
        self.folder_label: QLabel = QLabel(self.folder_frame)
        self.folder_label.setAlignment(QtCore.Qt.AlignCenter)
        self.download_folder_lineEdit: QLineEdit = QLineEdit(self.folder_frame)
        self.folder_pushButton: QPushButton = QPushButton(self.folder_frame)
        self.folder_pushButton.setIcon(QIcon(self.icons + 'folder'))
        self.folder_checkBox: QCheckBox = QCheckBox(self.folder_frame)

        folder_grid.addWidget(self.folder_label, 1, 0)
        folder_grid.addWidget(self.download_folder_lineEdit, 2, 0)
        folder_grid.addWidget(self.folder_pushButton, 3, 0)
        folder_grid.addWidget(self.folder_checkBox, 4, 0)
        row.addWidget(self.folder_frame)

        layout.addLayout(row)

    def __add_time_and_connections(self, layout: QVBoxLayout) -> None:
        """Start/end time pickers and number of connections."""
        time_row: QHBoxLayout = QHBoxLayout()
        time_row.setContentsMargins(-1, 10, -1, -1)

        # start time
        start_vertical: QVBoxLayout = QVBoxLayout()
        self.start_checkBox: QCheckBox = QCheckBox(self.more_options_tab)
        start_vertical.addWidget(self.start_checkBox)

        self.start_frame: QFrame = QFrame(self.more_options_tab)
        self.start_frame.setFrameShape(QFrame.StyledPanel)
        self.start_frame.setFrameShadow(QFrame.Raised)

        start_frame_layout: QHBoxLayout = QHBoxLayout(self.start_frame)
        self.start_time_qDataTimeEdit: MyQDateTimeEdit = MyQDateTimeEdit(self.start_frame)
        self.start_time_qDataTimeEdit.setDisplayFormat('H:mm')
        start_frame_layout.addWidget(self.start_time_qDataTimeEdit)
        start_vertical.addWidget(self.start_frame)
        time_row.addLayout(start_vertical)

        # end time
        end_vertical: QVBoxLayout = QVBoxLayout()
        self.end_checkBox: QCheckBox = QCheckBox(self.more_options_tab)
        end_vertical.addWidget(self.end_checkBox)

        self.end_frame: QFrame = QFrame(self.more_options_tab)
        self.end_frame.setFrameShape(QFrame.StyledPanel)
        self.end_frame.setFrameShadow(QFrame.Raised)

        end_frame_layout: QHBoxLayout = QHBoxLayout(self.end_frame)
        self.end_time_qDateTimeEdit: MyQDateTimeEdit = MyQDateTimeEdit(self.end_frame)
        self.end_time_qDateTimeEdit.setDisplayFormat('H:mm')
        end_frame_layout.addWidget(self.end_time_qDateTimeEdit)
        end_vertical.addWidget(self.end_frame)
        time_row.addLayout(end_vertical)

        # limit speed + connections — mesmo frame, mesma coluna
        self.limit_frame: QFrame = QFrame(self.more_options_tab)
        self.limit_frame.setFrameShape(QFrame.StyledPanel)
        self.limit_frame.setFrameShadow(QFrame.Raised)

        limit_layout: QVBoxLayout = QVBoxLayout(self.limit_frame)
        self.connections_label: QLabel = QLabel(self.limit_frame)
        self.connections_spinBox: QSpinBox = QSpinBox(self.limit_frame)
        self.connections_spinBox.setMinimum(1)
        self.connections_spinBox.setMaximum(64)
        self.connections_spinBox.setProperty('value', 64)
        limit_layout.addWidget(self.connections_label)
        limit_layout.addWidget(self.connections_spinBox)

        limit_vertical: QVBoxLayout = QVBoxLayout()
        limit_vertical.addWidget(self.limit_frame)
        time_row.addLayout(limit_vertical)
        layout.addLayout(time_row)

    def __add_advance_options_tab(self) -> None:
        """Referrer, header, user agent and cookies."""
        self.advance_options_tab: QWidget = QWidget(self)
        layout: QVBoxLayout = QVBoxLayout(self.advance_options_tab)

        self.referer_label: QLabel = QLabel(self.advance_options_tab)
        self.referer_lineEdit: QLineEdit = QLineEdit(self.advance_options_tab)
        self.header_label: QLabel = QLabel(self.advance_options_tab)
        self.header_lineEdit: QLineEdit = QLineEdit(self.advance_options_tab)
        self.user_agent_label: QLabel = QLabel(self.advance_options_tab)
        self.user_agent_lineEdit: QLineEdit = QLineEdit(self.advance_options_tab)
        self.load_cookies_label: QLabel = QLabel(self.advance_options_tab)
        self.load_cookies_lineEdit: QLineEdit = QLineEdit(self.advance_options_tab)

        for label, field in (
                (self.referer_label, self.referer_lineEdit),
                (self.header_label, self.header_lineEdit),
                (self.user_agent_label, self.user_agent_lineEdit),
                (self.load_cookies_label, self.load_cookies_lineEdit),
        ):
            row: QHBoxLayout = QHBoxLayout()
            row.addWidget(label)
            row.addWidget(field)
            layout.addLayout(row)

        layout.addStretch(1)
        self.add_link_tabWidget.addTab(self.advance_options_tab, '')

    def __add_action_buttons(self, layout: QVBoxLayout) -> None:
        """Download Later, Cancel and OK buttons."""
        row: QHBoxLayout = QHBoxLayout()
        row.addStretch(1)

        self.download_later_pushButton: QPushButton = QPushButton(self)
        self.download_later_pushButton.setIcon(QIcon(self.icons + 'stop'))

        self.cancel_pushButton: QPushButton = QPushButton(self)
        self.cancel_pushButton.setIcon(QIcon(self.icons + 'remove'))

        self.ok_pushButton: QPushButton = QPushButton(self)
        self.ok_pushButton.setIcon(QIcon(self.icons + 'ok'))

        row.addWidget(self.download_later_pushButton)
        row.addWidget(self.cancel_pushButton)
        row.addWidget(self.ok_pushButton)
        layout.addLayout(row)

    def __apply_texts(self) -> None:
        """All translateable labels in one place."""
        tr = QCoreApplication.translate

        self.setWindowTitle(tr("addlink_ui_tr", "Add Download Link"))

        self.link_label.setText(tr("addlink_ui_tr", "Download link: "))
        self.add_queue_label.setText(tr("addlink_ui_tr", "Add to category: "))
        self.change_name_checkBox.setText(tr("addlink_ui_tr", "Change file name: "))

        self.use_app_proxy_radioButton.setText(tr("addlink_ui_tr", "Use Application Proxy Settings"))
        self.custom_proxy_radioButton.setText(tr("addlink_ui_tr", "Custom Proxy"))
        self.detect_proxy_pushButton.setText(tr("addlink_ui_tr", "Detect System Proxy Settings"))
        self.ip_label.setText(tr("addlink_ui_tr", "IP: "))
        self.port_label.setText(tr("addlink_ui_tr", "Port:"))
        self.proxy_user_label.setText(tr("addlink_ui_tr", "Proxy username: "))
        self.proxy_pass_label.setText(tr("addlink_ui_tr", "Proxy password: "))
        self.http_radioButton.setText(tr("addlink_ui_tr", "HTTP"))
        self.https_radioButton.setText(tr("addlink_ui_tr", "HTTPS"))
        self.socks5_radioButton.setText(tr("addlink_ui_tr", "SOCKS5"))

        self.download_checkBox.setText(tr("addlink_ui_tr", "Download username and password"))
        self.download_user_label.setText(tr("addlink_ui_tr", "Download username: "))
        self.download_pass_label.setText(tr("addlink_ui_tr", "Download password: "))
        self.folder_label.setText(tr("addlink_ui_tr", "Download Folder: "))
        self.folder_pushButton.setText(tr("addlink_ui_tr", "Change Download Folder"))
        self.folder_checkBox.setText(tr("addlink_ui_tr", "Remember this path"))
        self.start_checkBox.setText(tr("addlink_ui_tr", "Start time"))
        self.end_checkBox.setText(tr("addlink_ui_tr", "End time"))
        self.connections_label.setText(tr("addlink_ui_tr", "Number of connections:"))

        self.referer_label.setText(tr("addlink_ui_tr", 'Referrer: '))
        self.header_label.setText(tr("addlink_ui_tr", 'Header: '))
        self.user_agent_label.setText(tr("addlink_ui_tr", 'User agent: '))
        self.load_cookies_label.setText(tr("addlink_ui_tr", 'Load cookies: '))

        self.download_later_pushButton.setText(tr("addlink_ui_tr", "Download Later"))
        self.cancel_pushButton.setText(tr("addlink_ui_tr", "Cancel"))
        self.ok_pushButton.setText(tr("addlink_ui_tr", "OK"))

        self.add_link_tabWidget.setTabText(self.add_link_tabWidget.indexOf(self.link_tab), tr("addlink_ui_tr", "Link"))
        self.add_link_tabWidget.setTabText(self.add_link_tabWidget.indexOf(self.proxy_tab),
                                           tr("addlink_ui_tr", "Proxy"))
        self.add_link_tabWidget.setTabText(self.add_link_tabWidget.indexOf(self.more_options_tab),
                                           tr("addlink_ui_tr", "More Options"))
        self.add_link_tabWidget.setTabText(self.add_link_tabWidget.indexOf(self.advance_options_tab),
                                           tr("addlink_ui_tr", "Advanced Options"))

    def __add_proxy_tab(self) -> None:
        self.proxy_tab: QWidget = QWidget(self)
        layout: QVBoxLayout = QVBoxLayout(self.proxy_tab)
        layout.setContentsMargins(21, 21, 21, 21)

        self.__add_proxy_controls(layout)
        self.__add_proxy_address_frame(layout)

        layout.addStretch(1)
        self.add_link_tabWidget.addTab(self.proxy_tab, "")

    def __add_proxy_controls(self, layout: QVBoxLayout) -> None:
        """Radio buttons to choose between application proxy or custom proxy + auto-detection button."""
        self.use_app_proxy_radioButton: QRadioButton = QRadioButton(self.proxy_tab)
        self.use_app_proxy_radioButton.setChecked(True)
        self.custom_proxy_radioButton: QRadioButton = QRadioButton(self.proxy_tab)

        self.proxy_buttonGroup: QButtonGroup = QButtonGroup(self.proxy_tab)
        self.proxy_buttonGroup.addButton(self.use_app_proxy_radioButton)
        self.proxy_buttonGroup.addButton(self.custom_proxy_radioButton)

        self.detect_proxy_pushButton: QPushButton = QPushButton(self.proxy_tab)
        self.detect_proxy_label: QLabel = QLabel(self.proxy_tab)

        radio_row: QHBoxLayout = QHBoxLayout()
        radio_row.addWidget(self.use_app_proxy_radioButton)
        radio_row.addWidget(self.custom_proxy_radioButton)
        radio_row.addStretch(1)

        detect_row: QHBoxLayout = QHBoxLayout()
        detect_row.addWidget(self.detect_proxy_pushButton)
        detect_row.addWidget(self.detect_proxy_label)
        detect_row.addStretch(1)

        controls_column: QVBoxLayout = QVBoxLayout()
        controls_column.addLayout(radio_row)
        controls_column.addLayout(detect_row)

        layout.addLayout(controls_column)

    def __add_proxy_address_frame(self, layout: QVBoxLayout) -> None:
        """Frame with IP, port, and proxy username and password."""
        self.proxy_frame: QFrame = QFrame(self.proxy_tab)
        self.proxy_frame.setFrameShape(QFrame.StyledPanel)
        self.proxy_frame.setFrameShadow(QFrame.Raised)

        grid: QGridLayout = QGridLayout(self.proxy_frame)

        self.ip_label: QLabel = QLabel(self.proxy_frame)
        self.ip_lineEdit: QLineEdit = QLineEdit(self.proxy_frame)
        self.ip_lineEdit.setInputMethodHints(QtCore.Qt.ImhNone)
        self.port_label: QLabel = QLabel(self.proxy_frame)
        self.port_spinBox: QSpinBox = QSpinBox(self.proxy_frame)
        self.port_spinBox.setMaximum(65535)
        self.port_spinBox.setSingleStep(1)

        self.proxy_user_label: QLabel = QLabel(self.proxy_frame)
        self.proxy_user_lineEdit: QLineEdit = QLineEdit(self.proxy_frame)
        self.proxy_pass_label: QLabel = QLabel(self.proxy_frame)
        self.proxy_pass_lineEdit: QLineEdit = QLineEdit(self.proxy_frame)
        self.proxy_pass_lineEdit.setEchoMode(QLineEdit.Password)

        grid.addWidget(self.ip_label, 0, 0)
        grid.addWidget(self.ip_lineEdit, 0, 1)
        grid.addWidget(self.port_label, 0, 2)
        grid.addWidget(self.port_spinBox, 0, 3)
        grid.addWidget(self.proxy_user_label, 2, 0)
        grid.addWidget(self.proxy_user_lineEdit, 2, 1)
        grid.addWidget(self.proxy_pass_label, 2, 2)
        grid.addWidget(self.proxy_pass_lineEdit, 2, 3)

        self.__add_proxy_type_buttons(grid)
        layout.addWidget(self.proxy_frame)

    def __add_proxy_type_buttons(self, grid: QGridLayout) -> None:
        """Radio buttons HTTP / HTTPS / SOCKS5 inside address frame."""
        self.http_radioButton: QRadioButton = QRadioButton(self.proxy_frame)
        self.https_radioButton: QRadioButton = QRadioButton(self.proxy_frame)
        self.socks5_radioButton: QRadioButton = QRadioButton(self.proxy_frame)

        grid.addWidget(self.http_radioButton, 4, 0)
        grid.addWidget(self.https_radioButton, 5, 0)
        grid.addWidget(self.socks5_radioButton, 6, 0)

        self.https_radioButton.hide()  # waiting for HTTPS support