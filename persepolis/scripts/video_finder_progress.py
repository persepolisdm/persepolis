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
from persepolis.gui.video_finder_progress_ui import VideoFinderProgressWindowUi
from persepolis.scripts.shutdown import shutDown

os_type = platform.system()


class ShutDownThread(QThread):
    def __init__(self, parent: QWidget, category: str, password: str | None = None) -> None:
        QThread.__init__(self)
        self.category = category
        self.password = password
        self.main_window = parent

    def run(self) -> None:
        shutDown(self.main_window, category=self.category, password=self.password)


class VideoFinderProgressWindow(VideoFinderProgressWindowUi):
    def __init__(self, parent: QWidget, gid_list: list[str], persepolis_setting: QSettings) -> None:
        super().__init__(persepolis_setting)
        self.persepolis_setting = persepolis_setting
        self.main_window = parent

        # first item in the gid_list is related to video's link and second item is related to audio's link.
        self.gid_list = gid_list

        # this variable can be changed by checkDownloadInfo method in mainwindow.py
        # self.gid defines that which gid is downloaded.
        self.gid = gid_list[0]

        # this variable used as category name in ShutDownThread
        self.video_finder_plus_gid = 'video_finder_' + str(gid_list[0])

        # connect signals and sluts
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

        self.after_comboBox.currentIndexChanged.connect(self.afterComboBoxChanged)

        # speed limit
        self.limit_dial.setValue(10)
        self.limit_dial.sliderReleased.connect(self.limitDialIsReleased)
        self.limit_dial.valueChanged.connect(self.limitDialIsChanged)
        self.limit_label.setText('Speed : Maximum')

        # set window size and position
        size = self.persepolis_setting.value('ProgressWindow/size', QSize(595, 274))
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
        # cancel shut down progress
        dictionary = {'category': self.video_finder_plus_gid, 'shutdown': 'canceled'}

        self.main_window.temp_db.updateQueueTable(dictionary)

        if self.status == 'downloading':
            # search gid in download_sessions_list
            for download_session_dict in self.main_window.download_sessions_list:
                if download_session_dict['gid'] == self.gid:
                    # unpause download
                    download_session_dict['download_session'].downloadStop()
                    break

    def afterComboBoxChanged(self, _connect: int) -> None:
        self.after_pushButton.setEnabled(True)

    def afterCheckBoxToggled(self, _checkBoxes: bool) -> None:
        if self.after_checkBox.isChecked():
            self.after_frame.setEnabled(True)
        else:
            # so user canceled shutdown after download
            # write cancel value in data_base for this gid
            dictionary = {'category': self.video_finder_plus_gid, 'shutdown': 'canceled'}

            self.main_window.temp_db.updateQueueTable(dictionary)

    def afterPushButtonPressed(self, _button: QPushButton) -> None:
        self.after_pushButton.setEnabled(False)

        # For Linux and Mac OSX and FreeBSD and OpenBSD
        if os_type != Os.WINDOWS:
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
                    # value of 'shutdown' will changed in temp_db for this progress
                    # and "wait" word will be written for this value.
                    # (see ShutDownThread and shutdown.py for more information)
                    # shutDown method will check that value in a loop .
                    # when "wait" changes to "shutdown" then shutdown.py script
                    # will shut down the system.

                    shutdown_enable = ShutDownThread(self.main_window, self.video_finder_plus_gid, passwd)
                    self.main_window.threadPool.append(shutdown_enable)
                    self.main_window.threadPool[-1].start()

                else:
                    self.after_checkBox.setChecked(False)
            else:
                self.after_checkBox.setChecked(False)

        else:
            # for Windows
            for _gid in self.gid_list:
                shutdown_enable = ShutDownThread(self.main_window, self.video_finder_plus_gid)
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
