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

from __future__ import annotations

try:
    from PySide6.QtCore import QCoreApplication, QLocale, QPoint, QSettings, QSize, Qt, QThread, QTranslator
    from PySide6.QtGui import QCloseEvent, QIcon, QKeyEvent
    from PySide6.QtWidgets import QInputDialog, QLineEdit, QPushButton, QWidget
except:
    from PyQt5.QtCore import QCoreApplication, QLocale, QPoint, QSettings, QSize, Qt, QThread, QTranslator
    from PyQt5.QtGui import QCloseEvent, QIcon, QKeyEvent
    from PyQt5.QtWidgets import QInputDialog, QLineEdit, QPushButton, QWidget

import platform
import subprocess

from persepolis.constants import Os
from persepolis.gui.progress_ui import ProgressWindowUi
from persepolis.scripts.shutdown import shutDown

os_type = platform.system()


class ShutDownThread(QThread):
    def __init__(self, parent: QWidget, gid: str, password: str | None = None) -> None:
        QThread.__init__(self)
        self.gid = gid
        self.password = password
        self.main_window = parent

    def run(self) -> None:
        shutDown(self.main_window, gid=self.gid, password=self.password)


class ProgressWindow(ProgressWindowUi):
    def __init__(self, parent: QWidget, gid: str, persepolis_setting: QSettings) -> None:
        super().__init__(persepolis_setting)
        self.persepolis_setting = persepolis_setting
        self.main_window = parent
        self.gid = gid
        self.status = None
        self.resume_pushButton.clicked.connect(self.resumePushButtonPressed)
        self.stop_pushButton.clicked.connect(self.stopPushButtonPressed)
        self.pause_pushButton.clicked.connect(self.pausePushButtonPressed)
        self.download_progressBar.setValue(0)

        self.after_frame.setEnabled(False)
        self.after_checkBox.toggled.connect(self.afterCheckBoxToggled)

        self.after_pushButton.clicked.connect(self.afterPushButtonPressed)

        # add support for other languages
        locale = str(self.persepolis_setting.value('settings/locale'))
        QLocale.setDefault(QLocale(locale))
        self.translator = QTranslator()
        if self.translator.load(':/translations/locales/ui_' + locale, 'ts'):
            QCoreApplication.installTranslator(self.translator)

        # speed limit
        self.limit_dial.setValue(10)
        self.limit_dial.sliderReleased.connect(self.limitDialIsReleased)
        self.limit_dial.valueChanged.connect(self.limitDialIsChanged)
        self.limit_label.setText('Speed : Maximum')

        self.after_comboBox.currentIndexChanged.connect(self.afterComboBoxChanged)

        # set window size and position
        size = self.persepolis_setting.value('ProgressWindow/size', QSize(617, 304))
        position = self.persepolis_setting.value('ProgressWindow/position', QPoint(300, 300))
        self.resize(size)
        self.move(position)

    # close window with ESC key
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            self.close()

    def closeEvent(self, _event: QCloseEvent) -> None:
        # save window size and position
        self.persepolis_setting.setValue('ProgressWindow/size', self.size())
        self.persepolis_setting.setValue('ProgressWindow/position', self.pos())
        self.persepolis_setting.sync()

        self.hide()

    def resumePushButtonPressed(self, _button: QPushButton) -> None:
        if self.status == 'paused':
            # search gid in download_sessions_list
            for download_session_dict in self.main_window.download_sessions_list:
                if download_session_dict['gid'] == self.gid:
                    # unpause download
                    download_session_dict['download_session'].downloadUnpause()
                    break

    def pausePushButtonPressed(self, _button: QPushButton) -> None:
        if self.status == 'downloading':
            # search gid in download_sessions_list
            for download_session_dict in self.main_window.download_sessions_list:
                if download_session_dict['gid'] == self.gid:
                    # unpause download
                    download_session_dict['download_session'].downloadPause()
                    break

    def stopPushButtonPressed(self, _button: QPushButton) -> None:
        download_dict = {'gid': self.gid, 'shutdown': 'canceled'}

        self.main_window.temp_db.updateSingleTable(download_dict)

        if self.status != 'stopped':
            # search gid in download_sessions_list
            for download_session_dict in self.main_window.download_sessions_list:
                if download_session_dict['gid'] == self.gid:
                    # stop download
                    download_session_dict['download_session'].downloadStop()
                    break

    def afterComboBoxChanged(self, _connect: str) -> None:
        self.after_pushButton.setEnabled(True)

    def afterCheckBoxToggled(self, _checkBoxes: bool) -> None:
        if self.after_checkBox.isChecked():
            self.after_frame.setEnabled(True)
        else:
            # so user canceled shutdown after download
            # write cancel value in data_base for this gid
            self.after_frame.setEnabled(False)

            download_dict = {'gid': self.gid, 'shutdown': 'canceled'}

            self.main_window.temp_db.updateSingleTable(download_dict)

    def afterPushButtonPressed(self, _button: QPushButton) -> None:
        self.after_pushButton.setEnabled(False)

        if os_type != Os.WINDOWS:  # For Linux and Mac OSX and FreeBSD and OpenBSD
            # get root password
            passwd, ok = QInputDialog.getText(self, 'PassWord', 'Please enter root password:', QLineEdit.Password)

            if ok:
                # check password is true or not!
                pipe = subprocess.Popen(
                    ['sudo', '-S', 'echo', 'hello'],
                    stdout=subprocess.DEVNULL,
                    stdin=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    shell=False,
                )

                pipe.communicate(passwd.encode())

                answer = pipe.wait()

                # Wrong password
                while answer != 0:
                    passwd, ok = QInputDialog.getText(
                        self, 'PassWord', 'Wrong Password!\nPlease try again.', QLineEdit.Password
                    )

                    if ok:
                        # checking password
                        pipe = subprocess.Popen(
                            ['sudo', '-S', 'echo', 'hello'],
                            stdout=subprocess.DEVNULL,
                            stdin=subprocess.PIPE,
                            stderr=subprocess.DEVNULL,
                            shell=False,
                        )

                        pipe.communicate(passwd.encode())

                        answer = pipe.wait()

                    else:
                        ok = False
                        break

                if ok is not False:
                    # if user selects shutdown option after download progress,
                    # value of 'shutdown' will changed in temp_db for this gid
                    # and "wait" word will be written for this value.
                    # (see ShutDownThread and shutdown.py for more information)
                    # shutDown method will check that value in a loop .
                    # when "wait" changes to "shutdown" then shutdown.py script
                    # will shut down the system.
                    shutdown_enable = ShutDownThread(self.main_window, self.gid, passwd)
                    self.main_window.threadPool.append(shutdown_enable)
                    self.main_window.threadPool[-1].start()

                else:
                    self.after_checkBox.setChecked(False)
            else:
                self.after_checkBox.setChecked(False)

        else:  # for Windows
            shutdown_enable = ShutDownThread(self.main_window, self.gid)
            self.main_window.threadPool.append(shutdown_enable)
            self.main_window.threadPool[-1].start()

    def limitDialIsReleased(self) -> None:
        limit_value = self.limit_dial.value()

        # set speed limit value
        for download_session_dict in self.main_window.download_sessions_list:
            if download_session_dict['gid'] == self.gid:
                # limit  download speed
                download_session_dict['download_session'].limitSpeed(limit_value)
                break

    def limitDialIsChanged(self, _button: QPushButton) -> None:
        if self.limit_dial.value() == 10:  # noqa: PLR2004
            self.limit_label.setText('Speed : Maximum')
        elif self.limit_dial.value() == 0:
            self.limit_label.setText('Speed : Minimum')
        else:
            self.limit_label.setText('Speed')

    def changeIcon(self, icons: str) -> None:
        icons = ':/' + str(icons) + '/'

        self.resume_pushButton.setIcon(QIcon(icons + 'play'))
        self.pause_pushButton.setIcon(QIcon(icons + 'pause'))
        self.stop_pushButton.setIcon(QIcon(icons + 'stop'))
