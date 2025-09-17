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

from persepolis.gui.addtorrent_ui import AddTorrentWindow_Ui
try:
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QLabel, QFrame, QHBoxLayout, QPushButton, QTextEdit
    from PySide6.QtCore import QCoreApplication
except:
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QLabel, QFrame, QHBoxLayout, QPushButton, QTextEdit
    from PySide6.QtCore import QCoreApplication


class AddMagnetWindow_ui(AddTorrentWindow_Ui):
    def __init__(self, persepolis_setting):
        super().__init__(persepolis_setting)

        # Add a tab for getting magnet information
        self.magnet_tab = QWidget()

        self.queue_tabWidget.insertTab(0, self.magnet_tab, "")
        self.queue_tabWidget.setCurrentIndex(0)
        # link
        magnet_tab_verticalLayout = QVBoxLayout(self.magnet_tab)
        magnet_tab_verticalLayout.setContentsMargins(21, 21, 21, 81)

        self.link_frame = QFrame(self.magnet_tab)
        self.link_frame.setFrameShape(QFrame.StyledPanel)
        self.link_frame.setFrameShadow(QFrame.Raised)

        horizontalLayout_2 = QHBoxLayout(self.link_frame)

        self.link_verticalLayout = QVBoxLayout()

        # link ->
        self.link_horizontalLayout = QHBoxLayout()
        self.link_label = QLabel(self.link_frame)
        self.link_horizontalLayout.addWidget(self.link_label)

        self.link_lineEdit = QLineEdit(self.link_frame)
        self.link_horizontalLayout.addWidget(self.link_lineEdit)

        self.link_verticalLayout.addLayout(self.link_horizontalLayout)

        horizontalLayout_2.addLayout(self.link_verticalLayout)
        magnet_tab_verticalLayout.addWidget(self.link_frame)

        # Fetch Button
        self.fetch_metadata_pushButtontton = QPushButton(self.link_frame)
        self.link_horizontalLayout.addWidget(self.fetch_metadata_pushButtontton)

        # Status Box
        self.status_box_textEdit = QTextEdit(self.link_frame)
        self.status_box_textEdit.setMaximumHeight(150)
        self.link_verticalLayout.addWidget(self.status_box_textEdit)

        # Set texts
        self.setWindowTitle(QCoreApplication.translate("addmagnet_ui_tr", "Add  Magnet Link"))
        self.link_label.setText(QCoreApplication.translate("addmagnet_ui_tr", "Magnet link: "))
        self.queue_tabWidget.setTabText(self.queue_tabWidget.indexOf(
            self.magnet_tab), QCoreApplication.translate("addmagnet_ui_tr", "Link"))
        self.fetch_metadata_pushButtontton.setText(QCoreApplication.translate("addmagnet_ui_tr", "Fetch information"))
