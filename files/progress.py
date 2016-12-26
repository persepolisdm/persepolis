
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
from PyQt5.QtWidgets import QWidget , QSizePolicy ,  QInputDialog
from PyQt5.QtCore import QSize , QPoint
from progress_ui import ProgressWindow_Ui
import os , time , ast
from newopen import Open , readList , writeList , readDict
import download
from bubble import notifySend


home_address = os.path.expanduser("~")

global config_folder
config_folder = str(home_address) + "/.config/persepolis_download_manager"

global download_info_folder
download_info_folder = config_folder + "/download_info"


class ProgressWindow(ProgressWindow_Ui):
    def __init__(self, parent ,gid , persepolis_setting ):
        super().__init__()
        self.persepolis_setting = persepolis_setting
        self.parent = parent
        self.gid = gid
        self.status = None
        self.resume_pushButton.clicked.connect(self.resumePushButtonPressed)
        self.stop_pushButton.clicked.connect(self.stopPushButtonPressed)
        self.pause_pushButton.clicked.connect(self.pausePushButtonPressed)
        self.download_progressBar.setValue(0)
        self.limit_pushButton.clicked.connect(self.limitPushButtonPressed)

        self.limit_frame.setEnabled(False)
        self.limit_checkBox.toggled.connect(self.limitCheckBoxToggled)

        self.after_frame.setEnabled(False)
        self.after_checkBox.toggled.connect(self.afterCheckBoxToggled)
        
        self.after_pushButton.clicked.connect(self.afterPushButtonPressed)
#check if limit speed actived by user or not
        download_info_file_list_len = 1
        while download_info_file_list_len != 13 :
            download_info_file = download_info_folder + "/" + self.gid
            download_info_file_list = readList(download_info_file) 
            download_info_file_list_len = len(download_info_file_list)

        add_link_dictionary = download_info_file_list[9]
        limit = add_link_dictionary['limit']  
        if limit != 0:
            limit_number = limit[:-1]
            limit_unit = limit[-1]
            self.limit_spinBox.setValue(int(limit_number))
            if limit_unit == 'K':
                self.after_comboBox.setCurrentIndex(0)
            else:
                self.after_comboBox.setCurrentIndex(1)
            self.limit_checkBox.setChecked(True)
            
        self.after_comboBox.currentIndexChanged.connect(self.afterComboBoxChanged)
        self.limit_comboBox.currentIndexChanged.connect(self.limitComboBoxChanged)
        self.limit_spinBox.valueChanged.connect(self.limitComboBoxChanged)

  #setting window size and position
        size = self.persepolis_setting.value('ProgressWindow/size' , QSize(595 , 274))
        position = self.persepolis_setting.value('ProgressWindow/position' , QPoint(300 , 300))
        self.resize(size)
        self.move(position)


    def closeEvent(self, event):
        #saving window size and position
        self.persepolis_setting.setValue('ProgressWindow/size' , self.size())
        self.persepolis_setting.setValue('ProgressWindow/position' , self.pos())
        self.persepolis_setting.sync()


        if self.parent.isVisible() == False:
            self.parent.minMaxTray(event)


        self.hide()
        

    def resumePushButtonPressed(self,button):
        if self.status == "paused":
            answer = download.downloadUnpause(self.gid)
#if aria2 did not respond , then this function is checking for aria2 availability , and if aria2 disconnected then aria2Disconnected is executed 
            if answer == 'None':
                version_answer = download.aria2Version()
                if version_answer == 'did not respond':
                    self.parent.aria2Disconnected()
                    notifySend("Aria2 disconnected!","Persepolis is trying to connect!be patient!",10000,'warning' , systemtray = self.parent.system_tray_icon )
                else:
                    notifySend("Aria2 did not respond!","Try agian!",10000,'warning' , systemtray = self.parent.system_tray_icon )




    def pausePushButtonPressed(self,button):
        if self.status == "downloading":
            answer = download.downloadPause(self.gid)
#if aria2 did not respond , then this function is checking for aria2 availability , and if aria2 disconnected then aria2Disconnected is executed 
            if answer == 'None':
                version_answer = download.aria2Version()
                if version_answer == 'did not respond':
                    self.parent.aria2Disconnected()
                    download.downloadStop(self.gid)
                    notifySend("Aria2 disconnected!","Persepolis is trying to connect!be patient!",10000,'warning' , systemtray = self.parent.system_tray_icon )
                else:
                    notifySend("Aria2 did not respond!" , "Try agian!" , 10000 , 'critical' , systemtray = self.parent.system_tray_icon )
 

    def stopPushButtonPressed(self,button):
        answer = download.downloadStop(self.gid)
#if aria2 did not respond , then this function is checking for aria2 availability , and if aria2 disconnected then aria2Disconnected is executed 
        if answer == 'None':
            version_answer = download.aria2Version()
            if version_answer == 'did not respond':
                self.parent.aria2Disconnected()
                notifySend("Aria2 disconnected!","Persepolis is trying to connect!be patient!",10000,'warning' , systemtray = self.parent.system_tray_icon )
 


    def limitCheckBoxToggled(self,checkBoxes): 
        if self.limit_checkBox.isChecked() == True :
            self.limit_frame.setEnabled(True)
            self.limit_pushButton.setEnabled(True)
        else :
            self.limit_frame.setEnabled(False)
            if self.status != 'scheduled':
                download.limitSpeed(self.gid , "0" )
            else:
                download_info_file = download_info_folder + '/' + self.gid
                download_info_file_list = readList(download_info_file)
                add_link_dictionary = download_info_file_list[9]
                add_link_dictionary['limit'] = '0'
                download_info_file_list[9] = add_link_dictionary
                writeList(download_info_file , download_info_file_list)

    def limitComboBoxChanged(self , connect):
        self.limit_pushButton.setEnabled(True)
    
    def afterComboBoxChanged(self , connect):
        self.after_pushButton.setEnabled(True)

 
    def afterCheckBoxToggled(self,checkBoxes): 
        if self.after_checkBox.isChecked() == True :
                self.after_frame.setEnabled(True)
        else :
            self.after_frame.setEnabled(False)
            f = Open('/tmp/persepolis/shutdown/' + self.gid , 'w')
            f.writelines('canceled')
            f.close()

    def afterPushButtonPressed(self , button):
        self.after_pushButton.setEnabled(False)
        #getting root password
        passwd, ok = QInputDialog.getText(self, 'PassWord','Please enter root password:' , QtWidgets.QLineEdit.Password)
        if ok :
            #checking password
            answer = os.system("echo '" + passwd+"' |sudo -S echo 'checking passwd'  "  )
            while answer != 0 :
                passwd, ok = QInputDialog.getText(self, 'PassWord','Wrong Password!\nTry again!' , QtWidgets.QLineEdit.Password)
                if ok :
                    answer = os.system("echo '" + passwd +"' |sudo -S echo 'checking passwd'  "  )
                else:
                    ok = False
                    break

            if ok != False :
                    #shutdown_script_root will create by initialization.py on persepolis startup
                    #sending password and queue name to shutdown_script_root
                    #this script is creating a file with name of self.gid in  this folder "/tmp/persepolis/shutdown/" . and writing a "wait" word in this file 
                    #shutdown_script_root is checking that file every second . when "wait" changes to "shutdown" in that file then script is shutting down system 
 
                    os.system("bash " + "/tmp/persepolis/shutdown_script_root  '" + passwd + "' '"+ self.gid + "' &" )
            else:
                self.after_checkBox.setChecked(False)
        else:
            self.after_checkBox.setChecked(False)



    def limitPushButtonPressed(self,button):
        self.limit_pushButton.setEnabled(False)
        if self.limit_comboBox.currentText() == "KB/S" :
            limit = str(self.limit_spinBox.value()) + str("K")
        else :
            limit = str(self.limit_spinBox.value()) + str("M")
#if download was started before , send the limit_speed request to aria2 . else save the request in download_information_file
        if self.status != 'scheduled':
            download.limitSpeed(self.gid , limit)
        else:
            download_info_file = download_info_folder + "/" + self.gid
            download_info_file_list = readList(download_info_file)
            add_link_dictionary = download_info_file_list[9]
            add_link_dictionary['limit'] = limit
            download_info_file_list[9] = add_link_dictionary
            writeList(download_info_file , download_info_file_list)



