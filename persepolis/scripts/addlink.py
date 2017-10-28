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

import os
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QHBoxLayout,  QApplication,  QFileDialog,  QCheckBox, QLineEdit, QPushButton
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QPoint, QSize, QDir, QThread, pyqtSignal
from persepolis.gui.addlink_ui import AddLinkWindow_Ui
from functools import partial
from persepolis.scripts import spider
from persepolis.scripts import logger
from persepolis.scripts.check_proxy import getProxy


class AddLinkSpiderThread(QThread):
    ADDLINKSPIDERSIGNAL = pyqtSignal(str)

    def __init__(self, add_link_dictionary):
        QThread.__init__(self)
        self.add_link_dictionary = add_link_dictionary

    def run(self):
        try :
            filesize = spider.addLinkSpider(self.add_link_dictionary)
            if filesize:
                self.ADDLINKSPIDERSIGNAL.emit(filesize)
            else:
                print("Spider couldn't find download information")
                logger.sendToLog(
                    "Spider couldn't find download information", "ERROR")
        except Exception as e:
            print(str(e))
            print("Spider couldn't find download information")
            logger.sendToLog(
                "Spider couldn't find download information", "ERROR")



class AddLinkWindow(AddLinkWindow_Ui):
    def __init__(self, parent, callback, persepolis_setting, plugin_add_link_dictionary={}):
        super().__init__(persepolis_setting)
        self.callback = callback
        self.plugin_add_link_dictionary = plugin_add_link_dictionary
        self.persepolis_setting = persepolis_setting
        self.parent = parent

        # entry initialization 
        # read values from persepolis_setting
        # connections
        connections = int(
            self.persepolis_setting.value('settings/connections'))

        self.connections_spinBox.setValue(connections)

        # download_path
        download_path = str(
            self.persepolis_setting.value('settings/download_path'))

        self.download_folder_lineEdit.setText(download_path)
        self.download_folder_lineEdit.setEnabled(False)

        # enable ok button only if link_lineEdit is not empty!
        # see linkLineChanged method.
        self.ok_pushButton.setEnabled(False)
        self.download_later_pushButton.setEnabled(False)
        self.link_lineEdit.textChanged.connect(self.linkLineChanged)

        self.options_pushButton.clicked.connect(self.optionsButtonClicked)

        # if browsers plugin didn't send any links
        # then check clipboard for link!
        if ('link' in self.plugin_add_link_dictionary):
            # check plugin_add_link_dictionary for link!
            # "link" key-value must be checked
            self.link_lineEdit.setText(
                str(self.plugin_add_link_dictionary['link']))
 
        else:
            # check clipboard
            clipboard = QApplication.clipboard()
            text = clipboard.text()
            if (("tp:/" in text[2:6]) or ("tps:/" in text[2:7])):
                self.link_lineEdit.setText(str(text))

        # detect_proxy_pushButton 
        self.detect_proxy_pushButton.clicked.connect(
                self.detectProxy)

        # ip_lineEdit initialization ->
        settings_ip = self.persepolis_setting.value(
            'add_link_initialization/ip', None)
        if (settings_ip):
            self.ip_lineEdit.setText(str(settings_ip))

        # proxy user lineEdit initialization ->
        settings_proxy_user = self.persepolis_setting.value(
            'add_link_initialization/proxy_user', None)
        if (settings_proxy_user):
            self.proxy_user_lineEdit.setText(str(settings_proxy_user))

        # port_spinBox initialization ->
        settings_port = self.persepolis_setting.value(
            'add_link_initialization/port', 0)

        self.port_spinBox.setValue(int(int(settings_port)))

        # download UserName initialization ->
        settings_download_user = self.persepolis_setting.value(
            'add_link_initialization/download_user', None)
        if (settings_download_user):
            self.download_user_lineEdit.setText(str(settings_download_user))

# get categories name and add them to add_queue_comboBox
        categories_list = self.parent.persepolis_db.categoriesList()
        for queue in categories_list:
            self.add_queue_comboBox.addItem(queue)

        self.add_queue_comboBox.setCurrentIndex(0)

        # add_queue_comboBox event
        self.add_queue_comboBox.currentIndexChanged.connect(self.queueChanged)

        # connect folder_pushButton
        self.folder_pushButton.clicked.connect(self.changeFolder)

        # connect OK and canel download_later button ->
        self.cancel_pushButton.clicked.connect(self.close)
        self.ok_pushButton.clicked.connect(partial(
            self.okButtonPressed, download_later=False))
        self.download_later_pushButton.clicked.connect(
            partial(self.okButtonPressed, download_later=True))

        # frames and checkBoxes ->
        self.proxy_frame.setEnabled(False)
        self.proxy_checkBox.toggled.connect(self.proxyFrame)

        self.download_frame.setEnabled(False)
        self.download_checkBox.toggled.connect(self.downloadFrame)

        self.limit_frame.setEnabled(False)
        self.limit_checkBox.toggled.connect(self.limitFrame)

        self.start_frame.setEnabled(False)
        self.start_checkBox.toggled.connect(self.startFrame)

        self.end_frame.setEnabled(False)
        self.end_checkBox.toggled.connect(self.endFrame)

        self.change_name_lineEdit.setEnabled(False)
        self.change_name_checkBox.toggled.connect(self.changeName)

        # set focus to ok button
        self.ok_pushButton.setFocus()

        # check plugin_add_link_dictionary for finding file name
        # perhaps plugin sended file name in plugin_add_link_dictionary
        # for finding file name "out" key must be checked
        if ('out' in self.plugin_add_link_dictionary):
            if self.plugin_add_link_dictionary['out']:
                self.change_name_lineEdit.setText(
                    str(self.plugin_add_link_dictionary['out']))
                self.change_name_checkBox.setChecked(True)

# set window size and position
        size = self.persepolis_setting.value(
            'AddLinkWindow/size', QSize(520, 265))
        position = self.persepolis_setting.value(
            'AddLinkWindow/position', QPoint(300, 300))
        self.resize(size)
        self.move(position)

        self.minimum_height = self.height()


# more options widgets list
        self.more_options_widgets = [self.proxy_checkBox, self.detect_proxy_pushButton, self.proxy_frame, self.download_checkBox,
                                    self.download_frame, self.folder_frame, self.start_checkBox,self.start_frame, self.end_checkBox,
                                    self.end_frame, self.limit_checkBox, self.limit_frame, self.connections_frame] 
        # hide more_options_widgets
        for widgets in self.more_options_widgets:
            widgets.hide()



# hide and show more options

    def resizeEvent(self, event):
        height = int(self.height())
        if height < self.minimum_height:
            self.minimum_height = height

# detect system proxy setting, and set ip_lineEdit and port_spinBox
    def detectProxy(self, button):
        # get system proxy information
        system_proxy_dict = getProxy()

        enable_proxy_frame = False

        # ip
        if 'http_proxy_ip' in system_proxy_dict.keys():
            self.ip_lineEdit.setText(str(system_proxy_dict['http_proxy_ip']))
            enable_proxy_frame = True

        # port
        if 'http_proxy_port' in system_proxy_dict.keys():
            self.port_spinBox.setValue(int(system_proxy_dict['http_proxy_port']))
            enable_proxy_frame = True

        # enable proxy frame if http_proxy_ip or http_proxy_port is valid.
        if enable_proxy_frame:
            self.proxy_checkBox.setChecked(True)
            self.detect_proxy_label.setText('')
        else:
            self.proxy_checkBox.setChecked(False)
            self.detect_proxy_label.setText('No proxy detected!')



# Show more options 
    def optionsButtonClicked(self, button):

        if self.options_pushButton.text() == 'Show more options' or self.options_pushButton.text() == '&Show more options':
            self.options_pushButton.setText('Hide options')
            
            #unhide more_options_widgets
            for widgets in self.more_options_widgets:
                widgets.show()

            self.layout().setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        else:
            self.options_pushButton.setText('Show more options')

            #hide more_options_widgets
            for widgets in self.more_options_widgets:
                widgets.hide()

            self.layout().setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
            self.setMinimumSize(QSize(self.width() , self.minimum_height))
            self.resize(QSize(self.width() , self.minimum_height))
            
            


# active frames if checkBoxes are checked
    def proxyFrame(self, checkBox):

        if self.proxy_checkBox.isChecked() == True:
            self.proxy_frame.setEnabled(True)
        else:
            self.proxy_frame.setEnabled(False)

    def downloadFrame(self, checkBox):

        if self.download_checkBox.isChecked() == True:
            self.download_frame.setEnabled(True)
        else:
            self.download_frame.setEnabled(False)

    def limitFrame(self, checkBox):

        if self.limit_checkBox.isChecked() == True:
            self.limit_frame.setEnabled(True)
        else:
            self.limit_frame.setEnabled(False)

    def startFrame(self, checkBox):

        if self.start_checkBox.isChecked() == True:
            self.start_frame.setEnabled(True)
        else:
            self.start_frame.setEnabled(False)

    def endFrame(self, checkBox):

        if self.end_checkBox.isChecked() == True:
            self.end_frame.setEnabled(True)
        else:
            self.end_frame.setEnabled(False)

    def changeFolder(self, button):
        # get download_path from lineEdit
        download_path = self.download_folder_lineEdit.text()

        # open select folder dialog
        fname = QFileDialog.getExistingDirectory(
            self, 'Select a directory', download_path)

        if fname:
            # Returns pathName with the '/' separators converted to separators that are appropriate for the underlying operating system.
            # On Windows, toNativeSeparators("c:/winnt/system32") returns
            # "c:\winnt\system32".
            fname = QDir.toNativeSeparators(fname)

        if os.path.isdir(fname):
            self.download_folder_lineEdit.setText(fname)

# enable when link_lineEdit is not empty and find size of file.
    def linkLineChanged(self, lineEdit):
        if str(self.link_lineEdit.text()) == '':
            self.ok_pushButton.setEnabled(False)
            self.download_later_pushButton.setEnabled(False)
        else: # find file size

            self.plugin_add_link_dictionary['link'] = str(self.link_lineEdit.text())

            # spider is finding file size
            new_spider = AddLinkSpiderThread(self.plugin_add_link_dictionary)
            self.parent.threadPool.append(new_spider)
            self.parent.threadPool[len(self.parent.threadPool) - 1].start()
            self.parent.threadPool[len(self.parent.threadPool) - 1].ADDLINKSPIDERSIGNAL.connect(
                partial(self.parent.addLinkSpiderCallBack, child=self))
 
            self.ok_pushButton.setEnabled(True)
            self.download_later_pushButton.setEnabled(True)

# enable change_name_lineEdit if change_name_checkBox is checked. 
    def changeName(self, checkBoxes):
        if self.change_name_checkBox.isChecked() == True:
            self.change_name_lineEdit.setEnabled(True)
        else:
            self.change_name_lineEdit.setEnabled(False)

    def queueChanged(self, combo):
        # if one of the queues selected by user , start time and end time must
        # be deactivated
        if self.add_queue_comboBox.currentIndex() != 0:
            self.start_checkBox.setCheckState(QtCore.Qt.Unchecked)
            self.start_checkBox.setEnabled(False)

            self.end_checkBox.setCheckState(QtCore.Qt.Unchecked)
            self.end_checkBox.setEnabled(False)

        else:
            self.start_checkBox.setEnabled(True)
            self.end_checkBox.setEnabled(True)

    def okButtonPressed(self, button, download_later):
    # user commited information by pressing ok_pushButton, so get information
    # from AddLinkWindow and return them to the mainwindow with callback!

        # write user's new inputs in persepolis_setting for next time :)
        self.persepolis_setting.setValue(
            'add_link_initialization/ip', self.ip_lineEdit.text())
        self.persepolis_setting.setValue(
            'add_link_initialization/port', self.port_spinBox.value())
        self.persepolis_setting.setValue(
            'add_link_initialization/proxy_user', self.proxy_user_lineEdit.text())
        self.persepolis_setting.setValue(
            'add_link_initialization/download_user', self.download_user_lineEdit.text())

        # get proxy information
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

        # get download username and password information
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

        # check that if user limits download speed.
        if not(self.limit_checkBox.isChecked()):
            limit = 0
        else:
            if self.limit_comboBox.currentText() == "KB/S":
                limit = str(self.limit_spinBox.value()) + str("K")
            else:
                limit = str(self.limit_spinBox.value()) + str("M")

        # get start time for download if user set that.
        if not(self.start_checkBox.isChecked()):
            start_time = None
        else:
            start_time = self.start_time_qDataTimeEdit.text()

        # get end time for download if user set that.
        if not(self.end_checkBox.isChecked()):
            end_time = None
        else:
            end_time = self.end_time_qDateTimeEdit.text()

        # check that if user set new name for download file.
        if not(self.change_name_checkBox.isChecked()):
            out = None
        else:
            out = str(self.change_name_lineEdit.text())

        # get download link
        link = self.link_lineEdit.text()

        # get number of connections
        connections = self.connections_spinBox.value()

        # get download_path
        download_path = self.download_folder_lineEdit.text()

        # get referer and header and user-agent and load-cookies in plugin_add_link_dictionary if exits.
        if not('referer' in self.plugin_add_link_dictionary):
            self.plugin_add_link_dictionary['referer'] = None

        if not('header' in self.plugin_add_link_dictionary):
            self.plugin_add_link_dictionary['header'] = None

        if not('user-agent' in self.plugin_add_link_dictionary):
            self.plugin_add_link_dictionary['user-agent'] = None

        if not('load-cookies' in self.plugin_add_link_dictionary):
            self.plugin_add_link_dictionary['load-cookies'] = None

        # save information in a dictionary(add_link_dictionary).
        self.add_link_dictionary = {'out': out, 'start_time': start_time, 'end_time': end_time, 'link': link, 'ip': ip,
                                    'port': port, 'proxy_user': proxy_user, 'proxy_passwd': proxy_passwd, 
                                    'download_user': download_user, 'download_passwd': download_passwd,
                                    'connections': connections, 'limit_value': limit, 'download_path': download_path}

        # add plugin_add_link_dictionary information to add_link_dictionary.
        for i in self.plugin_add_link_dictionary.keys():
            self.add_link_dictionary[i] = self.plugin_add_link_dictionary[i]

        # get category of download
        category = str(self.add_queue_comboBox.currentText())

        del self.plugin_add_link_dictionary

        # return information to mainwindow
        self.callback(self.add_link_dictionary, download_later, category)
        
        # close window
        self.close()


# save size and position of window, when user closes the window.
    def closeEvent(self, event):
        self.layout().setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.setMinimumSize(QSize(self.width() , self.minimum_height))
        self.resize(QSize(self.width() , self.minimum_height))
 
        self.persepolis_setting.setValue('AddLinkWindow/size', self.size())
        self.persepolis_setting.setValue('AddLinkWindow/position', self.pos())
        self.persepolis_setting.sync()
        self.destroy()
