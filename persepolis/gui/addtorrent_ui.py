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

from persepolis.gui.text_queue_ui import TextQueue_Ui
from persepolis.gui import resources

try:
    from PySide6.QtWidgets import QLabel, QHBoxLayout, QPushButton
    from PySide6.QtCore import QCoreApplication
    from PySide6.QtGui import QIcon

except:
    from PyQt5.QtWidgets import QLabel, QHBoxLayout, QPushButton
    from PyQt5.QtCore import QCoreApplication
    from PyQt5.QtGui import QIcon


class AddTorrentWindow_Ui(TextQueue_Ui):
    def __init__(self, persepolis_setting):
        super().__init__(persepolis_setting)

        # get icons name
        icons = ':/' + \
            str(self.persepolis_setting.value('settings/icons')) + '/'

        # torrent name
        torrent_name_horizontalLayout = QHBoxLayout()
        self.torrent_name_label1 = QLabel(self)
        torrent_name_horizontalLayout.addWidget(self.torrent_name_label1)

        self.torrent_name_label2 = QLabel(self)
        torrent_name_horizontalLayout.addWidget(self.torrent_name_label2)

        torrent_name_horizontalLayout.addStretch(1)
        self.links_tab_verticalLayout.addLayout(torrent_name_horizontalLayout)
        self.links_tab_verticalLayout.addStretch(1)

        self.links_table.setColumnCount(3)
        links_table_header_labels = [
            'File Name', 'File Size', 'index']
        self.links_table.setHorizontalHeaderLabels(links_table_header_labels)
        self.links_table.setColumnHidden(2, True)

        # add download later button
        self.download_later_pushButton = QPushButton(self)
        self.download_later_pushButton.setIcon(QIcon(icons + 'stop'))
        self.buttons_horizontalLayout.addWidget(self.download_later_pushButton)

        # Hide this widgets
        self.connections_label.setVisible(False)
        self.connections_spinBox.setVisible(False)

        # set text
        self.setWindowTitle(QCoreApplication.translate("addtorrent_ui_tr", "Add  Torrent"))
        self.torrent_name_label1.setText(QCoreApplication.translate("addtorrent_ui_tr", "Torrent name: "))
        self.queue_tabWidget.setTabText(
            self.queue_tabWidget.indexOf(self.links_tab), QCoreApplication.translate("addtorrent_ui_tr", 'Files'))
        self.download_later_pushButton.setText(QCoreApplication.translate("addtorrent.py", "Download Later"))
