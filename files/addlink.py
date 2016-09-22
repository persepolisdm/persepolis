#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QHBoxLayout ,  QApplication ,  QFileDialog,  QCheckBox , QLineEdit , QPushButton  
from PyQt5.QtGui import QIcon
import os , string , ast , functools
from addlink_ui import AddLinkWindow_Ui
from newopen import Open


home_address = os.path.expanduser("~")
config_folder = str(home_address) + "/.config/persepolis_download_manager"

#setting
setting_file = config_folder + '/setting'
f = Open(setting_file)
setting_file_lines = f.readlines()
f.close()
setting_dict_str = str(setting_file_lines[0].strip())
setting_dict = ast.literal_eval(setting_dict_str) 

icons =':/' + str(setting_dict['icons']) + '/'


class AddLinkWindow(AddLinkWindow_Ui):
    def __init__(self , callback,flashgot_add_link_dictionary = {}):
        super().__init__()
        self.callback = callback
        self.flashgot_add_link_dictionary = flashgot_add_link_dictionary

#add change_name field
        self.change_name_horizontalLayout = QHBoxLayout() 
        self.change_name_checkBox = QCheckBox(self.link_frame)
        self.change_name_checkBox.setText('Change File Name : ')
        self.change_name_horizontalLayout.addWidget(self.change_name_checkBox)



        self.change_name_lineEdit = QLineEdit(self.link_frame)
        self.change_name_horizontalLayout.addWidget(self.change_name_lineEdit)

        self.link_verticalLayout.addLayout(self.change_name_horizontalLayout)

#adding download_later button
        self.download_later_pushButton = QPushButton(self.widget)
        self.download_later_pushButton.setIcon(QIcon(icons + 'stop'))


        self.buttons_horizontalLayout.addWidget(self.download_later_pushButton)

        self.download_later_pushButton.setText("Download later")
#entry initialization            

        f = Open(setting_file)
        setting_file_lines = f.readlines()
        f.close()
        setting_dict_str = str(setting_file_lines[0].strip())
        setting_dict = ast.literal_eval(setting_dict_str) 
        global connections
        connections = int(setting_dict['connections'])
        global download_path
        download_path = str(setting_dict['download_path'])


        global init_file
        init_file = str(home_address) + "/.config/persepolis_download_manager/addlink_init_file"
        os.system("touch " + init_file)
        f = Open(init_file)
        init_file_lines = f.readlines()
        f.close()

#initialization
        self.connections_spinBox.setValue(connections)
        self.download_folder_lineEdit.setText(download_path)
        self.download_folder_lineEdit.setEnabled(False)

        self.ok_pushButton.setEnabled(False)
        self.link_lineEdit.textChanged.connect(self.linkLineChanged)
#AddLink - checking clipboard for link!   
        if 'link' in self.flashgot_add_link_dictionary : 
            self.link_lineEdit.setText(str(self.flashgot_add_link_dictionary['link']))
            del self.flashgot_add_link_dictionary['link']
        else:    
            clipboard = QApplication.clipboard()
            text = clipboard.text()
            try:
                if ("tp:/" in text[2:6]) or ("tps:/" in text[2:7]) :
                    self.link_lineEdit.setText(str(text))
            except:
                pass
#ip_lineEdit initialization 
        try:
            self.ip_lineEdit.setText(init_file_lines[0].strip())
        except :
            pass

#proxy user lineEdit initialization 
        try:
            self.proxy_user_lineEdit.setText(init_file_lines[2].strip())
        except :
            pass

#port_spinBox initialization 
        try:
            self.port_spinBox.setValue(int(init_file_lines[1].strip()))
        except :
            pass


#download UserName initialization
        try:
            self.download_user_lineEdit.setText(init_file_lines[3].strip())
        except :
            pass
#connect folder_pushButton
        self.folder_pushButton.clicked.connect(self.changeFolder)

#connect OK and canel download_later button

        self.cancel_pushButton.clicked.connect(self.cancelButtonPressed)
        self.ok_pushButton.clicked.connect(functools.partial(self.okButtonPressed ,download_later = 'no'))
        self.download_later_pushButton.clicked.connect(functools.partial(self.okButtonPressed , download_later = 'yes'))
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


        self.change_name_lineEdit.setEnabled(False)
        self.change_name_checkBox.toggled.connect(self.changeName)

#check name of flashgot link 
        if 'out' in self.flashgot_add_link_dictionary:
            self.change_name_lineEdit.setText(str(self.flashgot_add_link_dictionary['out']))
            self.change_name_checkBox.setChecked(True)
            del self.flashgot_add_link_dictionary['out']

      
           
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
        fname = QFileDialog.getExistingDirectory(self,'Open f', download_path )
        if os.path.isdir(fname):
            self.download_folder_lineEdit.setText(fname)

    def linkLineChanged(self,lineEdit):
        if str(self.link_lineEdit.text()) == '' :
            self.ok_pushButton.setEnabled(False)
        else :
            self.ok_pushButton.setEnabled(True)

    def changeName(self,checkBoxes):
        if self.change_name_checkBox.isChecked() == True:
            self.change_name_lineEdit.setEnabled(True)
        else:
            self.change_name_lineEdit.setEnabled(False)


#close window if cancelButton Pressed
    def cancelButtonPressed(self,button):
        self.close()

    def okButtonPressed(self,button , download_later):
        global init_file
        f = Open(init_file , "w")
#writing user's input data to init file
        for i in self.ip_lineEdit.text(),self.port_spinBox.value(),self.proxy_user_lineEdit.text(),self.download_user_lineEdit.text()  :
            f.writelines(str(i) + "\n")
        f.close()

        if self.proxy_checkBox.isChecked() == False :
            ip = None
            port = None
            proxy_user = None
            proxy_passwd = None
        else :
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

        if self.change_name_checkBox.isChecked() == False:
            out = None
        else:
            out = str(self.change_name_lineEdit.text())
            

        link = self.link_lineEdit.text()

        connections = self.connections_spinBox.value()
        download_path = self.download_folder_lineEdit.text()

        if not ('referer' in self.flashgot_add_link_dictionary) :
            self.flashgot_add_link_dictionary['referer'] = None

        if not ('header' in self.flashgot_add_link_dictionary):
            self.flashgot_add_link_dictionary['header'] = None


        if not('user-agent' in self.flashgot_add_link_dictionary):
            self.flashgot_add_link_dictionary['user-agent'] = None

        if not('load-cookies' in self.flashgot_add_link_dictionary):
            self.flashgot_add_link_dictionary['load-cookies'] = None

        final_download_path = None
        self.add_link_dictionary = {'out' :out , 'final_download_path':final_download_path , 'start_hour':start_hour ,'start_minute' : start_minute ,'end_hour' : end_hour ,'end_minute':end_minute , 'link':link , 'ip':ip , 'port':port , 'proxy_user':proxy_user , 'proxy_passwd' : proxy_passwd , 'download_user':download_user , 'download_passwd': download_passwd ,'connections':connections , 'limit':limit, 'download_path':download_path }
        for i in self.flashgot_add_link_dictionary.keys():
            self.add_link_dictionary[i] = self.flashgot_add_link_dictionary[i]


        del self.flashgot_add_link_dictionary
        self.callback(self.add_link_dictionary , download_later)


        self.close()
 
     


