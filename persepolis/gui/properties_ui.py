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
    from PySide6.QtCore import QCoreApplication
    from PySide6.QtWidgets import QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QSpinBox, QCheckBox, QFrame, QSizePolicy
except:
    from PyQt5.QtCore import QCoreApplication
    from PyQt5.QtWidgets import QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QSpinBox, QCheckBox, QFrame, QSizePolicy

from persepolis.gui.addlink_ui import AddLinkWindow_Ui


class PropertiesWindow_Ui(AddLinkWindow_Ui):
    def __init__(self, persepolis_setting):
        super().__init__(persepolis_setting)
        self.persepolis_setting = persepolis_setting
        self.download_later_pushButton.hide()  # hide download_later_pushButton
        self.change_name_checkBox.hide()  # hide change_name_checkBox
        self.change_name_lineEdit.hide()  # hide change_name_lineEdit

        # add new QLineEdit and QLineEdit for audio link if we have video finder links
        self.link_label_2 = QLabel(self.link_frame)
        self.link_horizontalLayout.addWidget(self.link_label_2)

        self.link_lineEdit_2 = QLineEdit(self.link_frame)
        self.link_horizontalLayout.addWidget(self.link_lineEdit_2)

        # Limit speed options for torrent
        limit_speed_horizontalLayout = QHBoxLayout()
        # limit download speed
        limit_download_speed_verticalLayout = QVBoxLayout()

        self.limit_download_checkBox = QCheckBox(self.more_options_tab)
        limit_download_speed_verticalLayout.addWidget(self.limit_download_checkBox)

        self.limit_download_frame = QFrame(self.more_options_tab)
        self.limit_download_frame.setFrameShape(QFrame.StyledPanel)
        self.limit_download_frame.setFrameShadow(QFrame.Raised)
        limit_download_speed_verticalLayout.addWidget(self.limit_download_frame)

        limit_download_speed_horizontlLayout = QHBoxLayout(self.limit_download_frame)
        self.limit_download_spinBox = QSpinBox(self.limit_download_frame)
        self.limit_download_spinBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.limit_download_spinBox.setMinimum(1)
        limit_download_speed_horizontlLayout.addWidget(self.limit_download_spinBox, 1)

        self.limit_download_label = QLabel(self.limit_download_frame)
        self.limit_download_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        limit_download_speed_horizontlLayout.addWidget(self.limit_download_label, 1)

        limit_speed_horizontalLayout.addLayout(limit_download_speed_verticalLayout)

        # limit upload speed
        limit_upload_speed_verticalLayout = QVBoxLayout()

        self.limit_upload_checkBox = QCheckBox(self.more_options_tab)
        limit_upload_speed_verticalLayout.addWidget(self.limit_upload_checkBox)

        self.limit_upload_frame = QFrame(self.more_options_tab)
        self.limit_upload_frame.setFrameShape(QFrame.StyledPanel)
        self.limit_upload_frame.setFrameShadow(QFrame.Raised)
        limit_upload_speed_verticalLayout.addWidget(self.limit_upload_frame)

        limit_upload_speed_horizontlLayout = QHBoxLayout(self.limit_upload_frame)
        self.limit_upload_spinBox = QSpinBox(self.limit_upload_frame)
        self.limit_download_spinBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.limit_upload_spinBox.setMinimum(0)
        limit_upload_speed_horizontlLayout.addWidget(self.limit_upload_spinBox, 1)

        self.limit_upload_label = QLabel(self.limit_upload_frame)
        self.limit_download_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        limit_upload_speed_horizontlLayout.addWidget(self.limit_upload_label, 1)

        limit_speed_horizontalLayout.addLayout(limit_upload_speed_verticalLayout)
        self.more_options_tab_verticalLayout.addLayout(limit_speed_horizontalLayout)
        self.more_options_tab_verticalLayout.addStretch(1)

        # Hide limit  frames and limit checkboxes and video finder label and lineEdit by default
        self.limit_upload_checkBox.hide()
        self.limit_download_checkBox.hide()
        self.limit_download_frame.hide()
        self.limit_upload_frame.hide()
        self.link_label_2.hide()
        self.link_lineEdit_2.hide()

        # Set text
        self.limit_download_checkBox.setText(QCoreApplication.translate("properties_ui", 'Limit download speed'))
        self.limit_upload_checkBox.setText(QCoreApplication.translate("properties_ui", 'Limit upload speed'))

        self.limit_download_label.setText(QCoreApplication.translate("properties_ui", 'KiB/s'))
        self.limit_upload_label.setText(QCoreApplication.translate("properties_ui", 'KiB/s'))
