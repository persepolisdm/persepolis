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

from persepolis.gui.windows_notification_ui import Windows_Notification_UI
from PyQt5.QtCore import QThread, pyqtSignal
from time import sleep

class TimerThread(QThread):
    TIMEISUP = pyqtSignal()

    def __init__(self, time):
        QThread.__init__(self)
        self.time = float(int(time)/1000) 

    def run(self):
        sleep(self.time)
        self.TIMEISUP.emit()


class Windows_Notification(Windows_Notification_UI):
    def __init__(self, parent, time, text1, text2, persepolis_setting):
        super().__init__(parent, persepolis_setting)
        
        # run timer and close notification after time is up.
        timer = TimerThread(time)
        parent.threadPool.append(timer)
        parent.threadPool[len(parent.threadPool) - 1].start()
        parent.threadPool[len(parent.threadPool) - 1].TIMEISUP.connect(self.close)
 
        # set text to the labels
        self.label1.setText(str(text1))
        self.label2.setText(str(text2))

    def mousePressEvent(self,event):
        self.close()

    def closeEvent(self, event):
        self.destroy()
