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
from persepolis.scripts.useful_tools import humanReadableSize
from persepolis.scripts import libtorrent_wrapper
from persepolis.scripts import logger
from functools import partial
from pathlib import Path
try:
    from PySide6.QtWidgets import QTableWidgetItem, QFileDialog
    from PySide6.QtCore import Signal, QCoreApplication, Qt, QPoint, QSize, QDir, QThread
    from PySide6.QtGui import QIcon
except:
    from PyQt5.QtWidgets import QTableWidgetItem, QFileDialog
    from PyQt5.QtCore import QCoreApplication, Qt, QPoint, QSize, QDir, QThread
    from PyQt5.QtGui import QIcon
    from PyQt5.QtCore import pyqtSignal as Signal


class GetMetaDataThread(QThread):
    NOMETADATASIGNAL = Signal(str)
    TORRENTINFORMATIONSIGNAL = Signal(list)

    def __init__(self, options_dict):
        super().__init__()
        self.magnet_link = libtorrent_wrapper.MagnetLink(options_dict)

    def run(self):
        try:
            session_parameters = self.magnet_link.createSession()
            self.magnet_link.createHandler(session_parameters)
            info = self.magnet_link.info()
        except Exception as e:
            self.NOMETADATASIGNAL.emit(str(e))
            return

        torrent_name, torrent_files_list, is_folder = libtorrent_wrapper.filesList(info)
        self.TORRENTINFORMATIONSIGNAL.emit([torrent_name, torrent_files_list, is_folder])


class AddMagnetWindow(AddMagnetWindow_ui):
    def __init__(self, parent, callback, persepolis_setting):
        super().__init__(persepolis_setting)
        self.persepolis_setting = persepolis_setting
        self.callback = callback
        self.parent = parent

        global icons
        icons = ':/' + \
            str(self.persepolis_setting.value('settings/icons')) + '/'

        # Hide files tab (second tab)
        self.queue_tabWidget.removeTab(1)

        # get categories name and add them to add_queue_comboBox
        categories_list = self.parent.persepolis_db.categoriesList()

        for queue in categories_list:
            if queue != 'All Downloads':
                self.add_queue_comboBox.addItem(queue)

        self.add_queue_comboBox.addItem(
            QIcon(icons + 'add_queue'), 'Create new queue')

        # entry initialization

        # get values from persepolis_setting
        global download_path
        download_path = str(
            self.persepolis_setting.value('settings/download_path'))

        self.download_folder_lineEdit.setText(download_path)
        self.download_folder_lineEdit.setEnabled(False)

        # ip_lineEdit initialization
        settings_ip = self.persepolis_setting.value(
            'add_link_initialization/ip', None)
        if settings_ip:
            self.ip_lineEdit.setText(str(settings_ip))

        # proxy user lineEdit initialization
        settings_proxy_user = self.persepolis_setting.value(
            'add_link_initialization/proxy_user', None)
        if settings_proxy_user:
            self.proxy_user_lineEdit.setText(str(settings_proxy_user))

        # port_spinBox initialization
        settings_port = self.persepolis_setting.value(
            'add_link_initialization/port', 0)

        self.port_spinBox.setValue(int(int(settings_port)))

        # http or socks5 initialization
        settings_proxy_type = self.persepolis_setting.value(
            'add_link_initialization/proxy_type', None)

        # default is http
        if settings_proxy_type == 'socks5':

            self.socks5_radioButton.setChecked(True)

        elif settings_proxy_type == 'https':
            self.https_radioButton.setChecked(True)

        else:
            self.http_radioButton.setChecked(True)

        # download UserName initialization
        settings_download_user = self.persepolis_setting.value(
            'add_link_initialization/download_user', None)
        if settings_download_user:
            self.download_user_lineEdit.setText(str(settings_download_user))

        # connect folder_pushButton
        self.folder_pushButton.clicked.connect(self.changeFolder)

        # connect fetch metadata push button
        self.fetch_metadata_pushButtontton.clicked.connect(self.fetchMetaData)

        # connect OK, cancel and download_later_pushButton button
        self.cancel_pushButton.clicked.connect(self.close)
        self.ok_pushButton.clicked.connect(self.okButtonPressed)
        self.download_later_pushButton.clicked.connect(
            partial(self.okButtonPressed, download_later=True))

        # connect select_all_pushButton  deselect_all_pushButton
        self.select_all_pushButton.clicked.connect(self.selectAll)

        self.deselect_all_pushButton.clicked.connect(self.deselectAll)

        # frames and checkBoxes
        self.proxy_frame.setEnabled(False)
        self.proxy_checkBox.toggled.connect(self.proxyFrame)

        self.download_frame.setEnabled(False)
        self.download_checkBox.toggled.connect(self.downloadFrame)

        self.limit_upload_frame.setEnabled(False)
        self.limit_upload_checkBox.toggled.connect(self.limitUploadFrame)

        self.limit_download_frame.setEnabled(False)
        self.limit_download_checkBox.toggled.connect(self.limitDownloadFrame)

        # disable ok_pushButton and download_later_pushButton
        self.ok_pushButton.setEnabled(False)
        self.download_later_pushButton.setEnabled(False)

        # add_queue_comboBox event
        self.add_queue_comboBox.currentIndexChanged.connect(self.queueChanged)

        # setting window size and position
        size = self.persepolis_setting.value('AddTorrentWindow/size', QSize(700, 500))
        position = self.persepolis_setting.value(
            'AddTorrentWindow/position', QPoint(300, 300))
        self.resize(size)
        self.move(position)

        # Set status
        self.status_box_textEdit.setText(
            QCoreApplication.translate("addmagnet_ui_tr", "Please enter a valid magnet link and press fetch information button"))

    # This method fetchs metadata
    def fetchMetaData(self, button):
        # Change status color to white for next status
        self.status_box_textEdit.setStyleSheet("color: Green;")

        # change status
        self.status_box_textEdit.setText(QCoreApplication.translate("addtorrent_ui_tr", "Please Wait..."))

        # Disable fetch_metadata_pushButtontton
        self.fetch_metadata_pushButtontton.setEnabled(False)

        # Get proxy information
        ip, port, proxy_user, proxy_passwd, proxy_type = self.getProxyInformation()

        # get download username and password information
        download_user, download_passwd = self.getUserPass()

        # get download link
        link = self.link_lineEdit.text()

        # get additinal information
        user_agent = self.getAdditionalInformation()

        magnet_dict = {'link': link,
                       'ip': ip,
                       'port': port,
                       'proxy_user': proxy_user,
                       'proxy_passwd': proxy_passwd,
                       'download_user': download_user,
                       'download_passwd': download_passwd,
                       'proxy_type': proxy_type,
                       'user_agent': user_agent,
                       }

        fetcher_thread = GetMetaDataThread(magnet_dict)
        self.parent.threadPool.append(fetcher_thread)
        self.parent.threadPool[-1].start()
        self.parent.threadPool[-1].TORRENTINFORMATIONSIGNAL.connect(self.metaDataIsReady)
        self.parent.threadPool[-1].NOMETADATASIGNAL.connect(self.metaDataIsNotFound)

    # Add files to the table
    def metaDataIsReady(self, info_list):
        # show file tab
        self.queue_tabWidget.insertTab(1, self.links_tab, QCoreApplication.translate("addtorrent_ui_tr", 'Files'))
        self.queue_tabWidget.setCurrentIndex(1)

        self.torrent_name = info_list[0]
        self.torrent_files_list = info_list[1]
        self.is_folder = info_list[2]

        # import files information to the table
        self.torrent_files_list.reverse()
        # file_list contains [file_path, file_size, index]
        for file_list in self.torrent_files_list:
            self.links_table.insertRow(0)

            # file_name
            file_path = Path(file_list[0])
            file_name = file_path.name
            index = file_list[2]
            file_size_list = humanReadableSize(file_list[1])
            file_size = str(file_size_list[0]) + ' ' + file_size_list[1]

            item = QTableWidgetItem(file_name)
            # centers horizontally and vertically
            item.setTextAlignment(Qt.AlignCenter)

            # add checkbox to the item
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setCheckState(Qt.Checked)
            # centers horizontally and vertically
            item.setTextAlignment(Qt.AlignCenter)

            # insert file_name
            self.links_table.setItem(0, 0, item)

            # insert file size
            item = QTableWidgetItem(str(file_size))
            # centers horizontally and vertically
            item.setTextAlignment(Qt.AlignCenter)

            self.links_table.setItem(0, 1, item)

            # inser index
            item = QTableWidgetItem(str(index))
            self.links_table.setItem(0, 2, item)

        # Enable ok_pushButton and download_later_pushButton
        self.ok_pushButton.setEnabled(True)
        self.download_later_pushButton.setEnabled(True)

        # Disable link_lineEdit
        self.link_lineEdit.setEnabled(False)

        # Update status
        self.status_box_textEdit.setText(QCoreApplication.translate("addtorrent_ui_tr", "The operation was successful."))

    # Get and show error in status_box_textEdit
    def metaDataIsNotFound(self, error):
        # Enable fetch_metadata_pushButtontton
        self.fetch_metadata_pushButtontton.setEnabled(True)

        # Update status with red color
        error = "ERROR:\n{}".format(error)
        self.status_box_textEdit.setStyleSheet("color: red;")
        self.status_box_textEdit.setText(error)
        logger.sendToLog(error, "ERROR")

    # this method checks all check boxes
    def selectAll(self, button):
        for i in range(self.links_table.rowCount()):
            item = self.links_table.item(i, 0)
            item.setCheckState(Qt.Checked)

    # this method deselect all check boxes
    def deselectAll(self, button):
        for i in range(self.links_table.rowCount()):
            item = self.links_table.item(i, 0)
            item.setCheckState(Qt.Unchecked)

    # this method is called, when user changes add_queue_comboBox
    def queueChanged(self, combo):
        if str(self.add_queue_comboBox.currentText()) == 'Create new queue':
            # if user want to create new queue, then callback
            # createQueue method from mainwindow(parent)
            new_queue = self.parent.createQueue(combo)

            if new_queue:
                # clear comboBox
                self.add_queue_comboBox.clear()

                # load queue list again!
                queues_list = self.parent.persepolis_db.categoriesList()
                for queue in queues_list:
                    if queue != 'All Downloads':
                        self.add_queue_comboBox.addItem(queue)

                self.add_queue_comboBox.addItem(
                    QIcon(icons + 'add_queue'), 'Create new queue')

                # finding index of new_queue and setting comboBox for it
                index = self.add_queue_comboBox.findText(str(new_queue))
                self.add_queue_comboBox.setCurrentIndex(index)
            else:
                self.add_queue_comboBox.setCurrentIndex(0)

    # activate frames if checkBoxes checked
    def proxyFrame(self, checkBox):

        if self.proxy_checkBox.isChecked():
            self.proxy_frame.setEnabled(True)
        else:
            self.proxy_frame.setEnabled(False)

    def downloadFrame(self, checkBox):

        if self.download_checkBox.isChecked():
            self.download_frame.setEnabled(True)
        else:
            self.download_frame.setEnabled(False)

    def limitDownloadFrame(self, checkBox):

        if self.limit_download_checkBox.isChecked():
            self.limit_download_frame.setEnabled(True)
        else:
            self.limit_download_frame.setEnabled(False)

    def limitUploadFrame(self, checkBox):
        if self.limit_upload_checkBox.isChecked():
            self.limit_upload_frame.setEnabled(True)
        else:
            self.limit_upload_frame.setEnabled(False)

    def changeFolder(self, button):
        fname = QFileDialog.getExistingDirectory(
            self, 'Select a directory', download_path)

        if fname:
            # Returns pathName with the '/' separators converted to
            # separators that are appropriate for the underlying
            # operating system.
            # On Windows, toNativeSeparators("c:/winnt/system32") returns
            # "c:\winnt\system32".
            fname = QDir.toNativeSeparators(fname)

            path = Path(fname)
            if path.is_dir():
                self.download_folder_lineEdit.setText(fname)

    # this method returns upload and download limit speed
    def getLimitSpeedInformation(self):
        if self.limit_download_checkBox.isChecked() is True:
            download_limit = self.limit_download_spinBox.value()
            download_limit *= 1024
        else:
            download_limit = None

        if self.limit_upload_checkBox.isChecked() is True:
            upload_limit = self.limit_upload_spinBox.value()
            upload_limit *= 1024
        else:
            upload_limit = None

        return download_limit, upload_limit

    # this method returns proxy information.
    def getProxyInformation(self):
        # http, https or socks5 proxy
        if self.http_radioButton.isChecked() is True:

            proxy_type = 'http'

        elif self.https_radioButton.isChecked() is True:

            proxy_type = 'https'

        else:

            proxy_type = 'socks5'

        # get proxy information
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

        return ip, port, proxy_user, proxy_passwd, proxy_type

    def getUserPass(self):
        # get download username and password information
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

        return download_user, download_passwd

    def getAdditionalInformation(self):
        # user_agent
        if self.user_agent_lineEdit.text() != '':
            user_agent = self.user_agent_lineEdit.text()
        else:
            user_agent = None

        return user_agent

    def okButtonPressed(self, button=None, download_later=False):
        # write user's input data to init file
        self.persepolis_setting.setValue(
            'add_link_initialization/ip', self.ip_lineEdit.text())
        self.persepolis_setting.setValue(
            'add_link_initialization/port', self.port_spinBox.value())
        self.persepolis_setting.setValue(
            'add_link_initialization/proxy_user',
            self.proxy_user_lineEdit.text())
        self.persepolis_setting.setValue(
            'add_link_initialization/download_user',
            self.download_user_lineEdit.text())

        # get proxy information
        ip, port, proxy_user, proxy_passwd, proxy_type = self.getProxyInformation()
        if proxy_type is not None:
            self.persepolis_setting.setValue('add_link_initialization/proxy_type', proxy_type)

        # get download and upload limit speed
        download_limit, upload_limit = self.getLimitSpeedInformation()

        # get download username and password information
        download_user, download_passwd = self.getUserPass()

        category = str(self.add_queue_comboBox.currentText())

        download_path = self.download_folder_lineEdit.text()

        # get additinal information
        user_agent = self.getAdditionalInformation()

        # set torrent_file_path for link
        dict_ = {'out': self.torrent_name,
                 'start_time': None,
                 'end_time': None,
                 'link': self.link_lineEdit.text(),
                 'ip': ip,
                 'port': port,
                 'proxy_user': proxy_user,
                 'proxy_passwd': proxy_passwd,
                 'download_user': download_user,
                 'download_passwd': download_passwd,
                 'proxy_type': proxy_type,
                 'connections': 64,
                 'limit_value': 10,
                 'download_path': download_path,
                 'referer': None,
                 'load_cookies': None,
                 'user_agent': user_agent,
                 'header': None,
                 'after_download': None,
                 'download_limit': download_limit,
                 'upload_limit': upload_limit
                 }

        # find checked links in links_table
        self.checked_files_list = []
        total_size = 0
        for row in range(self.links_table.rowCount()):
            item = self.links_table.item(row, 0)

            # if item is checked
            if (item.checkState() == Qt.Checked):
                # add file index to checked_files_list
                index = int(self.links_table.item(row, 2).text())
                self.checked_files_list.append(index)

                # find file size and add it to total size
                file_size = self.torrent_files_list[index][1]
                total_size = file_size + total_size

        # Create callback for mainwindow
        self.callback(dict_, self.torrent_files_list, self.checked_files_list, total_size, category, download_later, self.is_folder, "magnet")

        # close window
        self.close()

    # close window with ESC key
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def closeEvent(self, event):
        self.persepolis_setting.setValue('AddTorrentWindow/size', self.size())
        self.persepolis_setting.setValue('AddTorrentWindow/position', self.pos())
        self.persepolis_setting.sync()

        event.accept()

    def changeIcon(self, icons):
        icons = ':/' + str(icons) + '/'

        self.folder_pushButton.setIcon(QIcon(icons + 'folder'))
        self.ok_pushButton.setIcon(QIcon(icons + 'ok'))
        self.cancel_pushButton.setIcon(QIcon(icons + 'remove'))
