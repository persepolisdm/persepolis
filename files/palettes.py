#!/usr/bin/env python3
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

from PyQt5.QtGui import QPalette , QColor
from PyQt5.QtCore import Qt

class DarkRedPallete(QPalette):
    def __init__(self):
        super().__init__()
        #53 53 53 is gray
        self.setColor(QPalette.Window, QColor(53, 53, 53))
        #light gray
        self.setColor(QPalette.WindowText, QColor(174,167,159))
        #gray
        self.setColor(QPalette.Base, QColor(63, 63, 63))
        #gray
        self.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        self.setColor(QPalette.ToolTipBase, Qt.white)
        self.setColor(QPalette.ToolTipText, Qt.white)
        #light gray
        self.setColor(QPalette.Text, QColor(174,167,159))

        #gray
        self.setColor(QPalette.Button, QColor(53, 53, 53))
        #light gray
        self.setColor(QPalette.ButtonText, QColor(174,167,159))
        #numix red
        self.setColor(QPalette.BrightText, QColor(214,73,55))
        #blue
        self.setColor(QPalette.Link, QColor(42, 130, 218))
        #numix red
        self.setColor(QPalette.Highlight , QColor(214,73,55))
        self.setColor(QPalette.HighlightedText, Qt.white)

        self.setColor(QPalette.Disabled,QPalette.Window, QColor(51,51,51))
        self.setColor(QPalette.Disabled , QPalette.ButtonText , QColor(51,51,51))
        self.setColor(QPalette.Disabled , QPalette.Text , QColor(122,118,113))
        self.setColor(QPalette.Disabled , QPalette.WindowText , QColor(122,118,113))
        self.setColor(QPalette.Disabled , QPalette.Base , QColor(32 , 32 , 32))



class DarkBluePallete(QPalette):
    def __init__(self):
        super().__init__()
        self.setColor(QPalette.Window, QColor(53, 53, 53))
        self.setColor(QPalette.WindowText, QColor(174,167,159))
        self.setColor(QPalette.Base, QColor(63, 63, 63))
        self.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        self.setColor(QPalette.ToolTipBase, Qt.white)
        self.setColor(QPalette.ToolTipText, Qt.white)
        self.setColor(QPalette.Text, QColor(174,167,159))
        self.setColor(QPalette.Button, QColor(53, 53, 53))
        self.setColor(QPalette.ButtonText, QColor(174,167,159))
        #blue
        self.setColor(QPalette.BrightText, QColor(42,130,218))
        self.setColor(QPalette.Link, QColor(42, 130, 218))
        self.setColor(QPalette.Highlight , QColor(42 ,130 ,218))
        self.setColor(QPalette.HighlightedText, Qt.white)

        self.setColor(QPalette.Disabled,QPalette.Window, QColor(51,51,51))
        self.setColor(QPalette.Disabled , QPalette.ButtonText , QColor(51,51,51))
        self.setColor(QPalette.Disabled , QPalette.Text , QColor(122,118,113))
        self.setColor(QPalette.Disabled , QPalette.WindowText , QColor(122,118,113))
        self.setColor(QPalette.Disabled , QPalette.Base , QColor(32 , 32 , 32))

class ArcDarkRedPallete(QPalette):
     def __init__(self):
        super().__init__()
        # gray
        self.setColor(QPalette.Window, QColor(53, 57, 69))
        #light gray
        self.setColor(QPalette.WindowText, QColor(174,167,159))
        #gray
        self.setColor(QPalette.Base, QColor(64, 69, 82))
        #gray
        self.setColor(QPalette.AlternateBase, QColor(56, 60, 74))
        self.setColor(QPalette.ToolTipBase, Qt.white)
        self.setColor(QPalette.ToolTipText, Qt.white)
        #light gray
        self.setColor(QPalette.Text, QColor(174,167,159))
        #gray
        self.setColor(QPalette.Button, QColor(64, 69, 82))
        #light gray
        self.setColor(QPalette.ButtonText, QColor(174,167,159))
        #Arck red
        self.setColor(QPalette.BrightText, QColor(191,71,77))
        #blue
        self.setColor(QPalette.Link, QColor(42, 130, 218))
        #Arc red
        self.setColor(QPalette.Highlight , QColor(191,71,77))
        self.setColor(QPalette.HighlightedText, Qt.white)

        self.setColor(QPalette.Disabled,QPalette.Window, QColor(51,51,51))
        self.setColor(QPalette.Disabled , QPalette.ButtonText , QColor(51,51,51))
        self.setColor(QPalette.Disabled , QPalette.Text , QColor(120,133,148))
        self.setColor(QPalette.Disabled , QPalette.WindowText , QColor(120,133,148))
        self.setColor(QPalette.Disabled , QPalette.Base , QColor(32 , 32 , 32))

class ArcDarkBluePallete(QPalette):
     def __init__(self):
        super().__init__()
        # gray
        self.setColor(QPalette.Window, QColor(53, 57, 69))
        #light gray
        self.setColor(QPalette.WindowText, QColor(174,167,159))
        #gray
        self.setColor(QPalette.Base, QColor(64, 69, 82))
        #gray
        self.setColor(QPalette.AlternateBase, QColor(56, 60, 74))
        self.setColor(QPalette.ToolTipBase, Qt.white)
        self.setColor(QPalette.ToolTipText, Qt.white)
        #light gray
        self.setColor(QPalette.Text, QColor(174,167,159))
        #gray
        self.setColor(QPalette.Button, QColor(64, 69, 82))
        #light gray
        self.setColor(QPalette.ButtonText, QColor(174,167,159))
        #Arck red
        self.setColor(QPalette.BrightText, QColor(191,71,77))
        #blue
        self.setColor(QPalette.Link, QColor(42, 130, 218))
        #Arc Blue
        self.setColor(QPalette.Highlight , QColor(82,148,226))
        self.setColor(QPalette.HighlightedText, Qt.white)

        self.setColor(QPalette.Disabled,QPalette.Window, QColor(51,51,51))
        self.setColor(QPalette.Disabled , QPalette.ButtonText , QColor(51,51,51))
        self.setColor(QPalette.Disabled , QPalette.Text , QColor(120,133,148))
        self.setColor(QPalette.Disabled , QPalette.WindowText , QColor(120,133,148))
        self.setColor(QPalette.Disabled , QPalette.Base , QColor(32 , 32 , 32))

class LightRedPallete(QPalette):
    def __init__(self):
        super().__init__()
        #220 220 220 is light gray
        self.setColor(QPalette.Window, QColor(220, 220, 220))
        #0 0 0 is black
        self.setColor(QPalette.WindowText, Qt.black)
        #255 255 255 is white
        self.setColor(QPalette.Base, Qt.white)
        #gray
        self.setColor(QPalette.AlternateBase, QColor(220, 220, 220))
        self.setColor(QPalette.ToolTipBase, Qt.white)
        self.setColor(QPalette.ToolTipText, Qt.white)
        #light gray
        self.setColor(QPalette.Text, Qt.black )

        #gray
        self.setColor(QPalette.Button, QColor(220, 220, 220))
        #light gray
        self.setColor(QPalette.ButtonText, Qt.black)
        #numix red
        self.setColor(QPalette.BrightText, QColor(214,73,55))
        #blue
        self.setColor(QPalette.Link, QColor(42, 130, 218))
        #numix red
        self.setColor(QPalette.Highlight , QColor(214,73,55))
        self.setColor(QPalette.HighlightedText, Qt.white)

        self.setColor(QPalette.Disabled,QPalette.Window, Qt.lightGray)
        self.setColor(QPalette.Disabled , QPalette.ButtonText , QColor(51,51,51))
        self.setColor(QPalette.Disabled , QPalette.Text , QColor(122,118,113))
        self.setColor(QPalette.Disabled , QPalette.WindowText , QColor(122,118,113))
        self.setColor(QPalette.Disabled , QPalette.Base , Qt.lightGray)

class LightBluePallete(QPalette):
    def __init__(self):
        super().__init__()
        #220 220 220 is light gray
        self.setColor(QPalette.Window, QColor(220, 220, 220))
        #0 0 0 is black
        self.setColor(QPalette.WindowText, Qt.black)
        #255 255 255 is white
        self.setColor(QPalette.Base, Qt.white)
        #gray
        self.setColor(QPalette.AlternateBase, QColor(220, 220, 220))
        self.setColor(QPalette.ToolTipBase, Qt.white)
        self.setColor(QPalette.ToolTipText, Qt.white)
        #light gray
        self.setColor(QPalette.Text, Qt.black )

        #gray
        self.setColor(QPalette.Button, QColor(220, 220, 220))
        #light gray
        self.setColor(QPalette.ButtonText, Qt.black)
        #numix blue
        self.setColor(QPalette.BrightText, QColor(42 ,130 ,218))
        #blue
        self.setColor(QPalette.Link, QColor(42, 130, 218))
        #numix blue
        self.setColor(QPalette.Highlight , QColor(42 ,130 ,218))
        self.setColor(QPalette.HighlightedText, Qt.white)

        self.setColor(QPalette.Disabled,QPalette.Window, Qt.lightGray)
        self.setColor(QPalette.Disabled , QPalette.ButtonText , QColor(51,51,51))
        self.setColor(QPalette.Disabled , QPalette.Text , QColor(122,118,113))
        self.setColor(QPalette.Disabled , QPalette.WindowText , QColor(122,118,113))
        self.setColor(QPalette.Disabled , QPalette.Base , Qt.lightGray)

  
