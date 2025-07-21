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
from persepolis.scripts.addlink import AddLinkWindow
try:
    from PySide6.QtCore import QCoreApplication
except:
    from PyQt5.QtCore import QCoreApplication


class AddTorrentWindow(AddLinkWindow):
    def __init__(self, parent, callback, persepolis_setting):
        super().__init__(parent, callback, persepolis_setting)
        self.setWindowTitle(QCoreApplication.translate("addtorrent_ui_tr", "Add  Torrent"))

        self.link_label.setText(QCoreApplication.translate("addtorrent_ui_tr", "Magnet link: "))

    def okButtonPressed(self, download_later, button=None):
        # user submitted information by pressing ok_pushButton, so get information
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
        ip, port, proxy_user, proxy_passwd, proxy_type = self.getProxyInformation()
        if proxy_type is not None:
            self.persepolis_setting.setValue('add_link_initialization/proxy_type', proxy_type)

        # get download username and password information
        download_user, download_passwd = self.getUserPass()

        # get start time for download if user set that.
        if not (self.start_checkBox.isChecked()):
            start_time = None
        else:
            start_time = self.start_time_qDataTimeEdit.text()

        # get end time for download if user set that.
        if not (self.end_checkBox.isChecked()):
            end_time = None
        else:
            end_time = self.end_time_qDateTimeEdit.text()

        # check that if user set new name for download file.
        if self.change_name_checkBox.isChecked():
            out = str(self.change_name_lineEdit.text())
            self.plugin_add_link_dictionary['out'] = out
        else:
            out = None

        # get download link
        link = self.link_lineEdit.text()

        # get number of connections
        connections = self.connections_spinBox.value()

        # get download_path
        download_path = self.download_folder_lineEdit.text()

        # get additinal information
        referer, header, user_agent, load_cookies = self.getAdditionalInformation()

        # save information in a dictionary(add_link_dictionary).
        self.add_link_dictionary = {'referer': referer, 'header': header, 'user_agent': user_agent, 'load_cookies': load_cookies,
                                    'out': out, 'start_time': start_time, 'end_time': end_time, 'link': link, 'ip': ip,
                                    'port': port, 'proxy_user': proxy_user, 'proxy_passwd': proxy_passwd, 'proxy_type': proxy_type,
                                    'download_user': download_user, 'download_passwd': download_passwd,
                                    'connections': connections, 'limit_value': 10, 'download_path': download_path}

        # get category of download
        category = str(self.add_queue_comboBox.currentText())

        del self.plugin_add_link_dictionary

        # return information to mainwindow
        self.callback(self.add_link_dictionary, download_later, category)

        # close window
        self.close()
