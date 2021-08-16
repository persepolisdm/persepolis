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
from PySide6 import QtSvg
from PySide6.QtWidgets import QDesktopWidget, QHBoxLayout, QVBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt, QSize, QRect, QPoint


class Windows_Notification_UI(QWidget):
    def __init__(self, parent, persepolis_setting):
        super().__init__(parent)

        self.persepolis_setting = persepolis_setting

        # set ui direction
        ui_direction = self.persepolis_setting.value('ui_direction')

        if ui_direction == 'rtl':
            self.setLayoutDirection(Qt.RightToLeft)

        elif ui_direction in 'ltr':
            self.setLayoutDirection(Qt.LeftToRight)

        # set size
        self.resize(QSize(400, 80))
        self.setFixedWidth(400)

        # show this widget as ToolTip widget
        self.setWindowFlags(Qt.ToolTip)

        # find bottom right position
        bottom_right_screen = QDesktopWidget().availableGeometry().bottomRight()

        bottom_right_notification = QRect(QPoint(0, 0), QSize(410, 120))
        bottom_right_notification.moveBottomRight(bottom_right_screen)
        self.move(bottom_right_notification.topLeft())

        # get persepolis icon path
        icons = ':/' + \
            str(self.persepolis_setting.value('settings/icons')) + '/'

        notification_horizontalLayout = QHBoxLayout(self)

        # persepolis icon
        svgWidget = QtSvg.QSvgWidget(':/persepolis.svg')
        svgWidget.setFixedSize(QSize(64, 64))

        notification_horizontalLayout.addWidget(svgWidget)

        notification_verticalLayout = QVBoxLayout()

        # 2 labels for notification messages
        self.label1 = QLabel(self)
        self.label1.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label1.setStyleSheet("font-weight: bold")
        self.label1.setWordWrap(True)

        self.label2 = QLabel(self)
        self.label2.setWordWrap(True)
        self.label2.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        notification_verticalLayout.addWidget(self.label1)
        notification_verticalLayout.addWidget(self.label2)
        notification_horizontalLayout.addLayout(notification_verticalLayout)
