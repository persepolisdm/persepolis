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

from persepolis.gui.progress_ui import ProgressWindow_Ui
from persepolis.gui import resources
try:
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QAbstractItemView, QHeaderView
    from PySide6.QtCore import QCoreApplication, Qt
except:
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QAbstractItemView, QHeaderView
    from PyQt5.QtCore import QCoreApplication, Qt


class TorrentProgressWindow_Ui(ProgressWindow_Ui):
    def __init__(self, persepolis_setting ,parent):
        super().__init__(persepolis_setting, parent)

        # status_tab
        self.status_tab = QWidget()
        status_tab_verticalLayout = QVBoxLayout(self.status_tab)
        self.progress_tabWidget.insertTab(1, self.status_tab, "")

        # set status_tab as default tab
        self.progress_tabWidget.setCurrentIndex(0)

        # files table
        self.files_table = QTableWidget(self.status_tab)
        self.files_table.setSizeAdjustPolicy(QAbstractItemView.AdjustToContents)
        status_tab_verticalLayout.addWidget(self.files_table)

        self.files_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.files_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.files_table.verticalHeader().hide()

        self.files_table.setColumnCount(3)

        self.files_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.files_table.horizontalHeader().setStretchLastSection(True)

        self.files_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.files_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.progress_tabWidget.setTabText(self.progress_tabWidget.indexOf(
            self.status_tab), QCoreApplication.translate("torrentprogresswindow_ui_tr", "Files Status"))

