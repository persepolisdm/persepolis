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

from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt

class DarkFusionPalette(QPalette):
    def __init__(self):
        super().__init__()
        # 53 53 53 is gray
        self.setColor(QPalette.Window, QColor(56, 56, 56))

        # light gray
        self.setColor(QPalette.WindowText, Qt.white)

        # gray
        self.setColor(QPalette.Base, QColor(56, 56, 56))

        # gray
        self.setColor(QPalette.AlternateBase, QColor(63, 63, 63))
        self.setColor(QPalette.ToolTipBase, Qt.white)
        self.setColor(QPalette.ToolTipText, Qt.white)

        # light gray
        self.setColor(QPalette.Text, Qt.white)

        # gray
        self.setColor(QPalette.Button, QColor(56, 56, 56))

        # light gray
        self.setColor(QPalette.ButtonText, Qt.white)

        # numix red
        self.setColor(QPalette.BrightText, QColor(0, 128, 152))

        # blue
        self.setColor(QPalette.Link, QColor(42, 130, 218))

        # numix red
        self.setColor(QPalette.Highlight, QColor(0, 128, 152))

        self.setColor(QPalette.HighlightedText, Qt.white)

        self.setColor(QPalette.Disabled, QPalette.Window, QColor(51, 51, 51))

        self.setColor(QPalette.Disabled, QPalette.ButtonText,
                      QColor(111, 111, 111))

        self.setColor(QPalette.Disabled, QPalette.Text, QColor(122, 118, 113))

        self.setColor(QPalette.Disabled, QPalette.WindowText,
                      QColor(122, 118, 113))

        self.setColor(QPalette.Disabled, QPalette.Base, QColor(32, 32, 32))

