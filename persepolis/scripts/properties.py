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

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QSize, QPoint, QDir, QTime
import os
from persepolis.gui.addlink_ui import AddLinkWindow_Ui
from persepolis.scripts.check_proxy import getProxy


class PropertiesWindow(AddLinkWindow_Ui):
    def __init__(self, callback, gid, persepolis_setting, parent):
        super().__init__(persepolis_setting)

        self.parent = parent
        self.persepolis_setting = persepolis_setting
        self.download_later_pushButton.hide()  # hide download_later_pushButton
        self.change_name_checkBox.hide()  # hide change_name_checkBox
        self.change_name_lineEdit.hide()  # hide change_name_lineEdit

        self.callback = callback
        self.gid = gid

# detect_proxy_pushButton
        self.detect_proxy_pushButton.clicked.connect(
                self.detectProxy)

# connect folder_pushButton
        self.folder_pushButton.clicked.connect(self.changeFolder)
        self.download_folder_lineEdit.setEnabled(False)

        self.ok_pushButton.setEnabled(False)
        self.link_lineEdit.textChanged.connect(self.linkLineChanged)

# connect OK and canel button

        self.cancel_pushButton.clicked.connect(self.close)
        self.ok_pushButton.clicked.connect(self.okButtonPressed)
#frames and checkBoxes
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


        # get information from data base
        self.add_link_dictionary = self.parent.persepolis_db.searchGidInAddLinkTable(self.gid)

        self.download_table_dict = self.parent.persepolis_db.searchGidInDownloadTable(gid)

        # create a copy from add_link_dictionary for checking changes finally!
        self.add_link_dictionary_backup = {}
        for key in self.add_link_dictionary.keys():
            self.add_link_dictionary_backup[key] = self.add_link_dictionary[key]

# initialization
# disable folder_frame when download is complete
        status = self.download_table_dict['status']
        if status == 'complete':
            self.folder_frame.setEnabled(False)


# link
        self.link_lineEdit.setText(self.add_link_dictionary['link'])

# ip_lineEdit initialization
        if self.add_link_dictionary['ip']:
            self.proxy_checkBox.setChecked(True)
            self.ip_lineEdit.setText(self.add_link_dictionary['ip'])
# port_spinBox initialization
            try:
                self.port_spinBox.setValue(
                    int(self.add_link_dictionary['port']))
            except:
                pass
# proxy user lineEdit initialization
            try:
                self.proxy_user_lineEdit.setText(
                    self.add_link_dictionary['proxy_user'])
            except:
                pass
# proxy pass lineEdit initialization
            try:
                self.proxy_pass_lineEdit.setText(
                    self.add_link_dictionary['proxy_passwd'])
            except:
                pass


# download UserName initialization
        if self.add_link_dictionary['download_user']:
            self.download_checkBox.setChecked(True)
            self.download_user_lineEdit.setText(
                self.add_link_dictionary['download_user'])
# download PassWord initialization
            try:
                self.download_pass_lineEdit.setText(
                    self.add_link_dictionary['download_passwd'])
            except:
                pass

# folder_path
        try:
            self.download_folder_lineEdit.setText(
                self.add_link_dictionary['download_path'])
        except:
                pass

# connections
        try:
            self.connections_spinBox.setValue(
                int(self.add_link_dictionary['connections']))
        except:
            pass

# get categories name and add them to add_queue_comboBox
        categories_list = self.parent.persepolis_db.categoriesList()
        for queue in categories_list:
            if queue != 'All Downloads':
                self.add_queue_comboBox.addItem(queue)

    # finding current queue and setting it!
        self.current_category = self.download_table_dict['category'] 

        current_category_index = self.add_queue_comboBox.findText(
            self.current_category)
        self.add_queue_comboBox.setCurrentIndex(current_category_index)


# add_queue_comboBox event
        self.add_queue_comboBox.currentIndexChanged.connect(self.queueChanged)


# limit speed
        limit = str(self.add_link_dictionary['limit_value'])
        if limit != '0':
            self.limit_checkBox.setChecked(True)
            limit_number = limit[0:-1]
            limit_unit = limit[-1]
            self.limit_spinBox.setValue(float(limit_number))
            if limit_unit == "K":
                self.limit_comboBox.setCurrentIndex(0)
            else:
                self.limit_comboBox.setCurrentIndex(1)

# start_time
        if self.add_link_dictionary['start_time']:
            # get hour and minute
            hour, minute = self.add_link_dictionary['start_time'].split(':')
            
            # set time
            q_time = QTime(int(hour), int(minute))
            self.start_time_qDataTimeEdit.setTime(q_time)

            self.start_checkBox.setChecked(True)
# end_time
        if self.add_link_dictionary['end_time']:
            # get hour and minute
            hour, minute = self.add_link_dictionary['end_time'].split(':')

            # set time
            q_time = QTime(int(hour), int(minute))
            self.end_time_qDateTimeEdit(q_time)

            self.end_checkBox.setChecked(True)

        # referer
        if self.add_link_dictionary['referer']:
            self.referer_lineEdit.setText(str(self.add_link_dictionary['referer']))

        if self.add_link_dictionary['header']:
            self.header_lineEdit.setText(str(self.add_link_dictionary['header'])) 

        if self.add_link_dictionary['user_agent']:
            self.user_agent_lineEdit.setText(str(self.add_link_dictionary['user_agent']))

        if self.add_link_dictionary['load_cookies']:
            self.load_cookies_lineEdit.setText((self.add_link_dictionary['load_cookies']))

 


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

    def limitFrame(self, checkBox):

        if self.limit_checkBox.isChecked():
            self.limit_frame.setEnabled(True)
        else:
            self.limit_frame.setEnabled(False)

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
            self.start_checkBox.setCheckState(QtCore.Qt.Unchecked)
            self.start_checkBox.setEnabled(False)

            self.end_checkBox.setCheckState(QtCore.Qt.Unchecked)
            self.end_checkBox.setEnabled(False)
        else:
            self.start_checkBox.setEnabled(True)
            self.end_checkBox.setEnabled(True)

    def okButtonPressed(self, button):
        if not(self.proxy_checkBox.isChecked()):
            ip = None
            port = None
            proxy_user = None
            proxy_passwd = None
        else:
            ip = self.ip_lineEdit.text()
            if not(ip):
                ip = None
            port = str(self.port_spinBox.value())
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
            if self.limit_comboBox.currentText() == "KB/S":
                limit = str(self.limit_spinBox.value()) + str("K")
            else:
                limit = str(self.limit_spinBox.value()) + str("M")

        if not(self.start_checkBox.isChecked()):
            start_time = None
        else:
            start_time = self.start_time_qDataTimeEdit.text()

        if not(self.end_checkBox.isChecked()):
            end_time = None
        else:
            end_time = self.end_time_qDateTimeEdit.text()

        link = self.link_lineEdit.text()
        connections = self.connections_spinBox.value()
        download_path = self.download_folder_lineEdit.text()
 
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

        self.add_link_dictionary['start_time'] = start_time
        self.add_link_dictionary['end_time'] = end_time
        self.add_link_dictionary['link'] = link
        self.add_link_dictionary['ip'] = ip
        self.add_link_dictionary['port'] = port
        self.add_link_dictionary['proxy_user'] = proxy_user
        self.add_link_dictionary['proxy_passwd'] = proxy_passwd
        self.add_link_dictionary['download_user'] = download_user
        self.add_link_dictionary['download_passwd'] = download_passwd
        self.add_link_dictionary['download_path'] = download_path
        self.add_link_dictionary['limit_value'] = limit
        self.add_link_dictionary['connections'] = connections
        self.add_link_dictionary['referer'] = referer
        self.add_link_dictionary['header'] = header
        self.add_link_dictionary['user_agent'] = user_agent
        self.add_link_dictionary['load_cookies'] = load_cookies

        new_category = str(self.add_queue_comboBox.currentText())

        # it means category changed and data base must be updated.
        if new_category != self.current_category:  
            self.download_table_dict['category'] = new_category

            # update data base
            self.parent.persepolis_db.updateDownloadTable([self.download_table_dict])

        # if any thing in add_link_dictionary is changed,then update data base!
        for key in self.add_link_dictionary.keys():
            if self.add_link_dictionary[key] != self.add_link_dictionary_backup[key]:
                
                # update data base
                self.parent.persepolis_db.updateAddLinkTable([self.add_link_dictionary])

                # break the loop
                break

        # if link changed, then update download_db_table in data base
        if self.add_link_dictionary['link'] != self.add_link_dictionary_backup['link']:
            dict = {'gid': self.gid, 'link': link}
            self.parent.persepolis_db.updateDownloadTable([dict])


        # callback to mainwindow
        self.callback(self.add_link_dictionary, self.gid, new_category)

        # close window
        self.close()

    def closeEvent(self, event):
        # save window size and position
        self.persepolis_setting.setValue('PropertiesWindow/size', self.size())
        self.persepolis_setting.setValue(
            'PropertiesWindow/position', self.pos())
        self.persepolis_setting.sync()

        self.destroy()
