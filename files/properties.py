#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog 
import os , string , ast
from newopen import Open , writeList , readList
from addlink_ui import AddLinkWindow_Ui


home_address = os.path.expanduser("~")

config_folder = str(home_address) + "/.config/persepolis_download_manager"
os.system("mkdir -p  $HOME/.config/persepolis_download_manager")

download_info_folder = config_folder + "/download_info"
os.system("mkdir -p  $HOME/.config/persepolis_download_manager/download_info")

config_folder = str(home_address) + "/.config/persepolis_download_manager"

#setting
setting_file = config_folder + '/setting'

class PropertiesWindow(AddLinkWindow_Ui):
    def __init__(self,callback,gid):
        super().__init__()

        self.download_later_pushButton.hide() #hiding download_later_pushButton

        self.callback = callback
        self.gid = gid
        
        f = Open(setting_file)
        setting_file_lines = f.readlines()
        f.close()
        setting_dict_str = str(setting_file_lines[0].strip())
        setting_dict = ast.literal_eval(setting_dict_str) 

        global connections
        connections = int(setting_dict['connections'])


#connect folder_pushButton
        self.folder_pushButton.clicked.connect(self.changeFolder)
        self.download_folder_lineEdit.setEnabled(False)

        self.ok_pushButton.setEnabled(False)
        self.link_lineEdit.textChanged.connect(self.linkLineChanged)

# connect OK and canel button

        self.cancel_pushButton.clicked.connect(self.cancelButtonPressed)
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


#initialization
        self.connections_spinBox.setValue(connections)
        download_info_file = download_info_folder + "/" + self.gid
        download_info_file_list = readList(download_info_file) 
        self.add_link_dictionary = download_info_file_list[9]
#disable folder_frame when download is complete
        status = download_info_file_list[1] 
        if status == 'complete':
            self.folder_frame.setEnabled(False)


#link        
        self.link_lineEdit.setText(self.add_link_dictionary['link'])

#ip_lineEdit initialization 
        if self.add_link_dictionary['ip'] != None :
            self.proxy_checkBox.setChecked(True)
            self.ip_lineEdit.setText(self.add_link_dictionary['ip'])
#port_spinBox initialization 
            try:
                self.port_spinBox.setValue(int(self.add_link_dictionary['port']))
            except :
                pass
#proxy user lineEdit initialization 
            try:
                self.proxy_user_lineEdit.setText(self.add_link_dictionary['proxy_user'])
            except :
                pass
#proxy pass lineEdit initialization 
            try:
                self.proxy_pass_lineEdit.setText(self.add_link_dictionary['proxy_passwd'])
            except :
                pass



#download UserName initialization
        if self.add_link_dictionary['download_user'] != None :
            self.download_checkBox.setChecked(True)
            self.download_user_lineEdit.setText(self.add_link_dictionary['download_user'])
#download PassWord initialization
            try:
                self.download_pass_lineEdit.setText(self.add_link_dictionary['download_passwd'])
            except :
                pass

#folder_path
        if self.add_link_dictionary['final_download_path'] != None :
            self.download_folder_lineEdit.setText(str(self.add_link_dictionary['final_download_path']))
        else:    
            try:
                self.download_folder_lineEdit.setText(self.add_link_dictionary['download_path'])
            except:
                pass

#connections
        try:
            self.connections_spinBox.setValue(int(self.add_link_dictionary['connections']))
        except :
            pass
            
#limit speed            
        limit = str(self.add_link_dictionary['limit'])
        if limit != '0' :
            self.limit_checkBox.setChecked(True)
            limit_number = limit[0:-1]
            limit_unit = limit[-1]
            self.limit_spinBox.setValue(int(limit_number))
            if limit_unit == "K":
                self.limit_comboBox.setCurrentIndex(0)
            else :
                self.limit_comboBox.setCurrentIndex(1)
#start_time 
        if self.add_link_dictionary['start_hour'] != None :
            self.start_checkBox.setChecked(True)
            self.start_hour_spinBox.setValue(int(self.add_link_dictionary['start_hour']))
            self.start_minute_spinBox.setValue(int(self.add_link_dictionary['start_minute']))
#end_time
        if self.add_link_dictionary['end_hour'] != None :
            self.end_checkBox.setChecked(True)
            self.end_hour_spinBox.setValue(int(self.add_link_dictionary['end_hour']))
            self.end_minute_spinBox.setValue(int(self.add_link_dictionary['end_minute']))
        
            

       
           
#activate frames if checkBoxes checked
    def proxyFrame(self,checkBox):

        if self.proxy_checkBox.isChecked() == True :
            self.proxy_frame.setEnabled(True)
        else :
            self.proxy_frame.setEnabled(False)
    def downloadFrame(self,checkBox):

        if self.download_checkBox.isChecked() == True :
            self.download_frame.setEnabled(True)
        else :
            self.download_frame.setEnabled(False)

    def limitFrame(self,checkBox):

        if self.limit_checkBox.isChecked() == True :
            self.limit_frame.setEnabled(True)
        else :
            self.limit_frame.setEnabled(False)

    def startFrame(self,checkBox):

        if self.start_checkBox.isChecked() == True :
            self.start_frame.setEnabled(True)
        else :
            self.start_frame.setEnabled(False)

    def endFrame(self,checkBox):

        if self.end_checkBox.isChecked() == True :
            self.end_frame.setEnabled(True)
        else :
            self.end_frame.setEnabled(False)



    def changeFolder(self,button):
        fname = QFileDialog.getExistingDirectory(self,'Open f', '/home')
        if os.path.isdir(fname):
            self.download_folder_lineEdit.setText(fname)

    def linkLineChanged(self,lineEdit):
        if str(self.link_lineEdit.text()) == '' :
            self.ok_pushButton.setEnabled(False)
        else :
            self.ok_pushButton.setEnabled(True)




#close window if cancelButton Pressed
    def cancelButtonPressed(self,button):
        self.close()

    def okButtonPressed(self,button):
        if self.proxy_checkBox.isChecked() == False :
            ip = None
            port = None
            proxy_user = None
            proxy_passwd = None
        else :
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

        if self.download_checkBox.isChecked() == False :
            download_user = None
            download_passwd = None
        else :
            download_user = self.download_user_lineEdit.text()
            if not(download_user):
                download_user = None
            download_passwd = self.download_pass_lineEdit.text()
            if not(download_passwd):
                download_passwd = None

        if self.limit_checkBox.isChecked() == False :
            limit = 0
        else :
            if self.limit_comboBox.currentText() == "KB/S" :
                limit = str(self.limit_spinBox.value()) + str("K")
            else :
                limit = str(self.limit_spinBox.value()) + str("M")

        if self.start_checkBox.isChecked() == False :
            start_hour = None
            start_minute = None
        else :
            start_hour = str(self.start_hour_spinBox.value())
            start_minute = str(self.start_minute_spinBox.value())

        if self.end_checkBox.isChecked() == False :
            end_hour = None
            end_minute = None
        else :
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
        self.callback(self.add_link_dictionary , self.gid)


        self.close()
 

