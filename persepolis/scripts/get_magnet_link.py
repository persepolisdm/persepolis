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
    from PySide6.QtCore import QSize, QPoint, Qt
    from PySide6.QtGui import QIcon
except ImportError:
    from PyQt5.QtCore import QSize, QPoint, Qt
    from PyQt5.QtGui import QIcon

from persepolis.gui.get_magnet_link_ui import GetMagnetLinkWindow_Ui


class GetMagnetLinkWindow(GetMagnetLinkWindow_Ui):
    def __init__(self, parent, callback, persepolis_setting):
        super().__init__(persepolis_setting)
        self.callback = callback
        self.persepolis_setting = persepolis_setting
        self.parent = parent

        # Accept the dialog
        self.ok_pushButton.clicked.connect(self.okButtonPressed)
        # Reject the dialog
        self.cancel_pushButton.clicked.connect(self.close)

        # set window size and position
        size = self.persepolis_setting.value(
            'GetMagnetLinkWindow/size', QSize(300, 100))
        position = self.persepolis_setting.value(
            'GetMagnetLinkWindow/position', QPoint(300, 300))
        self.resize(size)
        self.move(position)

    def okButtonPressed(self):
        # Return the text from the QLineEdit
        self.callback(self.line_edit.text())
        self.close()

    # close window with ESC key
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    # save size and position of window, when user closes the window.
    def closeEvent(self, event):
        self.persepolis_setting.setValue('GetMagnetLinkWindow/size', self.size())
        self.persepolis_setting.setValue('GetMagnetLinkWindow/position', self.pos())
        self.persepolis_setting.sync()
        event.accept()

    def changeIcon(self, icons):
        icons = ':/' + str(icons) + '/'
        self.cancel_pushButton.setIcon(QIcon(icons + 'remove'))
        self.ok_pushButton.setIcon(QIcon(icons + 'ok'))
