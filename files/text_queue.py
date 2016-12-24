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
from text_queue_ui import TextQueue_Ui
from PyQt5 import QtWidgets , QtCore , QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTableWidgetItem , QFileDialog
from newopen import Open
import download
import ast , os 
import osCommands

home_address = os.path.expanduser("~")
config_folder = str(home_address) + "/.config/persepolis_download_manager"
queues_list_file = config_folder + '/queues_list'
#setting
setting_file = config_folder + '/setting'
f = Open(setting_file)
setting_file_lines = f.readlines()
f.close()
setting_dict_str = str(setting_file_lines[0].strip())
setting_dict = ast.literal_eval(setting_dict_str) 

icons =':/' + str(setting_dict['icons']) + '/'


class TextQueue(TextQueue_Ui):
    def __init__(self , parent , file_path , callback ):
        super().__init__()
        self.callback = callback
        self.file_path = file_path
        self.parent = parent
        #setting file column hidden in links_table
        self.links_table.setColumnHidden(1 , True)

        #reading text file lines and finding links.
        f = Open(self.file_path)
        f_links_list = f.readlines()
        f.close()

        f_links_list.reverse()
        #checking links! links must start with http or https or ftp
        link_list = []
        for link in f_links_list :
            text = link.strip()
            if ("tp:/" in text[2:6]) or ("tps:/" in text[2:7]) :
                link_list.append(text)

        for link in link_list :
            self.links_table.insertRow(0)
            item = QTableWidgetItem(str(link))

            #adding checkbox to the item
            item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.Checked)

            #inserting item
            self.links_table.setItem(0 , 0 , item)


        #finding queues name and adding them to add_queue_comboBox 
        f_queues_list = Open(queues_list_file)
        queues_list_file_lines = f_queues_list.readlines()
        f_queues_list.close()
        for queue in queues_list_file_lines :
            queue_strip = queue.strip()
            self.add_queue_comboBox.addItem(str(queue_strip))

        self.add_queue_comboBox.addItem('Single Downloads')

        self.add_queue_comboBox.addItem(QIcon(icons + 'add_queue') ,'Create new queue')

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
        osCommands.touch(init_file)
        f = Open(init_file)
        init_file_lines = f.readlines()
        f.close()

#initialization
        self.connections_spinBox.setValue(connections)
        self.download_folder_lineEdit.setText(download_path)
        self.download_folder_lineEdit.setEnabled(False)

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

#connect OK and canel button

        self.cancel_pushButton.clicked.connect(self.cancelButtonPressed)
        self.ok_pushButton.clicked.connect(self.okButtonPressed) 

#frames and checkBoxes
        self.proxy_frame.setEnabled(False)
        self.proxy_checkBox.toggled.connect(self.proxyFrame)

        self.download_frame.setEnabled(False)
        self.download_checkBox.toggled.connect(self.downloadFrame)

        self.limit_frame.setEnabled(False)
        self.limit_checkBox.toggled.connect(self.limitFrame)
    
        #set focus to ok button
        self.ok_pushButton.setFocus()

# add_queue_comboBox event
        self.add_queue_comboBox.currentIndexChanged.connect(self.queueChanged) 


    def queueChanged(self,combo):
        if str(self.add_queue_comboBox.currentText()) == 'Create new queue' :
            new_queue = self.parent.createQueue(combo)
            if new_queue != None :
                #clearing comboBox
                self.add_queue_comboBox.clear()
                #loading queue list again!
                f_queues_list = Open(queues_list_file)
                queues_list_file_lines = f_queues_list.readlines()
                f_queues_list.close()
                for queue in queues_list_file_lines :
                    queue_strip = queue.strip()
                    self.add_queue_comboBox.addItem(str(queue_strip))

                self.add_queue_comboBox.addItem('Single Downloads')

                self.add_queue_comboBox.addItem(QIcon(icons + 'add_queue') ,'Create new queue')

                #finding index of new_queue and setting comboBox for it
                index = self.add_queue_comboBox.findText(str(new_queue))
                self.add_queue_comboBox.setCurrentIndex(index) 
            else:
                self.add_queue_comboBox.setCurrentIndex(0)


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

    def changeFolder(self,button):
        fname = QFileDialog.getExistingDirectory(self,'Select a directory', download_path )
        if os.path.isdir(fname):
            self.download_folder_lineEdit.setText(fname)


#close window if cancelButton Pressed
    def cancelButtonPressed(self,button):
        self.saveWindowSize()
        self.close()

    def okButtonPressed(self,button):
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

        category = str(self.add_queue_comboBox.currentText()) 

        connections = self.connections_spinBox.value()
        download_path = self.download_folder_lineEdit.text()


        final_download_path = None

        now_date_list = download.nowDate()

        add_link_dictionary = {'referer' : None , 'header' : None  , 'user-agent' : None , 'load-cookies' : None , 'last_try_date' : now_date_list , 'firs_try_date' : now_date_list , 'out' : None , 'final_download_path':final_download_path , 'start_hour': None ,'start_minute' : None ,'end_hour' : None ,'end_minute': None , 'ip':ip , 'port':port , 'proxy_user':proxy_user , 'proxy_passwd' : proxy_passwd , 'download_user':download_user , 'download_passwd': download_passwd ,'connections':connections , 'limit':limit, 'download_path':download_path }

#finding checked links in links_table
        self.add_link_dictionary_list = []
        i = 0
        for row in range(self.links_table.rowCount()):
            item = self.links_table.item(row , 0 )
            if (item.checkState() == 2 ) :
                link = item.text()
                self.add_link_dictionary_list.append(add_link_dictionary.copy())
                self.add_link_dictionary_list[i]['link'] = str(link)
                i = i + 1

        self.add_link_dictionary_list.reverse()
        self.callback(self.add_link_dictionary_list , category)

        self.saveWindowSize()
        self.close()
 
    def saveWindowSize(self):
#finding last windows_size that saved in windows_size file
        windows_size = config_folder + '/windows_size'
        f = Open(windows_size)
        windows_size_file_lines = f.readlines()
        f.close()
        windows_size_dict_str = str(windows_size_file_lines[0].strip())
        windows_size_dict = ast.literal_eval(windows_size_dict_str) 

        
#getting current windows_size
        width = int(self.frameGeometry().width())
        height = int(self.frameGeometry().height())
#replacing current size with old size in window_size_dict
        windows_size_dict ['TextQueue_Ui'] = [ width , height ]
        f = Open(windows_size, 'w')
        f.writelines(str(windows_size_dict))
        f.close()


