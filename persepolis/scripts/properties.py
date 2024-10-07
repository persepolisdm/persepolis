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

try:
    from PySide6.QtCore import Qt, QSize, QPoint, QDir, QTime, QCoreApplication
    from PySide6.QtWidgets import QLabel, QLineEdit, QFileDialog
    from PySide6.QtGui import QIcon
except:
    from PyQt5.QtCore import Qt, QSize, QPoint, QDir, QTime, QCoreApplication
    from PyQt5.QtWidgets import QLabel, QLineEdit, QFileDialog
    from PyQt5.QtGui import QIcon

from persepolis.gui.addlink_ui import AddLinkWindow_Ui
from persepolis.scripts.check_proxy import getProxy
import os


class PropertiesWindow(AddLinkWindow_Ui):
    def __init__(self, parent, callback, gid, persepolis_setting, video_finder_dictionary=None):
        super().__init__(persepolis_setting)

        self.parent = parent
        self.persepolis_setting = persepolis_setting
        self.video_finder_dictionary = video_finder_dictionary

        self.download_later_pushButton.hide()  # hide download_later_pushButton
        self.change_name_checkBox.hide()  # hide change_name_checkBox
        self.change_name_lineEdit.hide()  # hide change_name_lineEdit

        # add new QLineEdit and QLineEdit for audio link if we have video finder links
        if self.video_finder_dictionary:

            self.link_label_2 = QLabel(self.link_frame)
            self.link_horizontalLayout.addWidget(self.link_label_2)

            self.link_lineEdit_2 = QLineEdit(self.link_frame)
            self.link_horizontalLayout.addWidget(self.link_lineEdit_2)
            self.link_lineEdit_2.textChanged.connect(self.linkLineChanged)

            self.link_label.setText(QCoreApplication.translate("addlink_ui_tr", "Video Link: "))
            self.link_label_2.setText(QCoreApplication.translate("addlink_ui_tr", "Audio Link: "))

            # gid_1 >> video_gid , gid_2 >> audio_gid
            self.gid_1 = self.video_finder_dictionary['video_gid']
            self.gid_2 = self.video_finder_dictionary['audio_gid']

        else:

            self.gid_1 = gid

        self.callback = callback

        # detect_proxy_pushButton
        self.detect_proxy_pushButton.clicked.connect(
            self.detectProxy)

        # connect folder_pushButton
        self.folder_pushButton.clicked.connect(self.changeFolder)
        self.download_folder_lineEdit.setEnabled(False)

        self.ok_pushButton.setEnabled(False)
        self.link_lineEdit.textChanged.connect(self.linkLineChanged)

        # connect OK and cancel button
        self.cancel_pushButton.clicked.connect(self.close)
        self.ok_pushButton.clicked.connect(self.okButtonPressed)

        # frames and checkBoxes
        self.proxy_frame.setEnabled(False)
        self.proxy_checkBox.toggled.connect(self.proxyFrame)

        self.download_frame.setEnabled(False)
        self.download_checkBox.toggled.connect(self.downloadFrame)

        self.start_frame.setEnabled(False)
        self.start_checkBox.toggled.connect(self.startFrame)

        self.end_frame.setEnabled(False)
        self.end_checkBox.toggled.connect(self.endFrame)

        # get information from data base
        self.add_link_dictionary_1 = self.parent.persepolis_db.searchGidInAddLinkTable(self.gid_1)
        self.download_table_dict_1 = self.parent.persepolis_db.searchGidInDownloadTable(self.gid_1)

        if video_finder_dictionary:
            self.add_link_dictionary_2 = self.parent.persepolis_db.searchGidInAddLinkTable(self.gid_2)
            self.download_table_dict_2 = self.parent.persepolis_db.searchGidInDownloadTable(self.gid_2)

        # create a copy from add_link_dictionary for checking changes finally!
        self.add_link_dictionary_1_backup = {}
        for key in self.add_link_dictionary_1.keys():
            self.add_link_dictionary_1_backup[key] = self.add_link_dictionary_1[key]

        if video_finder_dictionary:
            self.add_link_dictionary_2_backup = {}
            for key in self.add_link_dictionary_2.keys():
                self.add_link_dictionary_2_backup[key] = self.add_link_dictionary_2[key]

        # initialization
        # disable folder_frame when download is complete
        if self.video_finder_dictionary:
            if self.video_finder_dictionary['video_completed'] == 'yes' or self.video_finder_dictionary['audio_completed'] == 'yes':
                self.folder_frame.setEnabled(False)
        else:
            if self.download_table_dict_1['status'] == 'complete':
                self.folder_frame.setEnabled(False)

        # link
        self.link_lineEdit.setText(self.add_link_dictionary_1['link'])

        if self.video_finder_dictionary:
            self.link_lineEdit_2.setText(self.add_link_dictionary_2['link'])

        # ip_lineEdit initialization
        if self.add_link_dictionary_1['ip']:
            self.proxy_checkBox.setChecked(True)
            self.ip_lineEdit.setText(self.add_link_dictionary_1['ip'])
            # port_spinBox initialization
            try:
                self.port_spinBox.setValue(
                    int(self.add_link_dictionary_1['port']))
            except:
                pass
            # proxy user lineEdit initialization
            try:
                self.proxy_user_lineEdit.setText(
                    self.add_link_dictionary_1['proxy_user'])
            except:
                pass
            # proxy pass lineEdit initialization
            try:
                self.proxy_pass_lineEdit.setText(
                    self.add_link_dictionary_1['proxy_passwd'])
            except:
                pass

        # proxy type
        proxy_type = self.add_link_dictionary_1['proxy_type']

        # default is http
        if proxy_type == 'socks5':

            self.socks5_radioButton.setChecked(True)

        elif proxy_type == 'https':
            self.https_radioButton.setChecked(True)

        else:
            self.http_radioButton.setChecked(True)

        # download UserName initialization
        if self.add_link_dictionary_1['download_user']:
            self.download_checkBox.setChecked(True)
            self.download_user_lineEdit.setText(
                self.add_link_dictionary_1['download_user'])
            # download PassWord initialization
            try:
                self.download_pass_lineEdit.setText(
                    self.add_link_dictionary_1['download_passwd'])
            except:
                pass

        # folder_path
        try:
            self.download_folder_lineEdit.setText(
                self.add_link_dictionary_1['download_path'])
        except:
            pass

        # connections
        try:
            self.connections_spinBox.setValue(
                int(self.add_link_dictionary_1['connections']))
        except:
            pass

        # get categories name and add them to add_queue_comboBox
        categories_list = self.parent.persepolis_db.categoriesList()
        for queue in categories_list:
            if queue != 'All Downloads':
                self.add_queue_comboBox.addItem(queue)

        # finding current queue and setting it!
        self.current_category = self.download_table_dict_1['category']

        current_category_index = self.add_queue_comboBox.findText(
            self.current_category)
        self.add_queue_comboBox.setCurrentIndex(current_category_index)

        # add_queue_comboBox event
        self.add_queue_comboBox.currentIndexChanged.connect(self.queueChanged)

        # start_time
        if self.add_link_dictionary_1['start_time']:
            # get hour and minute
            hour, minute = self.add_link_dictionary_1['start_time'].split(':')

            # set time
            q_time = QTime(int(hour), int(minute))
            self.start_time_qDataTimeEdit.setTime(q_time)

            self.start_checkBox.setChecked(True)
        # end_time
        if self.add_link_dictionary_1['end_time']:
            # get hour and minute
            hour, minute = self.add_link_dictionary_1['end_time'].split(':')

            # set time
            q_time = QTime(int(hour), int(minute))
            self.end_time_qDateTimeEdit.setTime(q_time)

            self.end_checkBox.setChecked(True)

        # referer
        if self.add_link_dictionary_1['referer']:
            self.referer_lineEdit.setText(str(self.add_link_dictionary_1['referer']))

        if self.add_link_dictionary_1['header']:
            self.header_lineEdit.setText(str(self.add_link_dictionary_1['header']))

        if self.add_link_dictionary_1['user_agent']:
            self.user_agent_lineEdit.setText(str(self.add_link_dictionary_1['user_agent']))

        if self.add_link_dictionary_1['load_cookies']:
            self.load_cookies_lineEdit.setText((self.add_link_dictionary_1['load_cookies']))

        # set window size and position
        size = self.persepolis_setting.value(
            'PropertiesWindow/size', QSize(520, 425))
        position = self.persepolis_setting.value(
            'PropertiesWindow/position', QPoint(300, 300))
        self.resize(size)
        self.move(position)

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

    def startFrame(self, checkBox):

        if self.start_checkBox.isChecked():
            self.start_frame.setEnabled(True)
        else:
            self.start_frame.setEnabled(False)

    def endFrame(self, checkBox):

        if self.end_checkBox.isChecked():
            self.end_frame.setEnabled(True)
        else:
            self.end_frame.setEnabled(False)

    def changeFolder(self, button):
        fname = QFileDialog.getExistingDirectory(self, 'Open f', '/home')

        if fname:
            # Returns pathName with the '/' separators converted to separators that are appropriate for the underlying operating system.
            # On Windows, toNativeSeparators("c:/winnt/system32") returns
            # "c:\winnt\system32".
            fname = QDir.toNativeSeparators(fname)

        if os.path.isdir(fname):
            self.download_folder_lineEdit.setText(fname)

    def linkLineChanged(self, lineEdit):
        if str(self.link_lineEdit.text()) == '':
            self.ok_pushButton.setEnabled(False)
        else:
            self.ok_pushButton.setEnabled(True)

    def queueChanged(self, combo):
        # if one of the queues selected by user , start time and end time must
        # be deactivated
        if self.add_queue_comboBox.currentIndex() != 0:
            self.start_checkBox.setCheckState(Qt.Unchecked)
            self.start_checkBox.setEnabled(False)

            self.end_checkBox.setCheckState(Qt.Unchecked)
            self.end_checkBox.setEnabled(False)
        else:
            self.start_checkBox.setEnabled(True)
            self.end_checkBox.setEnabled(True)

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
        # referer
        if self.referer_lineEdit.text() != '':
            referer = self.referer_lineEdit.text()
        else:
            referer = None

        # header
        if self.header_lineEdit.text() != '':
            header = self.header_lineEdit.text()
        else:
            header = None

        # user_agent
        if self.user_agent_lineEdit.text() != '':
            user_agent = self.user_agent_lineEdit.text()
        else:
            user_agent = None

        # load_cookies
        if self.load_cookies_lineEdit.text() != '':
            load_cookies = self.load_cookies_lineEdit.text()
        else:
            load_cookies = None

        return referer, header, user_agent, load_cookies

    def okButtonPressed(self, button):
        # write user's new inputs in persepolis_setting for next time if needed
        if self.folder_checkBox.isChecked() is True:
            self.persepolis_setting.setValue(
                'settings/download_path', self.download_folder_lineEdit.text())

        # get proxy information
        ip, port, proxy_user, proxy_passwd, proxy_type = self.getProxyInformation()
        if proxy_type is not None:
            self.persepolis_setting.setValue('add_link_initialization/proxy_type', proxy_type)

        # get download username and password information
        download_user, download_passwd = self.getUserPass()

        if not (self.start_checkBox.isChecked()):
            start_time = None
        else:
            start_time = self.start_time_qDataTimeEdit.text()

        if not (self.end_checkBox.isChecked()):
            end_time = None
        else:
            end_time = self.end_time_qDateTimeEdit.text()

        connections = self.connections_spinBox.value()
        download_path = self.download_folder_lineEdit.text()

        # get additinal information
        referer, header, user_agent, load_cookies = self.getAdditionalInformation()

        self.add_link_dictionary_1['start_time'] = start_time
        self.add_link_dictionary_1['end_time'] = end_time
        self.add_link_dictionary_1['link'] = self.link_lineEdit.text()
        self.add_link_dictionary_1['ip'] = ip
        self.add_link_dictionary_1['port'] = port
        self.add_link_dictionary_1['proxy_user'] = proxy_user
        self.add_link_dictionary_1['proxy_passwd'] = proxy_passwd
        self.add_link_dictionary_1['proxy_type'] = proxy_type
        self.add_link_dictionary_1['download_user'] = download_user
        self.add_link_dictionary_1['download_passwd'] = download_passwd
        self.add_link_dictionary_1['download_path'] = download_path
        self.add_link_dictionary_1['connections'] = connections
        self.add_link_dictionary_1['referer'] = referer
        self.add_link_dictionary_1['header'] = header
        self.add_link_dictionary_1['user_agent'] = user_agent
        self.add_link_dictionary_1['load_cookies'] = load_cookies

        if self.video_finder_dictionary:
            self.add_link_dictionary_2['start_time'] = start_time
            self.add_link_dictionary_2['end_time'] = end_time
            self.add_link_dictionary_2['link'] = self.link_lineEdit_2.text()
            self.add_link_dictionary_2['ip'] = ip
            self.add_link_dictionary_2['port'] = port
            self.add_link_dictionary_2['proxy_user'] = proxy_user
            self.add_link_dictionary_2['proxy_passwd'] = proxy_passwd
            self.add_link_dictionary_2['proxy_type'] = proxy_type
            self.add_link_dictionary_2['download_user'] = download_user
            self.add_link_dictionary_2['download_passwd'] = download_passwd
            self.add_link_dictionary_2['download_path'] = download_path
            self.add_link_dictionary_2['connections'] = connections
            self.add_link_dictionary_2['referer'] = referer
            self.add_link_dictionary_2['header'] = header
            self.add_link_dictionary_2['user_agent'] = user_agent
            self.add_link_dictionary_2['load_cookies'] = load_cookies

        new_category = str(self.add_queue_comboBox.currentText())

        # it means category changed and data base must be updated.
        if new_category != self.current_category:

            self.download_table_dict_1['category'] = new_category
            # update data base
            self.parent.persepolis_db.updateDownloadTable([self.download_table_dict_1])

            # update category_db_table
            # remove download item from old category
            old_category_dict = self.parent.persepolis_db.searchCategoryInCategoryTable(self.current_category)
            old_category_gid_list = old_category_dict['gid_list']
            old_category_gid_list.remove(self.gid_1)
            self.parent.persepolis_db.updateCategoryTable([old_category_dict])

            # add download item to new category
            new_category_dict = self.parent.persepolis_db.searchCategoryInCategoryTable(new_category)
            new_category_gid_list = new_category_dict['gid_list']
            new_category_gid_list.append(self.gid_1)
            self.parent.persepolis_db.updateCategoryTable([new_category_dict])

            if self.video_finder_dictionary:

                # category for audio and video must be same as each other
                self.download_table_dict_2['category'] = new_category
                self.parent.persepolis_db.updateDownloadTable([self.download_table_dict_2])

                # update category_db_table
                # remove download item from old category
                old_category_dict = self.parent.persepolis_db.searchCategoryInCategoryTable(self.current_category)
                old_category_gid_list = old_category_dict['gid_list']
                old_category_gid_list.remove(self.gid_2)
                self.parent.persepolis_db.updateCategoryTable([old_category_dict])

                # add download item to new category
                new_category_dict = self.parent.persepolis_db.searchCategoryInCategoryTable(new_category)
                new_category_gid_list = new_category_dict['gid_list']
                new_category_gid_list.append(self.gid_2)
                self.parent.persepolis_db.updateCategoryTable([new_category_dict])


        # if any thing in add_link_dictionary_1 is changed,then update data base!
        for key in self.add_link_dictionary_1.keys():
            if self.add_link_dictionary_1[key] != self.add_link_dictionary_1_backup[key]:

                # update data base
                self.parent.persepolis_db.updateAddLinkTable([self.add_link_dictionary_1])

                # break the loop
                break

        # if link changed, then update download_db_table in data base
        if self.add_link_dictionary_1['link'] != self.add_link_dictionary_1_backup['link']:

            dictionary = {'gid': self.gid_1, 'link': self.add_link_dictionary_1['link']}
            self.parent.persepolis_db.updateDownloadTable([dictionary])

        # if any thing in add_link_dictionary_2 is changed,then update data base!
        if self.video_finder_dictionary:
            for key in self.add_link_dictionary_2.keys():
                if self.add_link_dictionary_2[key] != self.add_link_dictionary_2_backup[key]:

                    # update data base
                    self.parent.persepolis_db.updateAddLinkTable([self.add_link_dictionary_2])

                    # break the loop
                    break

            # if link changed, then update download_db_table in data base
            if self.add_link_dictionary_2['link'] != self.add_link_dictionary_2_backup['link']:

                dictionary = {'gid': self.gid_2, 'link': self.add_link_dictionary_2['link']}
                self.parent.persepolis_db.updateDownloadTable([dictionary])

            # if download_path was changed, then update video_finder_db_table in data base
            if self.add_link_dictionary_1['download_path'] != self.add_link_dictionary_1_backup['download_path']:
                dictionary = {'video_gid': self.gid_1,
                              'download_path': download_path}
                self.parent.persepolis_db.updateVideoFinderTable[dictionary]

        # callback to mainwindow
        self.callback(self.add_link_dictionary_1, self.gid_1, new_category, self.video_finder_dictionary)

        # close window
        self.close()

    # close window with ESC key
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def closeEvent(self, event):
        # save window size and position
        self.persepolis_setting.setValue('PropertiesWindow/size', self.size())
        self.persepolis_setting.setValue(
            'PropertiesWindow/position', self.pos())
        self.persepolis_setting.sync()

        event.accept()

    def changeIcon(self, icons):
        icons = ':/' + str(icons) + '/'

        self.folder_pushButton.setIcon(QIcon(icons + 'folder'))
        self.download_later_pushButton.setIcon(QIcon(icons + 'stop'))
        self.cancel_pushButton.setIcon(QIcon(icons + 'remove'))
        self.ok_pushButton.setIcon(QIcon(icons + 'ok'))
