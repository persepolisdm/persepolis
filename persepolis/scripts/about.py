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

from persepolis.gui.about_ui import AboutWindow_Ui
from PyQt5.QtCore import QSize, QPoint
from persepolis.gui import resources
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QIcon


class AboutWindow(AboutWindow_Ui):
    def __init__(self, persepolis_setting):
        super().__init__(persepolis_setting)

        self.persepolis_setting = persepolis_setting

# setting window size and position
        size = self.persepolis_setting.value(
            'AboutWindow/size', QSize(545, 375))
        position = self.persepolis_setting.value(
            'AboutWindow/position', QPoint(300, 300))

        self.resize(size)
        self.move(position)

    def changeIcon(self, icons):
        icons = ':/' + str(icons) + '/'
        self.pushButton.setIcon(QIcon(icons + 'ok'))

    def closeEvent(self, event):
        # saving window size and position
        self.persepolis_setting.setValue('AboutWindow/size', self.size())
        self.persepolis_setting.setValue('AboutWindow/position', self.pos())
        self.persepolis_setting.sync()
        event.accept()
