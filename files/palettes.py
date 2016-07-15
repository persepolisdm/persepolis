#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
        self.setColor(QPalette.Disabled , QPalette.Text , QColor(51,51,51))
        self.setColor(QPalette.Disabled , QPalette.WindowText , QColor(51,51,51))
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
        self.setColor(QPalette.Disabled , QPalette.Text , QColor(51,51,51))
        self.setColor(QPalette.Disabled , QPalette.WindowText , QColor(51,51,51))
        self.setColor(QPalette.Disabled , QPalette.Base , QColor(32 , 32 , 32))


