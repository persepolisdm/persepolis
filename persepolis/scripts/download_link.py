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
    from PySide6.QtCore import QThread, Signal
except:
    from PyQt5.QtCore import QThread
    from PyQt5.QtCore import pyqtSignal as Signal


# this thread starts download.
class DownloadLink(QThread):
    def __init__(self, gid, download_session, main_window):
        QThread.__init__(self)
        self.gid = gid
        self.download_session = download_session
        self.main_window = main_window

    def run(self):
        # add gid of download to the active gids in temp_db
        # or update data base , if it was existed before
        try:
            self.main_window.temp_db.insertInSingleTable(self.gid)
        except:
            # release lock
            self.main_window.temp_db.lock = False
            dictionary = {'gid': self.gid, 'status': 'active'}
            self.main_window.temp_db.updateSingleTable(dictionary)

        self.download_session.start()
