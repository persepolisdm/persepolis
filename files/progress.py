#!/usr/bin/env python3

# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget , QSizePolicy ,  QInputDialog
from progress_ui import ProgressWindow_Ui
import os , time , ast
from newopen import Open
import download
from bubble import notifySend

home_address = os.path.expanduser("~")

global config_folder
config_folder = str(home_address) + "/.config/persepolis_download_manager"
os.system("mkdir -p  $HOME/.config/persepolis_download_manager")

global download_info_folder
download_info_folder = config_folder + "/download_info"
os.system("mkdir -p  $HOME/.config/persepolis_download_manager/download_info")


class ProgressWindow(ProgressWindow_Ui):
    def __init__(self,gid ):
        super().__init__()
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
        download_info_file_lines_len = 1
        while download_info_file_lines_len != 10 :
            f = Open(download_info_folder + "/" + self.gid) 
            download_info_file_lines = f.readlines()
            f.close()
            download_info_file_lines_len = len(download_info_file_lines)

        add_link_dictionary_str = str(download_info_file_lines[9].strip())
        add_link_dictionary = ast.literal_eval(add_link_dictionary_str) 
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
            
 
    def closeEvent(self, event):
        self.hide()
    def resumePushButtonPressed(self,button):
        if self.status == "paused":
            answer = download.downloadUnpause(self.gid)
            if answer == 'None':
                notifySend("Aria2 did not respond!","Try agian!",10000,'warning' )



    def pausePushButtonPressed(self,button):
        if self.status == "downloading":
            answer = download.downloadPause(self.gid)
            if answer == 'None':
                notifySend("Aria2 did not respond!","Try agian!" , 10000 , 'critical' )


    def stopPushButtonPressed(self,button):
        answer = download.downloadStop(self.gid)
        if answer == 'None':
            notifySend("Aria2 did not respond!","Try agian!" , 10000 , 'critical' )




    def limitCheckBoxToggled(self,checkBoxes): 
        if self.limit_checkBox.isChecked() == True :
            self.limit_frame.setEnabled(True)
            self.limit_pushButton.setEnabled(True)
        else :
            self.limit_frame.setEnabled(False)
            if self.status != 'scheduled':
                download.limitSpeed(self.gid , "0" )
            else:
                f = Open(download_info_folder + "/" + self.gid) 
                download_info_file_lines = f.readlines()
                f.close()
                add_link_dictionary_str = str(download_info_file_lines[9].strip())
                add_link_dictionary = ast.literal_eval(add_link_dictionary_str) 
                add_link_dictionary['limit'] = '0'

                f = Open(download_info_folder + "/" + self.gid , "w")
                for i in range(10):
                    if i == 9 :
                        f.writelines(str(add_link_dictionary) + "\n")
                    else:
                        f.writelines(download_info_file_lines[i].strip() + "\n")

                f.close()

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
        action = self.after_comboBox.currentText()
        self.after_pushButton.setEnabled(False)
        if action == 'Shut Down as root':
            passwd, ok = QInputDialog.getText(self, 'PassWord','Please enter root password:' , QtWidgets.QLineEdit.Password)
            if ok :
                answer = os.system("echo '" + passwd+"' |sudo -S echo 'checking passwd'  "  )
                while answer != 0 :
                    passwd, ok = QInputDialog.getText(self, 'PassWord','Wrong Password!\nTry again!' , QtWidgets.QLineEdit.Password)
                    if ok :
                        answer = os.system("echo '" + passwd+"' |sudo -S echo 'checking passwd'  "  )
                    else:
                        ok = False
                        break

                if ok != False :
                    os.system("bash " + "shutdown_script_root  '" + passwd + "' '"+ self.gid + "' &" )
                else:
                    self.after_checkBox.setChecked(False)
            else:
                self.after_checkBox.setChecked(False)
        else:
            os.system("bash " + "shutdown_script  '" + self.gid  + "' &" )



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
            f = Open(download_info_folder + "/" + self.gid) 
            download_info_file_lines = f.readlines()
            f.close()
            add_link_dictionary_str = str(download_info_file_lines[9].strip())
            add_link_dictionary = ast.literal_eval(add_link_dictionary_str) 
            add_link_dictionary['limit'] = limit

            f = Open(download_info_folder + "/" + self.gid , "w")
            for i in range(10):
                if i == 9 :
                    f.writelines(str(add_link_dictionary) + "\n")
                else:
                    f.writelines(download_info_file_lines[i].strip() + "\n")

            f.close()






