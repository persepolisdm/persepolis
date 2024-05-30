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
    from PySide6.QtWidgets import QDateTimeEdit
    from PySide6.QtCore import QSettings, Qt
except:
    from PyQt5.QtWidgets import QDateTimeEdit
    from PyQt5.QtCore import QSettings, Qt

# import persepolis_setting
persepolis_setting = QSettings('persepolis_download_manager', 'persepolis')

# check ui_direction RTL or LTR
ui_direction = persepolis_setting.value('ui_direction')


class MyQDateTimeEdit(QDateTimeEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        # change ui direction from rtl to ltr
        if ui_direction == 'rtl':
            self.setLayoutDirection(Qt.LeftToRight)
