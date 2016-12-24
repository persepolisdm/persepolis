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
#

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget , QLabel , QVBoxLayout
from PyQt5.QtGui import QPixmap
import icons_resource

class GreetingWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowModality(QtCore.Qt.WindowModal)

        verticalLayout = QVBoxLayout(self)
        self.icon_label = QtWidgets.QLabel(self)
        self.icon_label.setMaximumSize(QtCore.QSize(504,232))
        self.icon_label.setPixmap(QPixmap(":/user_greeting"))
        verticalLayout.addWidget(self.icon_label)
 
