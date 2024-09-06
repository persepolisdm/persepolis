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
    from PySide6.QtCore import QDir, QPoint, QSettings, QSize, Qt, QThread, Signal
    from PySide6.QtGui import QCloseEvent, QIcon, QKeyEvent
    from PySide6.QtWidgets import QFileDialog, QPushButton, QTableWidgetItem, QWidget
except:
    from PyQt5.QtCore import QDir, QPoint, QSettings, QSize, Qt, QThread
    from PyQt5.QtCore import pyqtSignal as Signal
    from PyQt5.QtGui import QCloseEvent, QIcon, QKeyEvent
    from PyQt5.QtWidgets import QFileDialog, QPushButton, QTableWidgetItem, QWidget

import os
from copy import deepcopy
from functools import partial
from typing import Any, Callable

from persepolis.gui.text_queue_ui import TextQueueUi
from persepolis.scripts import logger, spider


# This thread finds filename
class QueueSpiderThread(QThread):
    QUEUESPIDERRETURNEDFILENAME = Signal(str)

    def __init__(self, download_dict: dict[str, Any]) -> None:
        QThread.__init__(self)
        self.dict = download_dict

    def run(self) -> None:
        try:
            filename = spider.queueSpider(self.dict)
            if filename:
                self.QUEUESPIDERRETURNEDFILENAME.emit(filename)
            else:
                logger.logObj.error("Spider couldn't find download information", exc_info=True)

        except Exception as e:
            logger.logObj.error("Spider couldn't find download information", exc_info=True)

            logger.logObj.error(str(e), exc_info=True)


class BrowserPluginQueue(TextQueueUi):
    def __init__(
        self,
        parent: QWidget,
        list_of_links: list[str],
        callback: Callable[[dict[str, Any], str], None],
        persepolis_setting: QSettings,
    ) -> None:
        super().__init__(persepolis_setting)
        self.persepolis_setting = persepolis_setting
        self.callback = callback
        self.parent = parent
        self.list_of_links = list_of_links

        global icons  # noqa: PLW0603
        icons = ':/' + str(self.persepolis_setting.value('settings/icons')) + '/'

        self.list_of_links.reverse()

        k = 1
        for link_dict in self.list_of_links:
            # add row to the links_table
            self.links_table.insertRow(0)

            # file_name
            file_name = link_dict['out'] if link_dict.get('out') else '***'

            if file_name == '***':
                # spider finds file name
                new_spider = QueueSpiderThread(link_dict)
                self.parent.threadPool.append(new_spider)
                self.parent.threadPool[-1].start()
                self.parent.threadPool[-1].QUEUESPIDERRETURNEDFILENAME.connect(
                    partial(self.parent.queueSpiderCallBack, child=self, row_number=len(self.list_of_links) - k)
                )
            k = k + 1

            item = QTableWidgetItem(file_name)
            # add checkbox to the item
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setCheckState(Qt.Checked)

            # insert file_name
            self.links_table.setItem(0, 0, item)

            # find link
            link = link_dict['link']
            item = QTableWidgetItem(str(link))

            # insert link
            self.links_table.setItem(0, 1, item)

        # get categories name and add them to add_queue_comboBox
        categories_list = self.parent.persepolis_db.categoriesList()

        for queue in categories_list:
            if queue != 'All Downloads':
                self.add_queue_comboBox.addItem(queue)

        self.add_queue_comboBox.addItem(QIcon(icons + 'add_queue'), 'Create new queue')

        # entry initialization
        global connections  # noqa: PLW0603
        connections = int(self.persepolis_setting.value('settings/connections'))
        global download_path  # noqa: PLW0603
        download_path = str(self.persepolis_setting.value('settings/download_path'))

        # initialization
        self.connections_spinBox.setValue(connections)
        self.download_folder_lineEdit.setText(download_path)
        self.download_folder_lineEdit.setEnabled(False)

        # ip_lineEdit initialization
        settings_ip = self.persepolis_setting.value('add_link_initialization/ip', None)
        if settings_ip:
            self.ip_lineEdit.setText(str(settings_ip))

        # proxy user lineEdit initialization
        settings_proxy_user = self.persepolis_setting.value('add_link_initialization/proxy_user', None)
        if settings_proxy_user:
            self.proxy_user_lineEdit.setText(str(settings_proxy_user))

        # port_spinBox initialization
        settings_port = self.persepolis_setting.value('add_link_initialization/port', 0)

        self.port_spinBox.setValue(int(int(settings_port)))

        # download UserName initialization
        settings_download_user = self.persepolis_setting.value('add_link_initialization/download_user', None)
        if settings_download_user:
            self.download_user_lineEdit.setText(str(settings_download_user))

        # http or socks5 initialization
        settings_proxy_type = self.persepolis_setting.value('add_link_initialization/proxy_type', None)

        # default is http
        if settings_proxy_type == 'socks5':
            self.socks5_radioButton.setChecked(True)

        elif settings_proxy_type == 'https':
            self.https_radioButton.setChecked(True)

        else:
            self.http_radioButton.setChecked(True)

        # connect folder_pushButton
        self.folder_pushButton.clicked.connect(self.changeFolder)

        # connect OK and cancel button

        self.cancel_pushButton.clicked.connect(self.close)
        self.ok_pushButton.clicked.connect(self.okButtonPressed)

        # connect select_all_pushButton  deselect_all_pushButton
        self.select_all_pushButton.clicked.connect(self.selectAll)

        self.deselect_all_pushButton.clicked.connect(self.deselectAll)

        # frames and checkBoxes
        self.proxy_frame.setEnabled(False)
        self.proxy_checkBox.toggled.connect(self.proxyFrame)

        self.download_frame.setEnabled(False)
        self.download_checkBox.toggled.connect(self.downloadFrame)

        # set focus to ok button
        self.ok_pushButton.setFocus()

        # add_queue_comboBox event
        self.add_queue_comboBox.currentIndexChanged.connect(self.queueChanged)

        # set window size and position
        size = self.persepolis_setting.value('TextQueue/size', QSize(700, 500))
        position = self.persepolis_setting.value('TextQueue/position', QPoint(300, 300))
        self.resize(size)
        self.move(position)

    # this method selects all links in links_table
    def selectAll(self, _button: QPushButton) -> None:
        for i in range(self.links_table.rowCount()):
            item = self.links_table.item(i, 0)
            item.setCheckState(Qt.Checked)

    # this method unchecks all check boxes
    def deselectAll(self, _button: QPushButton) -> None:
        for i in range(self.links_table.rowCount()):
            item = self.links_table.item(i, 0)
            item.setCheckState(Qt.Unchecked)

    # this method is called, when user changes add_queue_comboBox
    def queueChanged(self, combo: int) -> None:
        if str(self.add_queue_comboBox.currentText()) == 'Create new queue':
            # if user want to create new queue, then call createQueue method from mainwindow(parent)
            new_queue = self.parent.createQueue(combo)

            if new_queue:
                # clear comboBox
                self.add_queue_comboBox.clear()

                # load queue list again!
                queues_list = self.parent.persepolis_db.categoriesList()
                for queue in queues_list:
                    if queue != 'All Downloads':
                        self.add_queue_comboBox.addItem(queue)

                self.add_queue_comboBox.addItem(QIcon(icons + 'add_queue'), 'Create new queue')

                # finding index of new_queue and setting comboBox for it
                index = self.add_queue_comboBox.findText(str(new_queue))
                self.add_queue_comboBox.setCurrentIndex(index)
            else:
                self.add_queue_comboBox.setCurrentIndex(0)

    # activate frames if checkBoxes checked
    def proxyFrame(self, _checkBox: bool) -> None:
        if self.proxy_checkBox.isChecked():
            self.proxy_frame.setEnabled(True)
        else:
            self.proxy_frame.setEnabled(False)

    def downloadFrame(self, _checkBox: bool) -> None:
        if self.download_checkBox.isChecked():
            self.download_frame.setEnabled(True)
        else:
            self.download_frame.setEnabled(False)

    def changeFolder(self, _button: QPushButton) -> None:
        fname = QFileDialog.getExistingDirectory(self, 'Select a directory', download_path)

        if fname:
            # Returns pathName with the '/' separators converted to separators that are appropriate for the underlying operating system.
            # On Windows, toNativeSeparators("c:/winnt/system32") returns
            # "c:\winnt\system32".
            fname = QDir.toNativeSeparators(fname)

        if os.path.isdir(fname):
            self.download_folder_lineEdit.setText(fname)

    def okButtonPressed(self, _button: QPushButton) -> None:
        # write user's input data to init file
        self.persepolis_setting.setValue('add_link_initialization/ip', self.ip_lineEdit.text())
        self.persepolis_setting.setValue('add_link_initialization/port', self.port_spinBox.value())
        self.persepolis_setting.setValue('add_link_initialization/proxy_user', self.proxy_user_lineEdit.text())
        self.persepolis_setting.setValue('add_link_initialization/download_user', self.download_user_lineEdit.text())

        # http, https or socks5 proxy
        if self.http_radioButton.isChecked() is True:
            proxy_type = 'http'
            self.persepolis_setting.setValue('add_link_initialization/proxy_type', 'http')

        elif self.https_radioButton.isChecked() is True:
            proxy_type = 'https'
            self.persepolis_setting.setValue('add_link_initialization/proxy_type', 'https')

        else:
            proxy_type = 'socks5'
            self.persepolis_setting.setValue('add_link_initialization/proxy_type', 'socks5')

        if not (self.proxy_checkBox.isChecked()):
            ip = None
            port = None
            proxy_user = None
            proxy_passwd = None
            proxy_type = None
        else:
            ip = self.ip_lineEdit.text()
            if not (ip):
                ip = None
            port = self.port_spinBox.value()
            if not (port):
                port = None
            proxy_user = self.proxy_user_lineEdit.text()
            if not (proxy_user):
                proxy_user = None
            proxy_passwd = self.proxy_pass_lineEdit.text()
            if not (proxy_passwd):
                proxy_passwd = None

        if not (self.download_checkBox.isChecked()):
            download_user = None
            download_passwd = None
        else:
            download_user = self.download_user_lineEdit.text()
            if not (download_user):
                download_user = None
            download_passwd = self.download_pass_lineEdit.text()
            if not (download_passwd):
                download_passwd = None

        category = str(self.add_queue_comboBox.currentText())

        connections = self.connections_spinBox.value()
        download_path = self.download_folder_lineEdit.text()

        dict_ = {
            'out': None,
            'start_time': None,
            'end_time': None,
            'link': None,
            'ip': ip,
            'port': port,
            'proxy_user': proxy_user,
            'proxy_passwd': proxy_passwd,
            'proxy_type': proxy_type,
            'download_user': download_user,
            'download_passwd': download_passwd,
            'connections': connections,
            'limit_value': 10,
            'download_path': download_path,
            'referer': None,
            'load_cookies': None,
            'user_agent': None,
            'header': None,
            'after_download': None,
        }

        # find checked links in links_table
        self.list_of_links.reverse()
        self.add_link_dictionary_list = []
        i = 0
        for row in range(self.links_table.rowCount()):
            item = self.links_table.item(row, 0)

            # if item is checked
            if item.checkState() == Qt.Checked:
                # Create a copy from dict_ and add it to add_link_dictionary_list
                self.add_link_dictionary_list.append(deepcopy(dict_))

                # get link and add it to dict_
                link = self.links_table.item(row, 1).text()
                self.add_link_dictionary_list[i]['link'] = str(link)

                # add file name to the dict_
                self.add_link_dictionary_list[i]['out'] = self.links_table.item(row, 0).text()

                input_dict = self.list_of_links[row]

                keys_list = ['referer', 'header', 'user-agent', 'load_cookies']
                for key in keys_list:
                    if key in input_dict:
                        self.add_link_dictionary_list[i][key] = dict_[key]

                i = i + 1

        # reverse list
        self.add_link_dictionary_list.reverse()

        # Create callback for mainwindow
        self.callback(self.add_link_dictionary_list, category)

        # close window
        self.close()

    # close window with ESC key
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            self.close()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.persepolis_setting.setValue('TextQueue/size', self.size())
        self.persepolis_setting.setValue('TextQueue/position', self.pos())
        self.persepolis_setting.sync()

        event.accept()

    def changeIcon(self, icons: str) -> None:
        icons = ':/' + str(icons) + '/'

        self.folder_pushButton.setIcon(QIcon(icons + 'folder'))
        self.ok_pushButton.setIcon(QIcon(icons + 'ok'))
        self.cancel_pushButton.setIcon(QIcon(icons + 'remove'))
