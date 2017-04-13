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
#

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QSize, QPoint
import platform
import os
from newopen import Open
from functools import partial
import osCommands
import sys
import urllib
from urllib import request
import webbrowser
import platform
import newopen

# finding os_type
os_type = platform.system()
home_address = str(os.path.expanduser("~"))

# persepolis tmp folder (temporary folder)
if os_type != 'Windows':
    user_name_split = home_address.split('/')
    user_name = user_name_split[2]
    persepolis_tmp = '/tmp/persepolis_' + user_name + '/'
else:
    persepolis_tmp = os.path.join(
        str(home_address), 'AppData', 'Local', 'persepolis_tmp')

class checkupdate(QWidget):
    def __init__(self, persepolis_setting):
        super().__init__()

        self.persepolis_setting = persepolis_setting
        icons = ':/' + \
            str(self.persepolis_setting.value('settings/icons')) + '/'
        self.setWindowIcon(QIcon.fromTheme('persepolis', QIcon(':/icon.svg')))
        self.setWindowTitle('Persepolis Download Manager update')

        # get information dictionary from github
        updatesource = urllib.request.urlopen('https://persepolisdm.github.io/version', data=None)
        serverdict = updatesource.read().decode("utf-8")
        # save information to file
        fileup = open(persepolis_tmp + 'serverdictfile', 'w')  # store in tmp
        fileup.write(str(serverdict))
        fileup.close()
        # read as dictionary
        dictvalue = newopen.readDict(persepolis_tmp + 'serverdictfile')  # read from tmp
        # installed version
        clientversion = self.persepolis_setting.value('version/version')
        # get latest stable version
        serverversion = dictvalue['version']

        # Foundation for download latest windows installer
        def winupdatedl():
            # find system architect
            if platform.architecture()[0] == '64bit':
                webbrowser.open(dictvalue['win64dlurl'])
            elif platform.architecture()[0] == '32bit':
                webbrowser.open(dictvalue['win32dlurl'])

        # checking function
        def updatecheck():
            #Comparison
            if float(serverversion) > float(clientversion):
                statustext.setText('A newer Persepolis release is available')
                # check if it is Windows
                if os_type == "Windows":
                    winupdatedl() # this function download latest release
                if os_type == 'Darwin':
                    webbrowser.open(dictvalue['macdlurl']) # it download latest release for mac
            elif float(serverversion) == float(clientversion):
                statustext.setText('Latest version is installed :)')
            elif float(serverversion) < float(clientversion):
                statustext.setText('You are using beta version')

        # first line text
        uptext = QLabel("The newest is the best , We recommend to update Persepolis")
        uptext.setTextFormat(QtCore.Qt.RichText)
        uptext.setAlignment(QtCore.Qt.AlignCenter)

        # second line text
        versiontext = QLabel('This is Persepolis Download Manager version ' + self.persepolis_setting.value('version/version'))
        versiontext.setAlignment(QtCore.Qt.AlignCenter)

        # release link
        linktext = QLabel('<a href=https://github.com/persepolisdm/persepolis/releases>https://github.com/persepolisdm/persepolis/releases</a>')
        linktext.setAlignment(QtCore.Qt.AlignCenter)
        linktext.setOpenExternalLinks(True)

        # version status
        statustext = QLabel()
        statustext.setTextFormat(QtCore.Qt.RichText)
        statustext.setAlignment(QtCore.Qt.AlignCenter)

        # update button
        checkbutton = QPushButton("Check for new update")
        checkbutton.clicked.connect(updatecheck)

        # verticalLayout
        vbox = QVBoxLayout()
        vbox.addWidget(uptext)
        vbox.addWidget(versiontext)
        vbox.addWidget(linktext)
        vbox.addWidget(checkbutton)
        vbox.addWidget(statustext)

        # horizontalLayout
        hbox = QHBoxLayout()
        hbox.addLayout(vbox)

        # window layout
        self.setLayout(hbox)

        # window size and position
        size = self.persepolis_setting.value(
            'checkupdate/size', QSize(360, 250))
        position = self.persepolis_setting.value(
            'checkupdate/position', QPoint(300, 300))

        self.resize(size)
        self.move(position)

    def closeEvent(self, event):
        # saving window size and position
        self.persepolis_setting.setValue(
            'checkupdate/size', self.size())
        self.persepolis_setting.setValue(
            'checkupdate/position', self.pos())
        self.persepolis_setting.sync()
        self.destroy()
