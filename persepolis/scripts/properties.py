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
from PyQt5.QtCore import QSize, QPoint, QDir
import os
import ast
from persepolis.scripts.newopen import Open, writeList, readList, readDict
from persepolis.gui.addlink_ui import AddLinkWindow_Ui
import platform
from persepolis.scripts.check_proxy import getProxy

os_type = platform.system()


home_address = os.path.expanduser("~")

# config_folder
if os_type == 'Linux' or os_type == 'FreeBSD' or os_type == 'OpenBSD':
    config_folder = os.path.join(
        str(home_address), ".config/persepolis_download_manager")
elif os_type == 'Darwin':
    config_folder = os.path.join(
        str(home_address), "Library/Application Support/persepolis_download_manager")
elif os_type == 'Windows':
    config_folder = os.path.join(
        str(home_address), 'AppData', 'Local', 'persepolis_download_manager')


download_info_folder = os.path.join(config_folder, "download_info")

queues_list_file = os.path.join(config_folder, 'queues_list')
category_folder = os.path.join(config_folder, 'category_folder')


# setting
setting_file = os.path.join(config_folder, 'setting')


class PropertiesWindow(AddLinkWindow_Ui):
    def __init__(self, callback, gid, persepolis_setting):
        super().__init__(persepolis_setting)

        self.persepolis_setting = persepolis_setting
        self.download_later_pushButton.hide()  # hiding download_later_pushButton
        self.change_name_checkBox.hide()  # hiding change_name_checkBox
        self.change_name_lineEdit.hide()  # hiding change_name_lineEdit

        self.callback = callback
        self.gid = gid

        global connections
        connections = int(
            self.persepolis_setting.value('settings/connections'))

# hiding options_pushButton
        self.options_pushButton.hide()

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


# initialization
        self.connections_spinBox.setValue(connections)
        download_info_file = download_info_folder + "/" + self.gid
        download_info_file_list = readList(download_info_file)
        self.add_link_dictionary = download_info_file_list[9]
# disable folder_frame when download is complete
        status = download_info_file_list[1]
        if status == 'complete':
            self.folder_frame.setEnabled(False)


# link
        self.link_lineEdit.setText(self.add_link_dictionary['link'])

# ip_lineEdit initialization
        if self.add_link_dictionary['ip'] != None:
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
        if self.add_link_dictionary['download_user'] != None:
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

# finding categories name and adding them to add_queue_comboBox
        self.add_queue_comboBox.addItem('Single Downloads')
        f_queues_list = Open(queues_list_file)
        queues_list_file_lines = f_queues_list.readlines()
        f_queues_list.close()
        for queue in queues_list_file_lines:
            queue_strip = queue.strip()
            self.add_queue_comboBox.addItem(str(queue_strip))

    # finding current queue and setting it!
        self.current_category = str(download_info_file_list[12])

        current_category_index = self.add_queue_comboBox.findText(
            self.current_category)
        self.add_queue_comboBox.setCurrentIndex(current_category_index)


# add_queue_comboBox event
        self.add_queue_comboBox.currentIndexChanged.connect(self.queueChanged)


# limit speed
        limit = str(self.add_link_dictionary['limit'])
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
        if self.add_link_dictionary['start_hour'] != None:
            self.start_checkBox.setChecked(True)
            self.start_hour_spinBox.setValue(
                int(self.add_link_dictionary['start_hour']))
            self.start_minute_spinBox.setValue(
                int(self.add_link_dictionary['start_minute']))
# end_time
        if self.add_link_dictionary['end_hour'] != None:
            self.end_checkBox.setChecked(True)
            self.end_hour_spinBox.setValue(
                int(self.add_link_dictionary['end_hour']))
            self.end_minute_spinBox.setValue(
                int(self.add_link_dictionary['end_minute']))

 # setting window size and position
        size = self.persepolis_setting.value(
            'PropertiesWindow/size', QSize(700, 500))
        position = self.persepolis_setting.value(
            'PropertiesWindow/position', QPoint(300, 300))
        self.resize(size)
        self.move(position)

# detected system proxy setting, and set ip_lineEdit and port_spinBox
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
            self.detect_proxy_label.setText('Detecting proxy setting was unsuccessful!')




# activate frames if checkBoxes checked
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
        if self.proxy_checkBox.isChecked() == False:
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

        if self.download_checkBox.isChecked() == False:
            download_user = None
            download_passwd = None
        else:
            download_user = self.download_user_lineEdit.text()
            if not(download_user):
                download_user = None
            download_passwd = self.download_pass_lineEdit.text()
            if not(download_passwd):
                download_passwd = None

        if self.limit_checkBox.isChecked() == False:
            limit = 0
        else:
            if self.limit_comboBox.currentText() == "KB/S":
                limit = str(self.limit_spinBox.value()) + str("K")
            else:
                limit = str(self.limit_spinBox.value()) + str("M")

        if self.start_checkBox.isChecked() == False:
            start_hour = None
            start_minute = None
        else:
            start_hour = str(self.start_hour_spinBox.value())
            start_minute = str(self.start_minute_spinBox.value())

        if self.end_checkBox.isChecked() == False:
            end_hour = None
            end_minute = None
        else:
            end_hour = str(self.end_hour_spinBox.value())
            end_minute = str(self.end_minute_spinBox.value())

        link = self.link_lineEdit.text()
        connections = self.connections_spinBox.value()
        download_path = self.download_folder_lineEdit.text()

        self.add_link_dictionary['start_hour'] = start_hour
        self.add_link_dictionary['start_minute'] = start_minute
        self.add_link_dictionary['end_hour'] = end_hour
        self.add_link_dictionary['end_minute'] = end_minute
        self.add_link_dictionary['link'] = link
        self.add_link_dictionary['ip'] = ip
        self.add_link_dictionary['port'] = port
        self.add_link_dictionary['proxy_user'] = proxy_user
        self.add_link_dictionary['proxy_passwd'] = proxy_passwd
        self.add_link_dictionary['download_user'] = download_user
        self.add_link_dictionary['download_passwd'] = download_passwd
        self.add_link_dictionary['download_path'] = download_path
        self.add_link_dictionary['limit'] = limit
        self.add_link_dictionary['connections'] = connections

        new_category = str(self.add_queue_comboBox.currentText())
        if new_category != self.current_category:  # it means category changed
            # first download must eliminated form former category
            # reading current_category
            current_category_file = os.path.join(
                category_folder, self.current_category)

            f = Open(current_category_file)
            f_list = f.readlines()
            f.close()
            # eliminating gid of download from current_category_file
            f = Open(current_category_file, 'w')
            for line in f_list:
                gid = line.strip()
                if gid != self.gid:
                    f.writelines(gid + '\n')

            f.close()

            # adding download to the new category
            new_category_file = os.path.join(
                category_folder, str(new_category))

            f = Open(new_category_file, 'a')
            f.writelines(self.gid + '\n')
            f.close()

        self.callback(self.add_link_dictionary, self.gid, new_category)

        self.close()

    def closeEvent(self, event):
        # saving window size and position
        self.persepolis_setting.setValue('PropertiesWindow/size', self.size())
        self.persepolis_setting.setValue(
            'PropertiesWindow/position', self.pos())
        self.persepolis_setting.sync()

        self.destroy()
