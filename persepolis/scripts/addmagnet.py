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

from persepolis.gui.addmagnet_ui import AddMagnetWindow_ui


class AddMagnetWindow(AddMagnetWindow_ui):
    def __init__(self, main_window, callback, persepolis_setting):
        super().__init__(persepolis_setting)

        # Hide status_box_textEdit
        self.status_box_textEdit.setVisible(False)
