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
        self.setColor(QPalette.Window, QColor(56, 56, 56))

        self.setColor(QPalette.WindowText, Qt.white)

        self.setColor(QPalette.Base, QColor(56, 56, 56))

        self.setColor(QPalette.AlternateBase, QColor(63, 63, 63))
        self.setColor(QPalette.ToolTipBase, Qt.white)
        self.setColor(QPalette.ToolTipText, Qt.white)

        self.setColor(QPalette.Text, Qt.white)

        self.setColor(QPalette.Button, QColor(56, 56, 56))

        self.setColor(QPalette.ButtonText, Qt.white)

        self.setColor(QPalette.BrightText, QColor(0, 128, 152))

        self.setColor(QPalette.Link, QColor(42, 130, 218))

        self.setColor(QPalette.Highlight, QColor(0, 128, 152))

        self.setColor(QPalette.HighlightedText, Qt.white)

        self.setColor(QPalette.Disabled, QPalette.Window, QColor(51, 51, 51))

        self.setColor(QPalette.Disabled, QPalette.ButtonText,
                      QColor(111, 111, 111))

        self.setColor(QPalette.Disabled, QPalette.Text, QColor(122, 118, 113))

        self.setColor(QPalette.Disabled, QPalette.WindowText,
                      QColor(122, 118, 113))

        self.setColor(QPalette.Disabled, QPalette.Base, QColor(32, 32, 32))


class LightFusionPalette(QPalette):
    def __init__(self):
        super().__init__()
        # EFF0F1 
        self.setColor(QPalette.Window, QColor(239, 240, 241))

        self.setColor(QPalette.WindowText, QColor(49, 54, 59))

        self.setColor(QPalette.Base, QColor(239, 240, 241))

        self.setColor(QPalette.AlternateBase, QColor(63, 63, 63))
        self.setColor(QPalette.ToolTipBase, QColor(49, 54, 59))
        self.setColor(QPalette.ToolTipText, QColor(49, 54, 59))

        self.setColor(QPalette.Text, QColor(49, 54, 59))

        self.setColor(QPalette.Button, QColor(239, 240, 241))

        self.setColor(QPalette.ButtonText, QColor(49, 54, 59))

        self.setColor(QPalette.BrightText, QColor(110, 197, 244))

        self.setColor(QPalette.Link, QColor(42, 130, 218))

        self.setColor(QPalette.Highlight, QColor(110, 197, 244))

        self.setColor(QPalette.HighlightedText, QColor(49, 54, 59))

        self.setColor(QPalette.Disabled, QPalette.Window, QColor(227, 227, 227))

        self.setColor(QPalette.Disabled, QPalette.ButtonText,
                      QColor(111, 111, 111))

        self.setColor(QPalette.Disabled, QPalette.Text, QColor(111, 111, 111))

        self.setColor(QPalette.Disabled, QPalette.WindowText,
                      QColor(111, 111, 111))

        self.setColor(QPalette.Disabled, QPalette.Base, QColor(227, 227, 227))

