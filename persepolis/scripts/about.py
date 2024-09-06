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

try:
    from PySide6.QtCore import QFile, QIODevice, QPoint, QSettings, QSize, Qt, QTextStream
    from PySide6.QtGui import QCloseEvent, QIcon, QKeyEvent
except:
    from PyQt5.QtCore import QFile, QIODevice, QPoint, QSettings, QSize, Qt, QTextStream
    from PyQt5.QtGui import QCloseEvent, QIcon, QKeyEvent

from persepolis.gui import resources  # noqa: F401
from persepolis.gui.about_ui import AboutWindowUi


class AboutWindow(AboutWindowUi):
    def __init__(self, persepolis_setting: QSettings) -> None:
        super().__init__(persepolis_setting)

        self.persepolis_setting = persepolis_setting

        # setting window size and position
        size = self.persepolis_setting.value('AboutWindow/size', QSize(545, 375))
        position = self.persepolis_setting.value('AboutWindow/position', QPoint(300, 300))

        # read translators.txt files.
        # this file contains all translators.
        f = QFile(':/translators.txt')

        f.open(QIODevice.ReadOnly | QFile.Text)
        f_text = QTextStream(f).readAll()
        f.close()

        self.translators_textEdit.insertPlainText(f_text)

        self.resize(size)
        self.move(position)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            self.close()

    def changeIcon(self, icons: str) -> None:
        icons = ':/' + str(icons) + '/'
        self.pushButton.setIcon(QIcon(icons + 'ok'))

    def closeEvent(self, event: QCloseEvent) -> None:
        # saving window size and position
        self.persepolis_setting.setValue('AboutWindow/size', self.size())
        self.persepolis_setting.setValue('AboutWindow/position', self.pos())
        self.persepolis_setting.sync()
        event.accept()
