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

try:
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
    from PySide6.QtCore import QCoreApplication
except:
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
    from PyQt5.QtCore import QCoreApplication


class VideoFinderProgressWindow_Ui(ProgressWindow_Ui):
    def __init__(self, persepolis_setting):
        super().__init__(persepolis_setting)

        # status_tab
        self.status_tab = QWidget()
        status_tab_verticalLayout = QVBoxLayout(self.status_tab)

        # video_status_label
        self.video_status_label = QLabel(self.status_tab)
        status_tab_verticalLayout.addWidget(self.video_status_label)

        # audio_status_label
        self.audio_status_label = QLabel(self.status_tab)
        status_tab_verticalLayout.addWidget(self.audio_status_label)

        # muxing_status_label
        self.muxing_status_label = QLabel(self.status_tab)
        status_tab_verticalLayout.addWidget(self.muxing_status_label)

        self.progress_tabWidget.addTab(self.status_tab, "")

        # set status_tab as default tab
        self.progress_tabWidget.setCurrentIndex(2)

        # labels

        self.video_status_label.setText(QCoreApplication.translate(
            "video_finder_progress_ui_tr", "<b>Video file status: </b>"))
        self.audio_status_label.setText(QCoreApplication.translate(
            "video_finder_progress_ui_tr", "<b>Audio file status: </b>"))
        self.muxing_status_label.setText(QCoreApplication.translate(
            "video_finder_progress_ui_tr", "<b>Mixing status: </b>"))

        self.progress_tabWidget.setTabText(self.progress_tabWidget.indexOf(
            self.status_tab), QCoreApplication.translate("setting_ui_tr", "Status"))
