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

from PyQt5.QtCore import QDir , QPoint , QSize, QThread , pyqtSignal
from PyQt5.QtWidgets import QTableWidgetItem , QFileDialog
from persepolis.gui.text_queue_ui import TextQueue_Ui
from PyQt5 import QtWidgets , QtCore , QtGui
from persepolis.scripts import logger
from persepolis.scripts import spider
from PyQt5.QtGui import QIcon
from functools import partial
import os 

# This thread finds filename
class QueueSpiderThread(QThread):
    QUEUESPIDERRETURNEDFILENAME = pyqtSignal(str)

    def __init__(self, dict):
        QThread.__init__(self)
        self.dict = dict

    def run(self):
        try:
            filename = spider.queueSpider(self.dict)
            if filename:
                self.QUEUESPIDERRETURNEDFILENAME.emit(filename)
            else:
                logger.logObj.error(
                    "Spider couldn't find download information", exc_info=True)

        except Exception as e:
            # write error in log
            logger.logObj.error(
                "Spider couldn't find download information", exc_info=True)
            logger.logObj.error(
                str(e), exc_info=True)




class TextQueue(TextQueue_Ui):
    def __init__(self, parent, file_path, callback, persepolis_setting):
        super().__init__(persepolis_setting)
        self.persepolis_setting = persepolis_setting
        self.callback = callback
        self.file_path = file_path
        self.parent = parent

        global icons
        icons = ':/' + \
            str(self.persepolis_setting.value('settings/icons')) + '/'

        # read text file lines and put links in list format.
        f = open(self.file_path)
        f_links_list = f.readlines()
        f.close()

        f_links_list.reverse()

        # check links! links must be started with http or https or ftp
        link_list = []
        for link in f_links_list:
            text = link.strip()
            if ("tp:/" in text[2:6]) or ("tps:/" in text[2:7]):
                link_list.append(text)

        k = 1
        for link in link_list:
            self.links_table.insertRow(0)

            # file_name
            file_name = '***'
            dict = {'link': link}

            # spider finds file name
            new_spider = QueueSpiderThread(dict)
            self.parent.threadPool.append(new_spider)
            self.parent.threadPool[len(self.parent.threadPool) - 1].start()
            self.parent.threadPool[len(self.parent.threadPool) - 1].QUEUESPIDERRETURNEDFILENAME.connect(
                partial(self.parent.queueSpiderCallBack, child=self, row_number=len(link_list) - k))
            k = k + 1

            item = QTableWidgetItem(file_name)

            # add checkbox to the item
            item.setFlags(QtCore.Qt.ItemIsUserCheckable |
                          QtCore.Qt.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.Checked)

            # insert file_name
            self.links_table.setItem(0, 0, item)

            # insert link
            item = QTableWidgetItem(str(link))
            self.links_table.setItem(0, 1, item)

# get categories name and add them to add_queue_comboBox
        categories_list = self.parent.persepolis_db.categoriesList()
 
        for queue in categories_list:
            if queue != 'All Downloads':
                self.add_queue_comboBox.addItem(queue)

        self.add_queue_comboBox.addItem(
            QIcon(icons + 'add_queue'), 'Create new queue')

# entry initialization

        # get values from persepolis_setting
        global connections
        connections = int(
            self.persepolis_setting.value('settings/connections'))
        global download_path
        download_path = str(
            self.persepolis_setting.value('settings/download_path'))


        self.connections_spinBox.setValue(connections)
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


# download UserName initialization
        settings_download_user = self.persepolis_setting.value(
            'add_link_initialization/download_user', None)
        if settings_download_user:
            self.download_user_lineEdit.setText(str(settings_download_user))


# connect folder_pushButton
        self.folder_pushButton.clicked.connect(self.changeFolder)

# connect OK and canel button

        self.cancel_pushButton.clicked.connect(self.close)
        self.ok_pushButton.clicked.connect(self.okButtonPressed)

# connect select_all_pushButton  deselect_all_pushButton
        self.select_all_pushButton.clicked.connect(self.selectAll)

        self.deselect_all_pushButton.clicked.connect(self.deselectAll)


#frames and checkBoxes
        self.proxy_frame.setEnabled(False)
        self.proxy_checkBox.toggled.connect(self.proxyFrame)

        self.download_frame.setEnabled(False)
        self.download_checkBox.toggled.connect(self.downloadFrame)

        self.limit_frame.setEnabled(False)
        self.limit_checkBox.toggled.connect(self.limitFrame)

        # set focus to ok button
        self.ok_pushButton.setFocus()

# add_queue_comboBox event
        self.add_queue_comboBox.currentIndexChanged.connect(self.queueChanged)

# setting window size and position
        size = self.persepolis_setting.value('TextQueue/size', QSize(700, 500))
        position = self.persepolis_setting.value(
            'TextQueue/position', QPoint(300, 300))
        self.resize(size)
        self.move(position)

# this method checkes all check boxes
    def selectAll(self, button):
        for i in range(self.links_table.rowCount()):
            item = self.links_table.item(i, 0)
            item.setCheckState(QtCore.Qt.Checked)

# this method deselect all check boxes
    def deselectAll(self, button):
        for i in range(self.links_table.rowCount()):
            item = self.links_table.item(i, 0)
            item.setCheckState(QtCore.Qt.Unchecked)

# this method is called, when user changes add_queue_comboBox
    def queueChanged(self, combo):
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

    def limitFrame(self, checkBox):

        if self.limit_checkBox.isChecked():
            self.limit_frame.setEnabled(True)
        else:
            self.limit_frame.setEnabled(False)

    def changeFolder(self, button):
        fname = QFileDialog.getExistingDirectory(
            self, 'Select a directory', download_path)

        if fname:
            # Returns pathName with the '/' separators converted to separators that are appropriate for the underlying operating system.
            # On Windows, toNativeSeparators("c:/winnt/system32") returns
            # "c:\winnt\system32".
            fname = QDir.toNativeSeparators(fname)

        if os.path.isdir(fname):
            self.download_folder_lineEdit.setText(fname)

    def okButtonPressed(self, button):
        # write user's input data to init file
        self.persepolis_setting.setValue(
            'add_link_initialization/ip', self.ip_lineEdit.text())
        self.persepolis_setting.setValue(
            'add_link_initialization/port', self.port_spinBox.value())
        self.persepolis_setting.setValue(
            'add_link_initialization/proxy_user', self.proxy_user_lineEdit.text())
        self.persepolis_setting.setValue(
            'add_link_initialization/download_user', self.download_user_lineEdit.text())

        if not(self.proxy_checkBox.isChecked()):
            ip = None
            port = None
            proxy_user = None
            proxy_passwd = None
        else:
            ip = self.ip_lineEdit.text()
            if not(ip):
                ip = None
            port = self.port_spinBox.value()
            if not(port):
                port = None
            proxy_user = self.proxy_user_lineEdit.text()
            if not(proxy_user):
                proxy_user = None
            proxy_passwd = self.proxy_pass_lineEdit.text()
            if not(proxy_passwd):
                proxy_passwd = None

        if not(self.download_checkBox.isChecked()):
            download_user = None
            download_passwd = None
        else:
            download_user = self.download_user_lineEdit.text()
            if not(download_user):
                download_user = None
            download_passwd = self.download_pass_lineEdit.text()
            if not(download_passwd):
                download_passwd = None

        if not(self.limit_checkBox.isChecked()):
            limit = 0
        else:
            if self.limit_comboBox.currentText() == "KiB/s":
                limit = str(self.limit_spinBox.value()) + str("K")
            else:
                limit = str(self.limit_spinBox.value()) + str("M")

        category = str(self.add_queue_comboBox.currentText())

        connections = self.connections_spinBox.value()
        download_path = self.download_folder_lineEdit.text()

        dict = {'out': None,
                'start_time': None,
                'end_time': None,
                'link': None,
                'ip': ip,
                'port': port,
                'proxy_user': proxy_user,
                'proxy_passwd': proxy_passwd,
                'download_user': download_user,
                'download_passwd': download_passwd,
                'connections': connections,
                'limit_value': limit,
                'download_path' : download_path,
                'referer': None,
                'load_cookies': None,
                'user_agent': None,
                'header': None,
                'after_download': None
                }



# find checked links in links_table
        self.add_link_dictionary_list = []
        i = 0
        for row in range(self.links_table.rowCount()):
            item = self.links_table.item(row, 0)

            # if item is checked
            if (item.checkState() == 2):
                # Create a copy from dict and add it to add_link_dictionary_list
                self.add_link_dictionary_list.append(
                    dict.copy())

                # get link and add it to dict
                link = self.links_table.item(row, 1).text()
                self.add_link_dictionary_list[i]['link'] = str(link)

                # add file name to the dict
                self.add_link_dictionary_list[i]['out'] = self.links_table.item(
                    row, 0).text()

                i = i + 1
        # reverse list
        self.add_link_dictionary_list.reverse()

        # Create callback for mainwindow
        self.callback(self.add_link_dictionary_list, category)

        # close window
        self.close()

    def closeEvent(self, event):
        self.persepolis_setting.setValue('TextQueue/size', self.size())
        self.persepolis_setting.setValue('TextQueue/position', self.pos())
        self.persepolis_setting.sync()

        event.accept()
