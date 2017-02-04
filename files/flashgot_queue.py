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
from functools import partial
from PyQt5 import QtWidgets , QtCore , QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTableWidgetItem , QFileDialog
from PyQt5.QtCore import QPoint , QSize , QThread , pyqtSignal
from newopen import Open , readDict
import download
import ast , os 
import osCommands
import spider
import platform

os_type = platform.system()


class QueueSpiderThread(QThread):
    QUEUESPIDERRETURNEDFILENAME = pyqtSignal(str)
    def __init__(self,add_link_dictionary ):
        QThread.__init__(self)
        self.add_link_dictionary = add_link_dictionary

    def run(self):
        try :
            filename = spider.queueSpider(self.add_link_dictionary)
            self.QUEUESPIDERRETURNEDFILENAME.emit(filename)
        except :
            print("Spider couldn't find download information")


home_address = os.path.expanduser("~")

#config_folder
if os_type == 'Linux' or os_type == 'FreeBSD' :
    config_folder = os.path.join(str(home_address) , ".config/persepolis_download_manager")
elif os_type == 'Darwin':
    config_folder = os.path.join(str(home_address) , "Library/Application Support/persepolis_download_manager")
elif os_type == 'Windows' :
    config_folder = os.path.join(str(home_address) , 'AppData' , 'Local' , 'persepolis_download_manager')


queues_list_file = os.path.join(config_folder , 'queues_list')



class FlashgotQueue(TextQueue_Ui):
    def __init__(self , parent , flashgot_lines , callback , persepolis_setting ):
        super().__init__(persepolis_setting)
        self.persepolis_setting = persepolis_setting
        self.callback = callback
        self.parent = parent
        self.flashgot_lines = flashgot_lines

        global icons
        icons = ':/' + str(self.persepolis_setting.value('settings/icons')) + '/'

        self.flashgot_lines.reverse()
        
        k = 1
        for i in range(len(self.flashgot_lines)):
            flashgot_add_link_dictionary_str = flashgot_lines[i].strip()
            flashgot_add_link_dictionary = ast.literal_eval(flashgot_add_link_dictionary_str) 
            
            #adding row to links_table
            self.links_table.insertRow(0)

            # file_name
            if 'out' in flashgot_add_link_dictionary:
                file_name = str(flashgot_add_link_dictionary['out'])
            else:
                file_name = '***'
            #spider is finding file name
                new_spider = QueueSpiderThread(flashgot_add_link_dictionary )
                self.parent.threadPool.append(new_spider)
                self.parent.threadPool[len(self.parent.threadPool) - 1].start()
                self.parent.threadPool[len(self.parent.threadPool) - 1].QUEUESPIDERRETURNEDFILENAME.connect(partial(self.parent.queueSpiderCallBack , child = self , row_number = len(self.flashgot_lines) - k ))
            k = k + 1

            item = QTableWidgetItem(file_name)
            #adding checkbox to the item
            item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.Checked)


            #inserting file_name
            self.links_table.setItem(0 , 0 , item)


            #finding link
            link = str(flashgot_add_link_dictionary['link'])
            item = QTableWidgetItem(str(link))

            #inserting link 
            self.links_table.setItem(0 , 1 , item)

            #inserting add_link_dictionary
            item = QTableWidgetItem(flashgot_add_link_dictionary_str) 
            self.links_table.setItem(0 , 2 , item)

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

        global connections
        connections = int(self.persepolis_setting.value('settings/connections'))
        global download_path
        download_path = str(self.persepolis_setting.value('settings/download_path'))


#initialization
        self.connections_spinBox.setValue(connections)
        self.download_folder_lineEdit.setText(download_path)
        self.download_folder_lineEdit.setEnabled(False)

#ip_lineEdit initialization 
        settings_ip = self.persepolis_setting.value('add_link_initialization/ip' , None )
        if settings_ip :
            self.ip_lineEdit.setText(str(settings_ip))

#proxy user lineEdit initialization 
        settings_proxy_user = self.persepolis_setting.value('add_link_initialization/proxy_user' , None )
        if settings_proxy_user :
            self.proxy_user_lineEdit.setText(str(settings_proxy_user))

#port_spinBox initialization 
        settings_port = self.persepolis_setting.value('add_link_initialization/port' , 0 )
       
        self.port_spinBox.setValue(int(int(settings_port)))


#download UserName initialization
        settings_download_user = self.persepolis_setting.value('add_link_initialization/download_user' , None )
        if settings_download_user:
            self.download_user_lineEdit.setText(str(settings_download_user))


#connect folder_pushButton
        self.folder_pushButton.clicked.connect(self.changeFolder)

#connect OK and canel button

        self.cancel_pushButton.clicked.connect(self.close)
        self.ok_pushButton.clicked.connect(self.okButtonPressed) 

#connect select_all_pushButton  deselect_all_pushButton
        self.select_all_pushButton.clicked.connect(self.selectAll)

        self.deselect_all_pushButton.clicked.connect(self.deselectAll)


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

#setting window size and position
        size = self.persepolis_setting.value('TextQueue/size' , QSize(700 , 500))
        position = self.persepolis_setting.value('TextQueue/position' , QPoint(300 , 300))
        self.resize(size)
        self.move(position)


    def selectAll(self,button):
        for i in range(self.links_table.rowCount()):
            item = self.links_table.item(i , 0 )
            item.setCheckState(QtCore.Qt.Checked)

    def deselectAll(self,button):
        for i in range(self.links_table.rowCount()):
            item = self.links_table.item(i , 0 )
            item.setCheckState(QtCore.Qt.Unchecked)



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

        if fname:
            #Returns pathName with the '/' separators converted to separators that are appropriate for the underlying operating system.
            #On Windows, toNativeSeparators("c:/winnt/system32") returns "c:\winnt\system32".
            fname = QDir.toNativeSeparators(fname)
 
        if os.path.isdir(fname):
            self.download_folder_lineEdit.setText(fname)


    def okButtonPressed(self,button):
#writing user's input data to init file
        self.persepolis_setting.setValue('add_link_initialization/ip' , self.ip_lineEdit.text() )
        self.persepolis_setting.setValue('add_link_initialization/port' , self.port_spinBox.value())
        self.persepolis_setting.setValue('add_link_initialization/proxy_user' , self.proxy_user_lineEdit.text())
        self.persepolis_setting.setValue('add_link_initialization/download_user' , self.download_user_lineEdit.text() )

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


        now_date_list = download.nowDate()

        add_link_dictionary = {'referer' : None , 'header' : None  , 'user-agent' : None , 'load-cookies' : None , 'last_try_date' : now_date_list , 'firs_try_date' : now_date_list , 'out' : None , 'final_download_path': None , 'start_hour': None ,'start_minute' : None ,'end_hour' : None ,'end_minute': None , 'ip':ip , 'port':port , 'proxy_user':proxy_user , 'proxy_passwd' : proxy_passwd , 'download_user':download_user , 'download_passwd': download_passwd ,'connections':connections , 'limit':limit, 'download_path':download_path }

#finding checked links in links_table
        self.add_link_dictionary_list = []
        i = 0
        for row in range(self.links_table.rowCount()):
            item = self.links_table.item(row , 0 )
            if (item.checkState() == 2 ) :#it means item is checked
                link = self.links_table.item(row , 1).text()
                self.add_link_dictionary_list.append(add_link_dictionary.copy())
                self.add_link_dictionary_list[i]['link'] = str(link)

                flashgot_add_link_dictionary_str = self.links_table.item(row , 2).text()
                flashgot_add_link_dictionary = ast.literal_eval(flashgot_add_link_dictionary_str) 


                if not ('referer' in flashgot_add_link_dictionary) :
                    flashgot_add_link_dictionary['referer'] = None

                if not ('header' in flashgot_add_link_dictionary):
                    flashgot_add_link_dictionary['header'] = None


                if not('user-agent' in flashgot_add_link_dictionary):
                    flashgot_add_link_dictionary['user-agent'] = None

                if not('load-cookies' in flashgot_add_link_dictionary):
                    flashgot_add_link_dictionary['load-cookies'] = None
                    
                flashgot_add_link_dictionary['out'] = self.links_table.item(row , 0).text()

                for j in flashgot_add_link_dictionary.keys():
                    self.add_link_dictionary_list[i][j] = flashgot_add_link_dictionary[j]

                i = i + 1

        self.add_link_dictionary_list.reverse()
        self.callback(self.add_link_dictionary_list , category)

        self.close()
 

    def closeEvent(self , event):
        self.persepolis_setting.setValue('TextQueue/size' , self.size())
        self.persepolis_setting.setValue('TextQueue/position' , self.pos())
        self.persepolis_setting.sync()

        self.destroy()
