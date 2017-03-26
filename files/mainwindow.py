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
from functools import partial
import sys , ast
from PyQt5 import QtCore, QtGui, QtWidgets  
from PyQt5.QtWidgets import QApplication ,  QAction , QFileDialog , QSystemTrayIcon , QMenu , QTableWidgetItem , QApplication , QInputDialog , QMessageBox 
from PyQt5.QtGui import QIcon , QColor , QPalette , QStandardItem 
from PyQt5.QtCore import QCoreApplication , QRect , QSize , QPoint, QThread , pyqtSignal  , Qt
import os
from time import sleep
import random  
from after_download import AfterDownloadWindow 
from chromium_integration_window import ChromiumIntegrationWindow 
from text_queue import TextQueue
from flashgot_queue import FlashgotQueue
from addlink import AddLinkWindow
from properties import PropertiesWindow
from progress import ProgressWindow
import download
from mainwindow_ui import MainWindow_Ui
from newopen import Open , writeList , readList , readDict
from play import playNotification
from bubble import notifySend
from setting import PreferencesWindow
from about import AboutWindow
import icons_resource
import spider
import osCommands, logger
import platform
from copy import deepcopy
from shutdown import shutDown
#THIS FILE CREATES MAIN WINDOW

#The GID (or gid) is a key to manage each download. Each download will be assigned a unique GID.
#The GID is stored as 64-bit binary value in aria2. For RPC access, 
#it is represented as a hex string of 16 characters (e.g., 2089b05ecca3d829). 
#Normally, aria2 generates this GID for each download, but the user can specify GIDs manually


#shutdown_notification = 0 >> persepolis running , 1 >> persepolis is ready for close(closeEvent called) , 2 >> OK, let's close application!
global shutdown_notification
shutdown_notification = 0

# checking_flag : 0 >> normal situation ; 1 >> remove button or delete button pressed or sorting form viewMenu selected by user ; 2 >> check_download_info function is stopping until remove operation done ; 3 >> deleteFileAction is done it's job and It is called removeButtonPressed function
global checking_flag
checking_flag = 0
#when rpc connection between persepolis and aria is disconnected >> aria2_disconnected = 1
global aria2_disconnected
aria2_disconnected = 0

global aria_startup_answer
aria_startup_answer = 'None'


global button_pressed_counter
button_pressed_counter = 0

global flashgot_checked_links
flashgot_checked_links = False

home_address = os.path.expanduser("~")

#finding os platform
os_type = platform.system()

#persepolis tmp folder (temporary folder) 
if os_type != 'Windows':

    user_name_split = home_address.split('/')
    user_name = user_name_split[2]

    persepolis_tmp = '/tmp/persepolis_' + user_name
else:
    persepolis_tmp = os.path.join(str(home_address) , 'AppData','Local','persepolis_tmp')


#config_folder
if os_type == 'Linux' or os_type == 'FreeBSD'  or os_type == 'OpenBSD' :
    config_folder = os.path.join(str(home_address) , ".config/persepolis_download_manager")
elif os_type == 'Darwin':
    config_folder = os.path.join(str(home_address) , "Library/Application Support/persepolis_download_manager")
elif os_type == 'Windows' :
    config_folder = os.path.join(str(home_address) , 'AppData' , 'Local' , 'persepolis_download_manager')


download_info_folder = os.path.join(config_folder , "download_info")


#persepolis temporary download folder
if os_type != 'Windows':
    temp_download_folder = str(home_address) + '/.persepolis'
else :
    temp_download_folder = os.path.join(str(home_address) , 'AppData','Local','persepolis')


#download_list_file contains GID of all downloads
download_list_file = os.path.join(config_folder , "download_list_file")

#download_list_file_active for active downloads
download_list_file_active = os.path.join(config_folder , "download_list_file_active")

#queues_list contains queues name
queues_list_file = os.path.join(config_folder , 'queues_list' )

#category_folder contains some file , and every files named with queues . every file contains gid of downloads for that queue
category_folder = os.path.join(config_folder , 'category_folder')

#queue_info_folder is contains queues information(start time,end time,limit speed , ...)
queue_info_folder = os.path.join(config_folder , "queue_info")

#single_downloads_list_file contains gid of non categorised downloads
single_downloads_list_file = os.path.join(category_folder , "Single Downloads")

#see persepolis file for show_window_file and flashgot_ready and flashgot_file
flashgot_ready = os.path.join(persepolis_tmp , 'persepolis-flashgot-ready')

flashgot_file = os.path.join(persepolis_tmp , 'persepolis-flashgot' )

show_window_file = os.path.join(persepolis_tmp , 'show-window')

#starting aria2 when Persepolis starts
class StartAria2Thread(QThread):
    ARIA2RESPONDSIGNAL = pyqtSignal(str)
    def __init__(self):
        QThread.__init__(self)
        
    def run(self):
        #aria_startup_answer is None when Persepolis starts! and after ARIA2RESPONDSIGNAL emitting yes , then startAriaMessage function changing aria_startup_answer to 'Ready'
        global aria_startup_answer
        for i in range(5):
            answer = download.startAria()
            if answer == 'did not respond' and i != 4:
                signal_str = 'try again'
                self.ARIA2RESPONDSIGNAL.emit(signal_str)
                sleep(2)
            else :
                break

        #if Aria2 doesn't respond to Persepolis ,ARIA2RESPONDSIGNAL is emitting no  
        if answer == 'did not respond':
            signal_str = 'no'
        else :
            signal_str = 'yes'

        self.ARIA2RESPONDSIGNAL.emit(signal_str)


#This thread checking that which row in download_table highlited by user
class CheckSelectedRowThread(QThread):
    CHECKSELECTEDROWSIGNAL = pyqtSignal()
    def __init__(self):
        QThread.__init__(self)

    def run(self):
        while shutdown_notification == 0 and aria_startup_answer != 'ready':
            sleep (1)
        while shutdown_notification == 0:
            sleep(0.2)
            self.CHECKSELECTEDROWSIGNAL.emit()



class CheckDownloadInfoThread(QThread):
    DOWNLOAD_INFO_SIGNAL = pyqtSignal(str)
    def __init__(self):
        QThread.__init__(self)
    def run(self):
        global checking_flag
        global shutdown_notification
        while True:

            while shutdown_notification == 0 and aria_startup_answer != 'ready':
                sleep (1)

            while shutdown_notification != 1:
            #if checking_flag is equal to 1, it means that user pressed remove or delete button . so checking download information must stop until removing done!
                if checking_flag == 1 :
                    checking_flag = 2
                    while checking_flag != 0 :
                        sleep(0.2)
                sleep(0.1)
                f = Open(download_list_file_active) 
                download_list_file_active_lines = f.readlines()
                f.close()
                if len(download_list_file_active_lines) != 0 :
                    for line in download_list_file_active_lines:
                        gid = line.strip()
                        if checking_flag == 1 :
                            break
                        try:
                            answer = download.downloadStatus(gid)
                        except:
                            answer = 'None'
                        if answer == 'ready' :
                            sleep(0.2)
                            download_info_file = os.path.join(download_info_folder , gid)
                            if os.path.isfile(download_info_file) == True:
                                self.DOWNLOAD_INFO_SIGNAL.emit(gid)
            shutdown_notification = 2
            break                           
                                
                            
                        

#SpiderThread calls spider in spider.py . 
#spider finds file size and file name of download file .
#spider works similiar to spider in wget.
class SpiderThread(QThread):
    def __init__(self,add_link_dictionary , gid):
        QThread.__init__(self)
        self.add_link_dictionary = add_link_dictionary
        self.gid = gid

    def run(self):
        try :
            spider.spider(self.add_link_dictionary , self.gid)
        except :
            print("Spider couldn't find download information")
            logger.sendToLog("Spider couldn't find download information", "ERROR")

#this thread sending download request to aria2            
class DownloadLink(QThread):
    ARIA2NOTRESPOND = pyqtSignal()
    def __init__(self,gid):
        QThread.__init__(self)
        self.gid = gid

    def run(self):
        #if request is not successful then persepolis is checking rpc connection whith download.aria2Version() function
        answer = download.downloadAria(self.gid)
        if answer == 'None':
            version_answer = download.aria2Version()
            if version_answer == 'did not respond':
                self.ARIA2NOTRESPOND.emit()




#this thread managing queue and sending download request to aria2            
class Queue(QThread):
    #this signal emited when download status of queue changes to stop
    REFRESHTOOLBARSIGNAL = pyqtSignal(str)
    def __init__(self,category , start_hour , start_minute , end_hour , end_minute ,parent):
        QThread.__init__(self)
        self.category = str(category)
        self.parent = parent
        self.start_hour = start_hour
        self.start_minute = start_minute
        self.end_hour = end_minute
        self.end_minute = end_minute

    def run(self):
        self.start = True
        self.stop = False
        self.limit = False 
        self.limit_changed = False
        self.after = False
        self.break_for_loop = False

        queue_file = os.path.join(category_folder , self.category)

        for counter in range(5):#queue is repeating 5 times! and everty times load queue list again! It is helping for checking new downloads in queue and retrying failed downloads
        #getting list of gid in queue
            f = Open(queue_file)
            queue_file_lines = f.readlines()
            f.close()

            if not(self.parent.reverse_checkBox.isChecked()) :
                queue_file_lines.reverse()

            if self.start_hour != None and counter == 0: # checking that if user set start time
            #setting start time for first download in queue
            #finding gid of first download ! status of first download must be stopped or error but not compelete
                for index in range(len(queue_file_lines)):
                    first_download_gid = queue_file_lines[index].strip()

            #finding download_info_file
                    download_info_file = os.path.join(download_info_folder , first_download_gid)

            #reading download_info_file_list
                    download_info_file_list = readList(download_info_file)
                    
                    status = download_info_file_list [1]

                    if status != 'complete':

            #reading add_link_dictionary
                        add_link_dictionary = download_info_file_list[9]

            #setting start_hour and start_minute
                        add_link_dictionary['start_hour'] = self.start_hour
                        add_link_dictionary['start_minute'] = self.start_minute
                        download_info_file_list[9] = add_link_dictionary

            #writing on download_info_file
                        writeList(download_info_file , download_info_file_list)

                        break

            for line in queue_file_lines :
                gid = line.strip()

                download_info_file = os.path.join(download_info_folder , gid)

            #reading download_info_file_list
                download_info_file_list = readList(download_info_file)


                if str(download_info_file_list[1]) == 'complete': #if download was completed continues with the next iteration of the loop
                    continue

            #changing status of download to waiting
                status = 'waiting'
                download_info_file_list[1] = status 
          
                if self.end_hour != None :#it means user was set end time for download

                #reading add_link_dictionary 
                    add_link_dictionary = download_info_file_list[9]

                #setting end_hour and end_minute
                    add_link_dictionary['end_hour'] = self.end_hour
                    add_link_dictionary['end_minute'] = self.end_minute

                #writing changes to download_info_file_list
                    download_info_file_list[9] = add_link_dictionary


            #writing new download_info_file_list to download_info_file
                writeList(download_info_file , download_info_file_list)


            #starting new thread for download
                new_download = DownloadLink(gid)
                self.parent.threadPool.append(new_download)
                self.parent.threadPool[len(self.parent.threadPool) - 1].start()
                self.parent.threadPool[len(self.parent.threadPool) - 1].ARIA2NOTRESPOND.connect(self.parent.aria2NotRespond)
                sleep(3)

                while  status == 'downloading' or status == 'waiting' or status == 'paused' or status == 'scheduled' : #continue loop until download has finished

                    sleep(1)
                    try:
                        download_info_file_list = readList(download_info_file)
                        status = str(download_info_file_list[1])
                    except:
                        status = 'downloading'

                    if self.stop == True: #it means user stopped queue
                        answer = download.downloadStop(gid)
                    #if aria2 did not respond , then this function is checking for aria2 availability , and if aria2 disconnected then aria2Disconnected is executed 
                        if answer == 'None':
                            version_answer = download.aria2Version()
                            if version_answer == 'did not respond':
                                self.parent.aria2Disconnected()
                        status = 'stopped'

                    if self.limit == True and status == 'downloading' and self.limit_changed == True   : #It means user want to limit download speed
                    #getting limitation value
                        self.limit_comboBox_value = self.parent.limit_comboBox.currentText()
                        self.limit_spinBox_value = self.parent.limit_spinBox.value()
                        if self.limit_comboBox_value == "KB/S" :
                            limit = str(self.limit_spinBox_value) + str("K")
                        else :
                            limit = str(self.limit_spinBox_value) + str("M")
                    #applying limitation
                        download.limitSpeed(gid , limit)

                    #done!
                        self.limit_changed = False

                    if self.limit == False and status == 'downloading' and  self.limit_changed == True: #limiting speed is canceled by user!
                    #applying limitation
                        download.limitSpeed(gid , "0")

                    #done!
                        self.limit_changed = False


                if status == 'stopped': #it means queue stopped at end time or user stopped queue 
    
                    if self.stop == True and self.after == True : #It means user activated shutdown before and now user stopped queue . so after download must be canceled
                        self.parent.after_checkBox.setChecked(False)

                    self.stop = True
                    self.limit = False
                    self.limit_changed = False
                    self.break_for_loop = True #it means that break outer for loop

                    if str(self.parent.category_tree.currentIndex().data()) == str(self.category) :
                        self.REFRESHTOOLBARSIGNAL.emit(self.category)

        #showing notification
                    notifySend("Persepolis" , "Queue Stopped!", 10000 , 'no', systemtray = self.parent.system_tray_icon )

                    break
               

            if self.break_for_loop :
                break


        if self.start == True : #if queue finished
            self.start = False
#this section is sending shutdown signal to the shutdown script(if user select shutdown for after download)
            if self.after == True: 
                answer = download.shutDown()
#KILL aria2c if didn't respond
                if (answer == 'error') and (os_type != 'Windows'):
                    os.system('killall aria2c')

                shutdown_file = os.path.join(persepolis_tmp , 'shutdown' , self.category )
                f = Open( shutdown_file , 'w')
                notifySend('Persepolis is shutting down','your system in 20 seconds' , 15000 ,'warning', systemtray = self.parent.system_tray_icon )
                f.writelines('shutdown')
                f.close()

            notifySend("Persepolis" , 'Queue completed!'  , 10000 , 'queue' , systemtray = self.parent.system_tray_icon )
            self.stop = True
            self.limit = False
            self.limit_changed = False
            self.after = False
            if str(self.parent.category_tree.currentIndex().data()) == str(self.category) :
                self.REFRESHTOOLBARSIGNAL.emit(self.category)



 
#CheckingThread have 3 duty!        
#1-this class is checking that if user called flashgot .
#2-assume that user executed program before . if user is clicking on persepolis icon in menu this tread emits SHOWMAINWINDOWSIGNAL
#3-this class is checking aria2 rpc connection! if aria rpc is not availabile , this class restarts aria!
class CheckingThread(QThread):
    CHECKFLASHGOTSIGNAL = pyqtSignal()
    SHOWMAINWINDOWSIGNAL = pyqtSignal()
    RECONNECTARIASIGNAL = pyqtSignal(str)
    def __init__(self):
        QThread.__init__(self)

    def run(self):
        global shutdown_notification
        global aria2_disconnected
        global flashgot_checked_links
        while shutdown_notification == 0 and aria_startup_answer != 'ready':
            sleep (2)
        j = 0
        while shutdown_notification == 0:


            if os.path.isfile( show_window_file ) == True: #it means , user clicked on persepolis icon and persepolis is still running. see persepolis file for more details.
                osCommands.remove(show_window_file)
                self.SHOWMAINWINDOWSIGNAL.emit()

            sleep(1)

            if os.path.isfile(flashgot_ready)  == True :#It means new flashgot call is available!
                size = 0
                #This loop check that is size of persepolis-flashgot changed or not.
                #if it's changed , we have queue request and loop waits until all links inserted in persepolis-flashgot file

                while size != os.path.getsize(flashgot_file):
                    size =  os.path.getsize(flashgot_file)
                    sleep(0.3) 


                #When checkFlashgot method considered request , then flashgot_checked_links is changed to True
                flashgot_checked_links = False
                self.CHECKFLASHGOTSIGNAL.emit()#notifiying that we have flashgot request 
                while flashgot_checked_links != True :#wait for persepolis consideration!                   
                    sleep(0.5) 
                
             
            j = j + 1
#every 39 seconds
            if j == 39 or aria2_disconnected == 1 : 
                j = 0
                aria2_disconnected = 0
                answer = download.aria2Version() #checking aria2 availability by aria2Version function
                if answer == 'did not respond':
                    for i in range(5):
                        answer = download.startAria() #starting aria2
                        if answer == 'did not respond' and i != 4: # checking answer
                            sleep(2)
                        else :
                            break
                    self.RECONNECTARIASIGNAL.emit(str(answer))  #emitting answer , if answer is 'did not respond' , it means that reconnecting aria was not successful         
 



#if checking_flag is equal to 1, it means that user pressed remove or delete button or ... . so checking download information must be stopped until job is done!
#this thread checks checking_flag and when checking_flag changes to 2 QTABLEREADY signal is emmited
class WaitThread(QThread):
    QTABLEREADY = pyqtSignal()
    def __init__(self):
        QThread.__init__(self)

    def run(self):
        global checking_flag
        checking_flag = 1
        while checking_flag != 2 :
            sleep(0.05)
        self.QTABLEREADY.emit()

#button_pressed_counter changed if user pressed move up and move down and ... actions
#this thread is changing checking_flag to zero if button_pressed_counter don't change for 2 seconds
class ButtonPressedThread(QThread):
    def __init__(self):
        QThread.__init__(self)

    def run(self):
        global checking_flag
        current_button_pressed_value = deepcopy(button_pressed_counter) + 1 
        while current_button_pressed_value != button_pressed_counter :
            current_button_pressed_value = deepcopy(button_pressed_counter) 
            sleep(2)
#job is done!
        checking_flag = 0


class ShutDownThread(QThread):
    def __init__(self , gid , password = None):
        QThread.__init__(self)
        self.gid = gid
        self.password = password

    def run(self):
        shutDown(self.gid , self.password)

  
 
class MainWindow(MainWindow_Ui):
    def __init__(self , start_in_tray , persepolis_main , persepolis_setting):
        super().__init__(persepolis_setting)
        self.persepolis_setting = persepolis_setting
        self.persepolis_main = persepolis_main
        global icons
        icons = ':/' + str(self.persepolis_setting.value('settings/icons')) + '/'


#system_tray_icon
        self.system_tray_icon = QSystemTrayIcon() 
        self.system_tray_icon.setIcon(QIcon.fromTheme('persepolis',QIcon(':/icon.svg') ))
        system_tray_menu = QMenu()
        system_tray_menu.addAction(self.addlinkAction)
        system_tray_menu.addAction(self.stopAllAction)
        system_tray_menu.addAction(self.minimizeAction)
        system_tray_menu.addAction(self.exitAction)
        self.system_tray_icon.setContextMenu(system_tray_menu)
        self.system_tray_icon.activated.connect(self.systemTrayPressed)
        self.system_tray_icon.show()
        self.trayAction.setChecked(True)
        self.system_tray_icon.setToolTip('Persepolis Download Manager')

        if self.persepolis_setting.value('settings/tray-icon') != 'yes' and start_in_tray == 'no' : 
            self.minimizeAction.setEnabled(False)
            self.trayAction.setChecked(False)
            self.system_tray_icon.hide()
        if start_in_tray == 'yes':
            self.minimizeAction.setText('Show main Window')
            self.minimizeAction.setIcon(QIcon(icons + 'window'))

        if self.persepolis_setting.value('settings/show-menubar') == 'yes':
            self.menubar.show()
            self.showMenuBarAction.setChecked(True)
            self.toolBar2.hide()
        else:
            self.menubar.hide()
            self.showMenuBarAction.setChecked(False)
            self.toolBar2.show()

        if platform.system() == 'Darwin':
            self.showMenuBarAction.setEnabled(False)

        if self.persepolis_setting.value('settings/show-sidepanel') == 'yes':
            self.category_tree_qwidget.show()
            self.showSidePanelAction.setChecked(True)
        else:
            self.category_tree_qwidget.hide()
            self.showSidePanelAction.setChecked(False)


#statusbar
        self.statusbar.showMessage('Please Wait ...')
        self.checkSelectedRow()


#threads     
        self.threadPool=[]
#starting aria
        start_aria = StartAria2Thread()
        self.threadPool.append(start_aria)
        self.threadPool[0].start() 
        self.threadPool[0].ARIA2RESPONDSIGNAL.connect(self.startAriaMessage)

#initializing    
#add queues to category_tree
        f = Open(queues_list_file)
        queues_list = f.readlines()
        f.close()
        for line in queues_list :
            queue_name = line.strip()
            new_queue_category = QStandardItem(queue_name)
            font = QtGui.QFont()
            font.setBold(True)
            new_queue_category.setFont(font)
            new_queue_category.setEditable(False)
            self.category_tree_model.appendRow(new_queue_category)

            #queue_info_file contains start time and end time information and ... for queue
            #queue_info_file path
            queue_info_file = os.path.join(queue_info_folder , queue_name)
            osCommands.touch(queue_info_file)

            #checking queue_info_file for all queues
            try :
                queue_info_dict = readDict(queue_info_file)
            except: #using default queue_info_dict if any error occured!
                #default queue_info_dict
                queue_info_dict = {'start_time_enable' : 'no' , 'end_time_enable' : 'no' , 'start_minute' : '0' , 'start_hour' : '0' , 'end_hour': '0' , 'end_minute' : '0' , 'reverse' : 'no' , 'limit_speed' : 'yes' , 'limit' : '0K' , 'after' : 'yes' }
                
            #changing start_time_enable , end_time_enable , reverse , limit_speed , after to no !
            for i in ['start_time_enable' , 'end_time_enable' , 'reverse' , 'limit_speed' , 'after' ]:
                queue_info_dict[str(i)] = 'no' 

            f = Open(queue_info_file , 'w' )
            f.writelines(str(queue_info_dict))
            f.close()

 


#add downloads to the download_table
        f_download_list_file = Open(download_list_file)
        download_list_file_lines = f_download_list_file.readlines()
        f_download_list_file.close()
            
        for line in download_list_file_lines:
            gid = line.strip()
            self.download_table.insertRow(0)
            download_info_file = os.path.join(download_info_folder , gid)
            download_info_file_list = readList(download_info_file,'string')
            for i in range(13):
                item = QTableWidgetItem(download_info_file_list[i])
                self.download_table.setItem(0 , i , item)

        row_numbers = self.download_table.rowCount()
        for row in range(row_numbers):
            status = self.download_table.item(row , 1).text() 
            if (status != "complete" and status != "error"):
                gid = self.download_table.item(row,8).text() 
                add_link_dictionary_str = self.download_table.item(row,9).text() 
                add_link_dictionary = ast.literal_eval(add_link_dictionary_str.strip()) 
                add_link_dictionary['start_hour'] = None
                add_link_dictionary['start_minute'] = None
                add_link_dictionary['end_hour'] = None
                add_link_dictionary['end_minute'] = None
                add_link_dictionary['after_download'] = 'None'

                download_info_file = os.path.join(download_info_folder , gid)
                download_info_file_list = readList(download_info_file,'string')

                for i in range(13):
                    if i == 1 :
                        download_info_file_list[i] = 'stopped'
                        item = QTableWidgetItem('stopped')
                        self.download_table.setItem(row , i , item )
                download_info_file_list[9] = add_link_dictionary
                writeList(download_info_file , download_info_file_list)

#defining some lists and dictionaries for runinng addlinkwindows and propertieswindows and propertieswindows , ...
        self.addlinkwindows_list = []
        self.propertieswindows_list = []
        self.progress_window_list = []
        self.afterdownload_list = []
        self.text_queue_window_list = []
        self.about_window_list = []
        self.flashgot_queue_window_list = []
        self.browser_integration_window_list = []
        self.progress_window_list_dict = {}
#queue_list_dict contains queue threads >> queue_list_dict[name of queue] = Queue(name of queue , parent)
        self.queue_list_dict = {}

#CheckDownloadInfoThread
        check_download_info = CheckDownloadInfoThread()
        self.threadPool.append(check_download_info)
        self.threadPool[1].start()
        self.threadPool[1].DOWNLOAD_INFO_SIGNAL.connect(self.checkDownloadInfo)

#CheckSelectedRowThread
        check_selected_row = CheckSelectedRowThread()
        self.threadPool.append(check_selected_row)
        self.threadPool[2].start()
        self.threadPool[2].CHECKSELECTEDROWSIGNAL.connect(self.checkSelectedRow)

#CheckingThread
        check_flashgot = CheckingThread()
        self.threadPool.append(check_flashgot)
        self.threadPool[3].start()
        self.threadPool[3].CHECKFLASHGOTSIGNAL.connect(self.checkFlashgot)
        self.threadPool[3].SHOWMAINWINDOWSIGNAL.connect(self.showMainWindow)
        self.threadPool[3].RECONNECTARIASIGNAL.connect(self.reconnectAria)


#if user  doubleclicks on an item in download_table , then openFile function  executes
        self.download_table.itemDoubleClicked.connect(self.openFile)

#connecting queue_panel_show_button to showQueuePanelOptions
        self.queue_panel_show_button.clicked.connect(self.showQueuePanelOptions)

#connecting start_checkBox to startFrame
        self.start_checkBox.toggled.connect(self.startFrame)
#         self.startFrame('menu')
        self.start_checkBox.setChecked(False)

#connecting end_checkBox to endFrame
        self.end_checkBox.toggled.connect(self.endFrame)
#         self.endFrame('menu')
        self.end_checkBox.setChecked(False)

#connecting after_checkBox to afterFrame
        self.after_checkBox.toggled.connect(self.afterFrame)
        self.after_checkBox.setChecked(False)

#connecting limit_checkBox to limitFrame
        self.limit_checkBox.toggled.connect(self.limitFrame)

#connecting limit_pushButton to limitPushButtonPressed
        self.limit_pushButton.clicked.connect(self.limitPushButtonPressed)

#connecting limit_comboBox and limit_spinBox to limitComboBoxChanged
        self.limit_comboBox.currentIndexChanged.connect(self.limitComboBoxChanged)
        self.limit_spinBox.valueChanged.connect(self.limitComboBoxChanged)

#connecting after_pushButton to afterPushButtonPressed
        self.after_pushButton.clicked.connect(self.afterPushButtonPressed)

#setting index of all downloads for category_tree
        global current_category_tree_index
        current_category_tree_index = self.category_tree_model.index(0,0)
        self.category_tree.setCurrentIndex(current_category_tree_index)

#this line set toolBar And Context Menu Items
        self.toolBarAndContextMenuItems('All Downloads')

        self.category_tree_qwidget.setEnabled(False) #It will be enabled after aria2 startup!(see startAriaMessage method) .This line added for solving crash problems on startup


#finding windows_size
        size = self.persepolis_setting.value('MainWindow/size' , QSize(900 , 500) ) 
        position = self.persepolis_setting.value('MainWindow/position' , QPoint(300 , 300) )
#setting window size
        self.resize(size)
        self.move(position)

#check reverse_checkBox
        self.reverse_checkBox.setChecked(False)

# startAriaMessage function is showing some message on statusbar and sending notification when aria failed to start! see StartAria2Thread for more details
    def startAriaMessage(self,message):
        global aria_startup_answer
        if message == 'yes':
            sleep (0.5)
            self.statusbar.showMessage('Ready...')
            aria_startup_answer = 'ready'

            self.category_tree_qwidget.setEnabled(True)


        elif message == 'try again':
            self.statusbar.showMessage("Aria2 didn't respond! be patient!Persepolis tries again in 2 seconds!")
        else:
            self.statusbar.showMessage('Error...')
            notifySend('Persepolis can not connect to Aria2' , 'Check your network & Restart Persepolis' ,10000,'critical' , systemtray = self.system_tray_icon )
            self.propertiesAction.setEnabled(True)

            self.category_tree_qwidget.setEnabled(True)


    def reconnectAria(self,message):
        #this function is executing if RECONNECTARIASIGNAL is emitted by CheckingThread . 
        #if message is 'did not respond' then a message(Persepolis can not connect to Aria2) shown 
        #if message is not 'did not respond' , it means that reconnecting Aria2 was successful. 
        if message == 'did not respond' : 
            self.statusbar.showMessage('Error...')
            notifySend('Persepolis can not connect to Aria2' , 'Restart Persepolis' ,10000,'critical' , systemtray = self.system_tray_icon )
        else:
            self.statusbar.showMessage('Reconnecting aria2...')
            #this section is checking download status of items in download table , if status is downloading then restarting this download.
            for row in range(self.download_table.rowCount()):
                status_download_table = str(self.download_table.item( row , 1 ).text())
                gid = self.download_table.item( row , 8).text()
                if status_download_table == 'downloading': 
                    new_download = DownloadLink(gid)
                    self.threadPool.append(new_download)
                    self.threadPool[len(self.threadPool) - 1].start()
                    self.threadPool[len(self.threadPool) - 1].ARIA2NOTRESPOND.connect(self.aria2NotRespond)
            #if status is paused , then this section is stopping download.
                if status_download_table == 'paused':
                    download.downloadStop(gid)

            self.statusbar.showMessage('Persepolis reconnected aria2 successfully') 

#when this function is called , aria2_disconnected value is changing to 1! and it means that aria2 rpc connection disconnected.so CheckingThread is trying to fix it .          
    def aria2Disconnected(self):
        global aria2_disconnected
        aria2_disconnected = 1

    def checkDownloadInfo(self,gid):

#get download information from download_info_file according to gid and write them in download_table cells
        download_info_file = os.path.join(config_folder , "download_info" , gid)
        #check information validation
        try:
            download_info_file_list = readList(download_info_file)
            if len(download_info_file_list) == 13:
                file_validation = True
        except:
            file_validation = False

        if file_validation :
            download_info_file_list_string = download_info_file_list[:] 
            download_info_file_list_string[9] = str(download_info_file_list_string [9])

#if download completed , then the GID of download must removed from download_list_file_active
            status = str(download_info_file_list[1])
            if status == "complete":
                f = Open(download_list_file_active)
                download_list_file_active_lines = f.readlines()
                f.close()
                f = Open(download_list_file_active , "w")
                for line in download_list_file_active_lines :
                    if line.strip() != gid :
                        f.writelines(line.strip() + "\n")
                f.close()
 
#finding row of this gid!
            row = None
            for i in range(self.download_table.rowCount()):
                row_gid = self.download_table.item(i , 8).text()
                if gid == row_gid :
                    row = i 
                    break

#checking that if user checked selection mode from edit menu
            if self.selectAction.isChecked() == True :
                selection = 'actived'
            else:
                selection = None

#updating download_table items
            if row != None :
                for i in range(12):
#update download_table cells
                    item = QTableWidgetItem(download_info_file_list_string[i])

#adding checkbox to first cell in row , if user checked selection mode
                    if i == 0 and selection != None :
                        item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                        if self.download_table.item(row , i).checkState() == 2:
                            item.setCheckState(QtCore.Qt.Checked) #if user checked row before , check it again 
                        else:
                            item.setCheckState(QtCore.Qt.Unchecked) #if user didn't checked row then don't check it!
#setting item
                    try :
                        self.download_table.setItem(row , i , item)
                    except Exception as problem:
                        print('updating download_table was unsuccessful\nError is :' )
                        print (problem)
                        logger.sendToLog("Error occured while updating download table", "INFO")
                        logger.sendToLog(problem, "ERROR")
#updating download_table (refreshing!)
                self.download_table.viewport().update()
#update progresswindow

            if gid in self.progress_window_list_dict.keys(): #checking that progress_window availability
#finding progress_window for gid            
                member_number = self.progress_window_list_dict[gid]
                progress_window = self.progress_window_list[member_number]
                #link
                add_link_dictionary = download_info_file_list[9]
                link = "<b>Link</b> : " +  str(add_link_dictionary ['link'])
                progress_window.link_label.setText(link)
                progress_window.link_label.setToolTip(link)

                #Save as
                final_download_path = add_link_dictionary['final_download_path']
                if final_download_path == None : #It means that download didn't start yet
                    final_download_path = str(add_link_dictionary['download_path'])
                        
                save_as = "<b>Save as</b> : " + os.path.join(final_download_path , str(download_info_file_list[0]))
                progress_window.save_label.setText(save_as)
                progress_window.save_label.setToolTip(save_as)

                #status
                progress_window.status = download_info_file_list[1]
                status = "<b>Status</b> : " + progress_window.status 
                progress_window.status_label.setText(status)

                #activing/deactiving progress_window buttons according to status
                if progress_window.status == "downloading":
                    progress_window.resume_pushButton.setEnabled(False)
                    progress_window.stop_pushButton.setEnabled(True)
                    progress_window.pause_pushButton.setEnabled(True)

                elif progress_window.status == "paused":
                    progress_window.resume_pushButton.setEnabled(True)
                    progress_window.stop_pushButton.setEnabled(True)
                    progress_window.pause_pushButton.setEnabled(False)

                elif progress_window.status == "waiting":
                    progress_window.resume_pushButton.setEnabled(False)
                    progress_window.stop_pushButton.setEnabled(True)
                    progress_window.pause_pushButton.setEnabled(False)

                elif progress_window.status == "scheduled":
                    progress_window.resume_pushButton.setEnabled(False)
                    progress_window.stop_pushButton.setEnabled(True)
                    progress_window.pause_pushButton.setEnabled(False)

                elif progress_window.status == "stopped" or progress_window.status == "error" or progress_window.status == "complete" : #it means download has finished!
#close progress_window if download status is stopped or completed or error
                    progress_window.destroy() #close window!

                    #eliminating window information! in progress_window_list and progress_window_list_dict
                    self.progress_window_list[member_number] = []
                    del self.progress_window_list_dict[gid]

                    if progress_window.status == "stopped":
                        #showing notification
                        notifySend("Download Stopped" , str(download_info_file_list[0]) , 10000 , 'no', systemtray = self.system_tray_icon )

                    elif progress_window.status == "error":
                        #showing notification
                        notifySend("Error - " + add_link_dictionary['error'] , str(download_info_file_list[0]) , 10000 , 'fail', systemtray = self.system_tray_icon )
            
                        #setting start_hour and start_minute and end_hour and end_minute to None and writing it to download_info_file,because download has finished
                        add_link_dictionary['start_hour'] = None
                        add_link_dictionary['start_minute'] = None
                        add_link_dictionary['end_hour'] = None
                        add_link_dictionary['end_minute'] = None
                        add_link_dictionary['after_download'] = 'None'
    
                        for i in range(12):
                            if i == 9 :
                                download_info_file_list[i] = add_link_dictionary
                            
                        download_info_file_list[9] = add_link_dictionary 
                        writeList(download_info_file , download_info_file_list )


#this section is sending shutdown signal to the shutdown script(if user select shutdown for after download)
                    shutdown_file = os.path.join( persepolis_tmp , 'shutdown' , gid )
                    if os.path.isfile(shutdown_file) == True and progress_window.status != 'stopped':
                        answer = download.shutDown()
#KILL aria2c if didn't respond
                        if (answer == 'error') and (os_type != 'Windows'):
                            os.system('killall aria2c')
                        f = Open(shutdown_file, 'w')
                        notifySend('Persepolis is shutting down','your system in 20 seconds' , 15000 ,'warning', systemtray = self.system_tray_icon )
                        f.writelines('shutdown')
                        f.close()
                    elif os.path.isfile(shutdown_file ) == True and progress_window.status == 'stopped':
                        f = Open( shutdown_file , 'w')
                        f.writelines('canceled')
                        f.close()

#showing download compelete dialog
#check user's Preferences
                    self.persepolis_setting.sync()
                    if progress_window.status == "complete" :
                        if self.persepolis_setting.value('settings/after-dialog') == 'yes' :
                            afterdownloadwindow = AfterDownloadWindow(download_info_file_list,self.persepolis_setting)
                            self.afterdownload_list.append(afterdownloadwindow)
                            self.afterdownload_list[len(self.afterdownload_list) - 1].show()
                            self.afterdownload_list[len(self.afterdownload_list) - 1].raise_()

                        else :
                            notifySend("Download Complete" ,str(download_info_file_list[0])  , 10000 , 'ok' , systemtray = self.system_tray_icon )



             
                #downloaded
                downloaded = "<b>Downloaded</b> : " + str(download_info_file_list[3]) + "/" + str(download_info_file_list[2])
                progress_window.downloaded_label.setText(downloaded)

                #Transfer rate
                rate = "<b>Transfer rate</b> : " + str(download_info_file_list[6])
                progress_window.rate_label.setText(rate)

                #Estimate time left
                estimate_time_left = "<b>Estimate time left</b> : " + str(download_info_file_list[7]) 
                progress_window.time_label.setText(estimate_time_left)

                #Connections
                connections = "<b>Connections</b> : " + str(download_info_file_list[5])
                progress_window.connections_label.setText(connections)


                #progressbar
                value = download_info_file_list[4]
                file_name = str(download_info_file_list[0])
                if file_name != "***":
                    windows_title = '(' + str(value) + ')' +  str(file_name)
                    progress_window.setWindowTitle(windows_title) 

                try:
                    value = int(value[:-1])
                except:
                    value = 0
                progress_window.download_progressBar.setValue(value)


                   

#drag and drop for links
    def dragEnterEvent(self, droplink):

        text = str(droplink.mimeData().text())
      
        if ("tp:/" in text[2:6]) or ("tps:/" in text[2:7]) :
            droplink.accept()
        else:
            droplink.ignore() 

    def dropEvent(self, droplink):
        link_clipborad = QApplication.clipboard()
        link_clipborad.clear(mode=link_clipborad.Clipboard )
        link_string = droplink.mimeData().text() 
        link_clipborad.setText(str(link_string), mode=link_clipborad.Clipboard) 
        self.addLinkButtonPressed(button =link_clipborad )
    
	
    def gidGenerator(self):
        my_gid = hex(random.randint(1152921504606846976,18446744073709551615))
        my_gid = my_gid[2:18]
        my_gid = str(my_gid)
        f = Open(download_list_file_active)
        active_gid_list = f.readlines()
        f.close()
        while my_gid in active_gid_list :
            my_gid = self.gidGenerator()
        active_gids = download.activeDownloads()
        while my_gid in active_gids:
            my_gid = self.gidGenerator()
        
        return my_gid

    def selectedRow(self):
        try:
            item = self.download_table.selectedItems()
            selected_row_return = self.download_table.row(item[1]) 
            download_info = self.download_table.item(selected_row_return , 9).text()
            download_info = ast.literal_eval(download_info) 
            link = download_info['link']
            self.statusbar.showMessage(str(link))

        except :
            selected_row_return = None

        return selected_row_return 

    def checkSelectedRow(self):
        try:
            item = self.download_table.selectedItems()
            selected_row_return = self.download_table.row(item[1]) 
        except :
            selected_row_return = None

        if selected_row_return != None :
            status = self.download_table.item(selected_row_return , 1).text() 
            category = self.download_table.item(selected_row_return , 12).text()
            
            if category == 'Single Downloads':
                if status == "scheduled":
                    self.resumeAction.setEnabled(False)
                    self.pauseAction.setEnabled(False)
                    self.stopAction.setEnabled(True)
                    self.removeAction.setEnabled(False)
                    self.propertiesAction.setEnabled(False)
                    self.progressAction.setEnabled(True)
                    self.openDownloadFolderAction.setEnabled(False)
                    self.openFileAction.setEnabled(False)            
                    self.deleteFileAction.setEnabled(False)

                elif status == "stopped" or status == "error" :
                    self.stopAction.setEnabled(False)
                    self.pauseAction.setEnabled(False)
                    self.resumeAction.setEnabled(True)
                    self.removeAction.setEnabled(True)
                    self.propertiesAction.setEnabled(True)
                    self.progressAction.setEnabled(False)
                    self.openDownloadFolderAction.setEnabled(False)
                    self.openFileAction.setEnabled(False)            
                    self.deleteFileAction.setEnabled(False)



                elif status == "downloading":
                    self.resumeAction.setEnabled(False)
                    self.pauseAction.setEnabled(True)
                    self.stopAction.setEnabled(True)
                    self.removeAction.setEnabled(False)
                    self.propertiesAction.setEnabled(False)
                    self.progressAction.setEnabled(True)
                    self.openDownloadFolderAction.setEnabled(False)
                    self.openFileAction.setEnabled(False)            
                    self.deleteFileAction.setEnabled(False)



                elif status == "waiting": 
                    self.stopAction.setEnabled(True)
                    self.resumeAction.setEnabled(False)
                    self.pauseAction.setEnabled(False)
                    self.removeAction.setEnabled(False)
                    self.propertiesAction.setEnabled(False)
                    self.progressAction.setEnabled(True)
                    self.openDownloadFolderAction.setEnabled(False)
                    self.openFileAction.setEnabled(False)            
                    self.deleteFileAction.setEnabled(False)



                elif status == "complete":
                    self.stopAction.setEnabled(False)
                    self.resumeAction.setEnabled(False)
                    self.pauseAction.setEnabled(False)
                    self.removeAction.setEnabled(True)
                    self.propertiesAction.setEnabled(True)
                    self.progressAction.setEnabled(False)
                    self.openDownloadFolderAction.setEnabled(True)
                    self.openFileAction.setEnabled(True)            
                    self.deleteFileAction.setEnabled(True)



                elif status == "paused":
                    self.stopAction.setEnabled(True)
                    self.resumeAction.setEnabled(True)
                    self.pauseAction.setEnabled(False)
                    self.removeAction.setEnabled(False)
                    self.propertiesAction.setEnabled(False)
                    self.progressAction.setEnabled(True)
                    self.openDownloadFolderAction.setEnabled(False)
                    self.openFileAction.setEnabled(False)            
                    self.deleteFileAction.setEnabled(False)


              
 
                else:
                    self.progressAction.setEnabled(False)
                    self.resumeAction.setEnabled(False)
                    self.stopAction.setEnabled(False)
                    self.pauseAction.setEnabled(False)
                    self.removeAction.setEnabled(False)
                    self.propertiesAction.setEnabled(False)
                    self.openDownloadFolderAction.setEnabled(False)
                    self.openFileAction.setEnabled(False)            
                    self.deleteFileAction.setEnabled(False)

            else:

                if status == 'complete': 
                    self.stopAction.setEnabled(False)
                    self.resumeAction.setEnabled(False)
                    self.pauseAction.setEnabled(False)
                    self.removeAction.setEnabled(True)
                    self.propertiesAction.setEnabled(True)
                    self.progressAction.setEnabled(False)
                    self.openDownloadFolderAction.setEnabled(True)
                    self.openFileAction.setEnabled(True)            
                    self.deleteFileAction.setEnabled(True)

                elif status == "stopped" or status == "error" :
                    self.stopAction.setEnabled(False)
                    self.pauseAction.setEnabled(False)
                    self.resumeAction.setEnabled(False)
                    self.removeAction.setEnabled(True)
                    self.propertiesAction.setEnabled(True)
                    self.progressAction.setEnabled(False)
                    self.openDownloadFolderAction.setEnabled(False)
                    self.openFileAction.setEnabled(False)            
                    self.deleteFileAction.setEnabled(False)

                elif status == "scheduled" or status == "downloading" or status == "paused" or status == "waiting":
                    self.resumeAction.setEnabled(False)
                    self.pauseAction.setEnabled(False)
                    self.stopAction.setEnabled(False)
                    self.removeAction.setEnabled(False)
                    self.propertiesAction.setEnabled(False)
                    self.progressAction.setEnabled(False)
                    self.openDownloadFolderAction.setEnabled(False)
                    self.openFileAction.setEnabled(False)            
                    self.deleteFileAction.setEnabled(False)




        else:
            self.progressAction.setEnabled(False)
            self.resumeAction.setEnabled(False)
            self.stopAction.setEnabled(False)
            self.pauseAction.setEnabled(False)
            self.removeAction.setEnabled(False)
            self.propertiesAction.setEnabled(False)
            self.openDownloadFolderAction.setEnabled(False)
            self.openFileAction.setEnabled(False)            
            self.deleteFileAction.setEnabled(False)

        

#when new user requests download with flashgot , this method called           
    def checkFlashgot(self):
        global flashgot_checked_links
        #this lines extract add_link_dictionary from persepolis-flashgot
        f = Open(flashgot_file)
        flashgot_lines = f.readlines()
        f.close()

        #job is done! remove files!
        f.remove() 
        osCommands.remove(flashgot_ready)

        flashgot_checked_links = True #notifiying that job is done!and links are extracted flashgot_file

        if len(flashgot_lines) == 1 : #It means we have only one request from flashgot
            flashgot_add_link_dictionary_str = flashgot_lines[0].strip()
            flashgot_add_link_dictionary = ast.literal_eval(flashgot_add_link_dictionary_str) 

            #this line calls flashgotAddLink method with flashgot_add_link_dictionary
            self.flashgotAddLink(flashgot_add_link_dictionary)

        else: #we have queue request from flashgot
            self.flashgotQueue(flashgot_lines)

#this method creates an addlinkwindow when user calls Persepolis whith flashgot (Single Download)
    def flashgotAddLink(self,flashgot_add_link_dictionary):
        addlinkwindow = AddLinkWindow(self.callBack , self.persepolis_setting , flashgot_add_link_dictionary)
        self.addlinkwindows_list.append(addlinkwindow)
        self.addlinkwindows_list[len(self.addlinkwindows_list) - 1].show()
        self.addlinkwindows_list[len(self.addlinkwindows_list) - 1].raise_()


#This method creates addlinkwindow when user presses plus button in MainWindow
    def addLinkButtonPressed(self ,button):
        addlinkwindow = AddLinkWindow( self.callBack , self.persepolis_setting)
        self.addlinkwindows_list.append(addlinkwindow)
        self.addlinkwindows_list[len(self.addlinkwindows_list) - 1].show()

#callback of AddLinkWindow
    def callBack(self , add_link_dictionary , download_later , category):
        category = str(category)
        #aria2 identifies each download by the ID called GID. The GID must be hex string of 16 characters.
        gid = self.gidGenerator()

	#download_info_file_list is a list that contains ['file_name' , 'status' , 'size' , 'downloaded size' ,'download percentage' , 'number of connections' ,'Transfer rate' , 'estimate_time_left' , 'gid' , 'add_link_dictionary' , 'firs_try_date' , 'last_try_date']

        #if user or flashgot defined filename then file_name is valid in add_link_dictionary['out']
        if add_link_dictionary['out'] != None :
            file_name = add_link_dictionary['out']
        else:
            file_name = '***'

        #If user selected a queue in add_link window , then download must be added to queue and and download must  be started with queue so >> download_later == yes
        if str(category) != 'Single Downloads' :
            download_later = 'yes'

        if download_later == 'no' :
            download_info_file_list = [ file_name ,'waiting','***','***','***','***','***','***',gid , add_link_dictionary , '***' , '***' , category ]
        else:
            download_info_file_list = [ file_name ,'stopped','***','***','***','***','***','***',gid , add_link_dictionary , '***' , '***' , category ]



        #if user pushs ok button on add link window , a gid is generating for download and a file (with name of gid) is creating in download_info_folder . this file is containing download_info_file_list
        download_info_file = os.path.join(download_info_folder , gid) 
        osCommands.touch(download_info_file)
         
        writeList(download_info_file , download_info_file_list)

        #highlighting selected category in category_tree
        #finding item 
        for i in range(self.category_tree_model.rowCount()):
            category_tree_item_text = str(self.category_tree_model.index(i,0).data())
            if category_tree_item_text == category:
                category_index = i
                break
        #highliting
        category_tree_model_index = self.category_tree_model.index(category_index , 0)
        self.category_tree.setCurrentIndex(category_tree_model_index)
        self.categoryTreeSelected(category_tree_model_index)

      
        #creating a row in download_table
        self.download_table.insertRow(0)
        j = 0
        download_info_file_list[9] = str(download_info_file_list[9])
        for i in download_info_file_list :
            item = QTableWidgetItem(i)
            self.download_table.setItem(0,j,item)
            j = j + 1

        #this section adds checkBox to the row , if user selected selectAction
        if self.selectAction.isChecked() == True:
            item = self.download_table.item(0 , 0)
            item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.Unchecked)

        #adding gid to download_list_file , download_list_file_active , category_gid_list_file
        #defining category_gid_list_file
        category_gid_list_file = os.path.join(category_folder , category)

        for i in [download_list_file , download_list_file_active , category_gid_list_file] :
            f = Open ( i , "a")
            f.writelines(gid + "\n")
            f.close()

        #if user didn't press download_later_pushButton in add_link window then this section is creating new qthread for new download!
        if download_later == 'no':
            new_download = DownloadLink(gid)
            self.threadPool.append(new_download)
            self.threadPool[len(self.threadPool) - 1].start()
            self.threadPool[len(self.threadPool) - 1].ARIA2NOTRESPOND.connect(self.aria2NotRespond)
        #opening progress window for download.
            self.progressBarOpen(gid) 
        #notifiying user for scheduled download or download starting.
            if add_link_dictionary['start_hour'] == None :
                message = "Download Starts"
            else:
                new_spider = SpiderThread(add_link_dictionary , gid )
                self.threadPool.append(new_spider)
                self.threadPool[len(self.threadPool) - 1].start()
                message = "Download Scheduled"
            notifySend(message ,'' , 10000 , 'no', systemtray = self.system_tray_icon )

        else :
            new_spider = SpiderThread(add_link_dictionary , gid )
            self.threadPool.append(new_spider)
            self.threadPool[len(self.threadPool) - 1].start()

#when user presses resume button this method called
    def resumeButtonPressed(self,button):
        self.resumeAction.setEnabled(False)
        selected_row_return = self.selectedRow() #finding user selected row

        if selected_row_return != None:
            gid = self.download_table.item(selected_row_return , 8 ).text()
            download_status = self.download_table.item(selected_row_return , 1).text()
 
#this 'if' checks status of download before resuming! If download status is 'paused' then download must resumed and if status isn't 'paused' new download thread must created !                 
            if download_status == "paused" :
                answer = download.downloadUnpause(gid)
#if aria2 did not respond , then this function is checking for aria2 availability , and if aria2 disconnected then aria2Disconnected is executed 
                if answer == 'None':
                    version_answer = download.aria2Version()
                    if version_answer == 'did not respond':
                        self.aria2Disconnected()
                        notifySend("Aria2 disconnected!","Persepolis is trying to connect!be patient!",10000,'warning' , systemtray = self.system_tray_icon )
                    else:
                        notifySend("Aria2 did not respond!","Try agian!",10000,'warning' , systemtray = self.system_tray_icon )



            else:
                #new download thread
                new_download = DownloadLink(gid)
                self.threadPool.append(new_download)
                self.threadPool[len(self.threadPool) - 1].start()
                self.threadPool[len(self.threadPool) - 1].ARIA2NOTRESPOND.connect(self.aria2NotRespond)

                sleep(1)
                #new progress_window
                self.progressBarOpen(gid)



#this method called if aria2 crashed or disconnected!
    def aria2NotRespond(self):
        self.aria2Disconnected()
        notifySend('Aria2 did not respond' , 'Try again' , 5000 , 'critical' , systemtray = self.system_tray_icon )

#this method called if user presses stop button in MainWindow
    def stopButtonPressed(self,button):
        self.stopAction.setEnabled(False)
        selected_row_return = self.selectedRow()#finding user selected row

        if selected_row_return != None:
            gid = self.download_table.item(selected_row_return , 8 ).text()
            answer = download.downloadStop(gid)
#if aria2 did not respond , then this function is checking for aria2 availability , and if aria2 disconnected then aria2Disconnected is executed 
            if answer == 'None':
                version_answer = download.aria2Version()
                if version_answer == 'did not respond':
                    self.aria2Disconnected()
                    notifySend("Aria2 disconnected!","Persepolis is trying to connect!be patient!",10000,'warning' , systemtray = self.system_tray_icon )
               

#this method called if user presses pause button in MainWindow
    def pauseButtonPressed(self,button):
        self.pauseAction.setEnabled(False)
        selected_row_return = self.selectedRow()#finding user selected row

        if selected_row_return != None:
            gid = self.download_table.item(selected_row_return , 8 ).text()
            answer = download.downloadPause(gid)
#if aria2 did not respond , then this function is checking for aria2 availability , and if aria2 disconnected then aria2Disconnected is executed 
            if answer == 'None':
                version_answer = download.aria2Version()
                if version_answer == 'did not respond':
                    self.aria2Disconnected()
                    download.downloadStop(gid)
                    notifySend("Aria2 disconnected!","Persepolis is trying to connect!be patient!",10000,'warning' , systemtray = self.system_tray_icon )
                else:
                    notifySend("Aria2 did not respond!" , "Try agian!" , 10000 , 'critical' , systemtray = self.system_tray_icon )

#This method called if properties button pressed by user in MainWindow
    def propertiesButtonPressed(self,button):
        self.propertiesAction.setEnabled(False)
        selected_row_return = self.selectedRow() #finding user selected row

        if selected_row_return != None :
            #finding gid of download
            add_link_dictionary_str = self.download_table.item(selected_row_return , 9).text() 
            add_link_dictionary = ast.literal_eval(add_link_dictionary_str) 
            gid = self.download_table.item(selected_row_return , 8 ).text()

            #creating propertieswindow
            propertieswindow = PropertiesWindow(self.propertiesCallback ,gid  , self.persepolis_setting)
            self.propertieswindows_list.append(propertieswindow)
            self.propertieswindows_list[len(self.propertieswindows_list) - 1].show()

#callBack of PropertiesWindow
    def propertiesCallback(self,add_link_dictionary , gid , category ):

#if checking_flag is equal to 1, it means that user pressed remove or delete button or ... . so checking download information must be stopped until job is done!
        if checking_flag != 2 :
            wait_check = WaitThread()
            self.threadPool.append(wait_check)
            self.threadPool[len(self.threadPool) - 1].start()
            self.threadPool[len(self.threadPool) - 1].QTABLEREADY.connect(partial(self.propertiesCallback2 , add_link_dictionary , gid , category  ))
        else:
            self.removeSelected2(self , add_link_dictionary , gid , category)

    def propertiesCallback2(self , add_link_dictionary , gid , category):
        #current_category_tree_text is current category that highlited by user is the left side panel
        current_category_tree_text = str(self.category_tree.currentIndex().data())

        selected_row_return = self.selectedRow()#finding user selected row

        #finding current category before changing
        current_category = self.download_table.item(selected_row_return , 12).text()

 #finding checked rows! and append gid of checked rows to gid_list

        download_info_file = os.path.join(download_info_folder , gid)
        download_info_file_list = readList(download_info_file )
        download_info_file_list [9] = add_link_dictionary
        download_info_file_list [12] = str(category)


        #updating download_info_file
        writeList(download_info_file , download_info_file_list)

#updating category in download_table
#finding row of this gid!
        for i in range(self.download_table.rowCount()):
            row_gid = self.download_table.item(i , 8).text()
            if gid == row_gid :
                row = i 
                break

        if current_category_tree_text == 'All Downloads':
            item = QTableWidgetItem(str(category))
            self.download_table.setItem(row , 12 , item)
        elif (str(current_category) != str(category)):

            #removing row from download_table
            self.download_table.removeRow(row)



#telling the CheckDownloadInfoThread that job is done!
        global checking_flag
        checking_flag = 0

        

#This method called if user presses "show/hide progress window" button in MainWindow            
    def progressButtonPressed(self,button):
        selected_row_return = self.selectedRow() #finding user selected row
        if selected_row_return != None:
            gid = self.download_table.item(selected_row_return , 8 ).text()
        # if gid is in self.progress_window_list_dict , it means that progress window  for this gid (for this download) is created before and it's available!
            if gid in self.progress_window_list_dict :
                member_number = self.progress_window_list_dict[gid]
                #if window is visible >> hide it , and if window is hide >> make it visible!
                if self.progress_window_list[member_number].isVisible() == False:
                    self.progress_window_list[member_number].show()
                else :
                    self.progress_window_list[member_number].hide()
            else :
                self.progressBarOpen(gid) #if window is not availabile , let's create it!

#This method creates new ProgressWindow
    def progressBarOpen(self,gid):
        progress_window = ProgressWindow(parent = self,gid = gid , persepolis_setting = self.persepolis_setting ) #creating a progress window
        self.progress_window_list.append(progress_window) #adding progress window to progress_window_list
        member_number = len(self.progress_window_list) - 1
        self.progress_window_list_dict[gid] = member_number #in progress_window_list_dict , key is gid and value is member's rank(number) in progress_window_list

        #checking user preferences
        if str(self.persepolis_setting.value('settings/show-progress')) == 'yes':
            self.progress_window_list[member_number].show() #showing progress window
        else:
            self.progress_window_list[member_number].hide() #hiding progress window
 
#close event
#when user wants to close application then this function is called
    def closeEvent(self, event):
        self.persepolis_setting.setValue('MainWindow/size' , self.size())
        self.persepolis_setting.setValue('MainWindow/position' , self.pos())
        self.persepolis_setting.sync()

        self.hide()
        print("Please Wait...")
        logger.sendToLog("Please wait ...", "INFO")

        self.stopAllDownloads(event) #stopping all downloads
        self.system_tray_icon.hide() #hiding system_tray_icon

        download.shutDown() #shutting down Aria2
        sleep(0.5)
        global shutdown_notification #see start of this script and see inherited QThreads 
#shutdown_notification = 0 >> persepolis running , 1 >> persepolis is ready for close(closeEvent called) , 2 >> OK, let's close application!
        shutdown_notification = 1
        while shutdown_notification != 2:
            sleep (0.1)


        QCoreApplication.instance().quit
        print("Persepolis Closed")
        logger.sendToLog("Persepolis closed!", "INFO")
        sys.exit(0)

#showTray method is showing/hiding system tray icon
    def showTray(self,menu):
        if self.trayAction.isChecked() == True :
            self.system_tray_icon.show() #showing system_tray_icon
            self.minimizeAction.setEnabled(True) #enabling minimizeAction in menu
            tray_icon = 'yes' 
        else:
            self.system_tray_icon.hide() #hide system_tray_icon
            self.minimizeAction.setEnabled(False) #disabaling minimizeAction in menu
            tray_icon = 'no'
        #writing changes to setting file
        self.persepolis_setting.setValue('settings/tray-icon'  , tray_icon)
        self.persepolis_setting.sync()

    def showMenuBar(self , menu):
        if self.showMenuBarAction.isChecked():
            self.menubar.show()
            self.toolBar2.hide()
            show_menubar = 'yes'
        else:
            self.menubar.hide()
            self.toolBar2.show()
            show_menubar = 'no'

        #writing changes to persepolis_setting
        self.persepolis_setting.setValue('settings/show-menubar' , show_menubar)
        self.persepolis_setting.sync()

    def showSidePanel(self , menu):
        if self.showSidePanelAction.isChecked():
            self.category_tree_qwidget.show()
            show_sidepanel = 'yes'
        else:
            self.category_tree_qwidget.hide()
            show_sidepanel = 'no'

        #writing changes to persepolis_setting
        self.persepolis_setting.setValue('settings/show-sidepanel' , show_sidepanel)
        self.persepolis_setting.sync()

#when user click on mouse's left button , then this method is called
    def systemTrayPressed(self,click):
        if click == 3 :
            self.minMaxTray(click)
            
#when minMaxTray method called ,this method showed/hide main window 
    def minMaxTray(self,menu):
        if self.isVisible() == False:
            self.show()
            self.minimizeAction.setText('Minimize to system tray')
            self.minimizeAction.setIcon(QIcon(icons + 'minimize'))
        
        else :
            self.minimizeAction.setText('Show main Window')
            self.minimizeAction.setIcon(QIcon(icons + 'window'))
            self.hide()

#showMainWindow shows main window in normal mode , see CheckingThread 
    def showMainWindow(self):
        self.showNormal()
        self.minimizeAction.setText('Minimize to system tray')
        self.minimizeAction.setIcon(QIcon(icons + 'minimize'))
 
#stopAllDownloads is stopping all downloads
    def stopAllDownloads(self,menu):

#stopping all queues
        for queue in self.queue_list_dict.values():
            queue.stop = True
            queue.start = False

#stopping single downloads

        f = Open(single_downloads_list_file)
        single_downloads_list_file_lines = f.readlines()
        f.close()

        for line in single_downloads_list_file_lines:
            gid = line.strip()
            download_info_file = os.path.join(download_info_folder , gid)
            download_info_file_list = readList(download_info_file)
            status = download_info_file_list[1]
            if status == 'downloading' or status == 'paused' or status == 'waiting': #checking status of downloads
                answer = download.downloadStop(gid)
                #if aria2 did not respond , then this function is checking for aria2 availability , and if aria2 disconnected then aria2Disconnected is executed 
                if answer == 'None':
                    version_answer = download.aria2Version()
                    if version_answer == 'did not respond':
                        self.aria2Disconnected()
           
#this method is creating Preferences window
    def openPreferences(self,menu):
        self.preferenceswindow = PreferencesWindow(self , self.persepolis_setting )
        self.preferenceswindow.show() #showing Preferences Window


#this method is creating AboutWindow
    def openAbout(self,menu):
        about_window = AboutWindow(self.persepolis_setting)
        self.about_window_list.append(about_window)
        self.about_window_list[len(self.about_window_list) - 1].show()



#This method is openning user's default download folder
    def openDefaultDownloadFolder(self,menu):
        #finding user's default download folder from persepolis_setting 
        self.persepolis_setting.sync()
        download_path = self.persepolis_setting.value('settings/download_path')
        if os.path.isdir(download_path): #checking that if download folder is availabile or not
            osCommands.xdgOpen(download_path) #openning folder
        else:
            notifySend(str(download_path) ,'Not Found' , 5000 , 'warning' , systemtray = self.system_tray_icon ) #showing error message if folder didn't existed

#this method is openning download folder , if download was finished
    def openDownloadFolder(self,menu):
        selected_row_return = self.selectedRow() #finding user selected row

        if selected_row_return != None:
            gid = self.download_table.item(selected_row_return , 8 ).text() #finding gid
            download_status = self.download_table.item(selected_row_return , 1).text() #finding download status
            if download_status == 'complete':
            #finding download path
                add_link_dictionary_str = self.download_table.item(selected_row_return , 9).text() 
                add_link_dictionary = ast.literal_eval(add_link_dictionary_str) 
                if 'file_path' in add_link_dictionary :
                    file_path = add_link_dictionary ['file_path']
                        
                    file_name = os.path.basename(str(file_path))
                    
                    file_path_split = file_path.split(file_name)

                    del file_path_split[-1]

                    download_path = file_name.join(file_path_split)

                    if os.path.isdir(download_path):
                        osCommands.xdgOpen(download_path) #openning file
                    else:
                        notifySend(str(download_path) ,'Not Found' , 5000 , 'warning' , systemtray = self.system_tray_icon ) #showing error message , if folder did't existed


#this method is executing(openning) download file if download was finished
    def openFile(self,menu):
        selected_row_return = self.selectedRow() #finding user selected row

        if selected_row_return != None:
            gid = self.download_table.item(selected_row_return , 8 ).text() #finding gid
            download_status = self.download_table.item(selected_row_return , 1).text() #finding download status
            if download_status == 'complete':
                #finding file path
                add_link_dictionary_str = self.download_table.item(selected_row_return , 9).text() 
                add_link_dictionary = ast.literal_eval(add_link_dictionary_str) 
                if 'file_path' in add_link_dictionary:
                    file_path = add_link_dictionary['file_path']
                    if os.path.isfile(file_path):
                        osCommands.xdgOpen(file_path) #openning file
                    else:
                        notifySend(str(file_path) ,'Not Found' , 5000 , 'warning' , systemtray = self.system_tray_icon ) #showing error message , if file was deleted or moved

#This method is called when user presses remove button in main window . removeButtonPressed is removing download item
    def removeButtonPressed(self,button):
        self.removeAction.setEnabled(False)
        global checking_flag
#if checking_flag is equal to 1, it means that user pressed remove or delete button or ... . so checking download information must be stopped until job is done!
        if checking_flag != 2 :
            wait_check = WaitThread()
            self.threadPool.append(wait_check)
            self.threadPool[len(self.threadPool) - 1].start()
            self.threadPool[len(self.threadPool) - 1].QTABLEREADY.connect(self.removeButtonPressed2)
        else:
            self.removeButtonPressed2()



    def removeButtonPressed2(self):
        selected_row_return = self.selectedRow() #finding selected row

        if selected_row_return != None:
            gid = self.download_table.item(selected_row_return , 8 ).text()
            file_name = self.download_table.item(selected_row_return , 0).text()
            status = self.download_table.item(selected_row_return , 1).text()
            category = self.download_table.item(selected_row_return , 12).text()

            self.download_table.removeRow(selected_row_return) #removing item from download table

#remove gid of download from download list file and category list file and active download list file
            
            #finding category_gid_list_file
            category_gid_list_file = os.path.join(category_folder , str(category))
            #removing gid
            for file in [download_list_file , download_list_file_active , category_gid_list_file] :
                f = Open(file)
                f_lines = f.readlines()
                f.close()
                f = Open(file , "w")
                for i in f_lines:
                    if i.strip() != gid:
                        f.writelines(i.strip() + "\n")
                f.close()

#removing download_info_file
            download_info_file = os.path.join(download_info_folder , gid)
            f = Open(download_info_file)
            f.close()
            f.remove()

#remove file of download from download temp folder
            if file_name != '***' and status != 'complete' :
                file_name_path = os.path.join(temp_download_folder ,  str(file_name))
                osCommands.remove(file_name_path) #removing file

                file_name_aria = file_name_path + str('.aria2')
                osCommands.remove(file_name_aria) #removin file.aria 
        else:
            self.statusbar.showMessage("Please select an item first!")

#telling the CheckDownloadInfoThread that job is done!
        global checking_flag
        checking_flag = 0

        self.selectedRow()



#this method is called when user presses delete button in MainWindow . this method is deleting download file from hard disk and removing download item
    def deleteFile(self,menu):
#if checking_flag is equal to 1, it means that user pressed remove or delete button or ... . so checking download information must be stopped until job is done!
        if checking_flag != 2 :
            wait_check = WaitThread()
            self.threadPool.append(wait_check)
            self.threadPool[len(self.threadPool) - 1].start()
            self.threadPool[len(self.threadPool) - 1].QTABLEREADY.connect(self.deleteFile2)
        else:
            self.deleteFile2()

    def deleteFile2(self):
        selected_row_return = self.selectedRow() #finding user selected row
#This section is checking the download status , if download was completed then download file is removing
        if selected_row_return != None:
            gid = self.download_table.item(selected_row_return , 8 ).text()
            download_status = self.download_table.item(selected_row_return , 1).text()
            if download_status == 'complete':
                add_link_dictionary_str = self.download_table.item(selected_row_return , 9).text() 
                add_link_dictionary = ast.literal_eval(add_link_dictionary_str) 
                if 'file_path' in add_link_dictionary:
                    file_path = add_link_dictionary['file_path'] #finding file_path from add_link_dictionary
                    remove_answer = osCommands.remove(file_path) #removing file_path file
                    if remove_answer == 'no': #notifiying user if file_path is not valid
                        notifySend(str(file_path) ,'Not Found' , 5000 , 'warning' , systemtray = self.system_tray_icon )
                    self.removeButtonPressed2()

#this method is called when user checkes selection mode in edit menu!
    def selectDownloads(self,menu):
#selectAllAction is checked >> activating actions and adding removeSelectedAction and deleteSelectedAction to the toolBar
#selectAction is unchecked deactivate actions and adding removeAction and deleteFileAction to the toolBar
#if checking_flag is equal to 1, it means that user pressed remove or delete button or ... . so checking download information must be stopped until job is done!
        if checking_flag != 2 :
            wait_check = WaitThread()
            self.threadPool.append(wait_check)
            self.threadPool[len(self.threadPool) - 1].start()
            self.threadPool[len(self.threadPool) - 1].QTABLEREADY.connect(self.selectDownloads2)
        else:
            self.selectDownloads2()


    def selectDownloads2(self):
#finding highlited item in category_tree
        current_category_tree_text = str(current_category_tree_index.data())
        self.toolBarAndContextMenuItems(current_category_tree_text)

        if self.selectAction.isChecked() == True:
        #adding checkbox to items
            for i in range(self.download_table.rowCount()):
                item = self.download_table.item(i , 0)
                item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                item.setCheckState(QtCore.Qt.Unchecked)
        #activating selectAllAction and removeSelectedAction and deleteSelectedAction
                self.selectAllAction.setEnabled(True)
                self.removeSelectedAction.setEnabled(True)
                self.deleteSelectedAction.setEnabled(True)
                 
        else:
        #removing checkbox from items
            for i in range(self.download_table.rowCount()):
                item_text = self.download_table.item(i , 0).text()
                item = QTableWidgetItem(item_text) 
                self.download_table.setItem(i , 0 , item)
        #deactivating selectAllAction and removeSelectedAction and deleteSelectedAction
                self.selectAllAction.setEnabled(False)
                self.removeSelectedAction.setEnabled(False)
                self.deleteSelectedAction.setEnabled(False)
                

#telling the CheckDownloadInfoThread that job is done!
        global checking_flag
        checking_flag = 0


#this method called when user selects "select all items" form edit menu
    def selectAll(self,menu):
        for i in range(self.download_table.rowCount()):
            item = self.download_table.item(i , 0)
            item.setCheckState(QtCore.Qt.Checked)
 
#this method is called when user presses 'remove selected items' button
    def removeSelected(self,menu):

#if checking_flag is equal to 1, it means that user pressed remove or delete button or ... . so checking download information must be stopped until job is done!
        if checking_flag != 2 :
            wait_check = WaitThread()
            self.threadPool.append(wait_check)
            self.threadPool[len(self.threadPool) - 1].start()
            self.threadPool[len(self.threadPool) - 1].QTABLEREADY.connect(self.removeSelected2)
        else:
            self.removeSelected2()

    def removeSelected2(self):
 #finding checked rows! and append gid of checked rows to gid_list
        gid_list = []
        for row in range(self.download_table.rowCount()):
            status = self.download_table.item(row , 1).text() 
            item = self.download_table.item(row , 0)
            if (item.checkState() == 2) and (status == 'complete' or status == 'error' or status == 'stopped' ):
                gid = self.download_table.item(row , 8 ).text()
                gid_list.append(gid)

#removing checked rows
        #finding the row for specific gid
        for gid in gid_list:        
            for i in range(self.download_table.rowCount()):
                row_gid = self.download_table.item(i , 8).text()
                if gid == row_gid :
                    row = i 
                    break

            #finding filename 
            file_name = self.download_table.item(row , 0).text()
            
            #finding category
            category = self.download_table.item(row , 12).text()

            #removing row from download_table
            self.download_table.removeRow(row)

#removing gid of download from download list file and download_list_file_active and category_gid_list_file
            #setting category_gid_list_file path
            category_gid_list_file = os.path.join(category_folder , str(category))

            #removing gid
            for file in [download_list_file , download_list_file_active , category_gid_list_file] :
                f = Open(file)
                f_lines = f.readlines()
                f.close()
                f = Open(file , "w")
                for i in f_lines:
                    if i.strip() != gid:
                        f.writelines(i.strip() + "\n")
                f.close()

#removing download_info_file
            download_info_file = os.path.join(download_info_folder , gid)
            f = Open(download_info_file)
            f.close()
            f.remove()
#removing file of download form download temp folder
            if file_name != '***' and status != 'complete' :
                file_name_path = os.path.join(temp_download_folder , str(file_name))
                osCommands.remove(file_name_path) #removing file : file_name_path
                file_name_aria = file_name_path + str('.aria2')
                osCommands.remove(file_name_aria) #removing aria2 information file *.aria

#telling the CheckDownloadInfoThread that job is done!
        global checking_flag
        checking_flag = 0

#this method is called when user presses 'delete selected items'
    def deleteSelected(self,menu):
#if checking_flag is equal to 1, it means that user pressed remove or delete button or ... . so checking download information must be stopped until job is done!
        if checking_flag != 2 :
            wait_check = WaitThread()
            self.threadPool.append(wait_check)
            self.threadPool[len(self.threadPool) - 1].start()
            self.threadPool[len(self.threadPool) - 1].QTABLEREADY.connect(self.deleteSelected2)
        else:
            self.deleteSelected2()

    def deleteSelected2(self):
#finding checked rows! and appending gid of checked rows to gid_list
        gid_list = []
        for row in range(self.download_table.rowCount()):
            status = self.download_table.item(row , 1).text() 
            item = self.download_table.item(row , 0)
            if (item.checkState() == 2) and (status == 'complete' or status == 'error' or status == 'stopped' ):
                gid = self.download_table.item(row , 8 ).text()
                gid_list.append(gid)

#removing checked rows

        #finding row number for specific gid
        for gid in gid_list:        
            for i in range(self.download_table.rowCount()):
                row_gid = self.download_table.item(i , 8).text()
                if gid == row_gid :
                    row = i 
                    break

            #finding file_name
            file_name = self.download_table.item(row , 0).text()
            
            #finding category
            category = self.download_table.item(row , 12) . text()

            #finding add_link_dictionary
            add_link_dictionary_str = self.download_table.item(row , 9).text() 
            add_link_dictionary = ast.literal_eval(add_link_dictionary_str) 

            #removing row
            self.download_table.removeRow(row)

#removing gid of download from download list file and download_list_file_active and category_gid_list_file
            #finding category_gid_list_file
            category_gid_list_file = os.path.join(category_folder , str(category))

            #removing gid
            for file in [download_list_file , download_list_file_active , category_gid_list_file] :
                f = Open(file)
                f_lines = f.readlines()
                f.close()
                f = Open(file , "w")
                for i in f_lines:
                    if i.strip() != gid:
                        f.writelines(i.strip() + "\n")
                f.close()

#remove download_info_file
            download_info_file = os.path.join(download_info_folder , gid)
            f = Open(download_info_file)
            f.close()
            f.remove()

#remove file of download form download temp folder
            if file_name != '***' and status != 'complete' :
                file_name_path = os.path.join(temp_download_folder , str(file_name))
                osCommands.remove(file_name_path) #removing file : file_name_path

                file_name_aria = file_name_path + str('.aria2') #removing aria2 download information file : file_name_aria
                osCommands.remove(file_name_aria)
#remove download file
            if status == 'complete':
                if 'file_path' in add_link_dictionary:
                    file_path = add_link_dictionary['file_path']
                    remove_answer = osCommands.remove(file_path)
                    if remove_answer == 'no':
                        notifySend(str(file_path) ,'Not Found' , 5000 , 'warning' , systemtray = self.system_tray_icon )

#telling the CheckDownloadInfoThread that job is done!
        global checking_flag
        checking_flag = 0

#when this method called , download_table will sort by name
    def sortByName(self,menu_item):

#if checking_flag is equal to 1, it means that user pressed remove or delete button or ... . so checking download information must be stopped until job is done!
        if checking_flag != 2 :
            wait_check = WaitThread()
            self.threadPool.append(wait_check)
            self.threadPool[len(self.threadPool) - 1].start()
            self.threadPool[len(self.threadPool) - 1].QTABLEREADY.connect(self.sortByName2)
        else:
            self.sortByName2()

    def sortByName2(self):
#finding names and gid of download and saving them in name_gid_dict
        gid_name_dict = {}
        for row in range(self.download_table.rowCount()):
            name = self.download_table.item(row , 0).text() 
            gid = self.download_table.item(row , 8).text()
            gid_name_dict[gid] = name
#sorting names
        gid_sorted_list = sorted(gid_name_dict , key=gid_name_dict.get)

#clearing download_table 
        self.download_table.clearContents()
        j = -1
        for gid in gid_sorted_list:
            #entering download rows according to gid_sorted_list
            j = j + 1
            download_info_file = os.path.join(download_info_folder , gid)
            download_info_file_list = readList(download_info_file,'string')
            for i in range(13):
                item = QTableWidgetItem(download_info_file_list[i])

                #adding checkbox to download rows if selectAction is checked in edit menu
                if self.selectAction.isChecked() == True and i == 0 :
                    item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                    item.setCheckState(QtCore.Qt.Unchecked)
 
                self.download_table.setItem(j , i , item)

        #finding name of selected category
        current_category_tree_text = str(current_category_tree_index.data())
        if current_category_tree_text != 'All Downloads':
            category_file = os.path.join(category_folder , current_category_tree_text)
        else:
            category_file = download_list_file

        #opening category_file for writing changes
        f = Open(category_file , 'w')
        gid_sorted_list.reverse()

        for gid in gid_sorted_list:
            #applying changes to category_file
            f.writelines(gid + '\n')    

        f.close()

#telling the CheckDownloadInfoThread that job is done!
        global checking_flag
        checking_flag = 0

#this method is sorting download_table by size
    def sortBySize(self , menu_item):

#if checking_flag is equal to 1, it means that user pressed remove or delete button or ... . so checking download information must be stopped until job is done!
        if checking_flag != 2 :
            wait_check = WaitThread()
            self.threadPool.append(wait_check)
            self.threadPool[len(self.threadPool) - 1].start()
            self.threadPool[len(self.threadPool) - 1].QTABLEREADY.connect(self.sortBySize2)
        else:
            self.sortBySize2()


    def sortBySize2(self):
#finding gid and size of downloads
        gid_size_dict = {}
        for row in range(self.download_table.rowCount()):
            size_str = self.download_table.item(row , 2).text()
            gid = self.download_table.item(row , 8).text()
            try :
                #converting fike size to the Byte
                size_int = float(size_str[:-3])
                size_symbol = str(size_str[-2])
                if size_symbol == 'G': #Giga Byte
                    size = size_int * 1073741824   
                elif size_symbol == 'M':#Mega Byte
                    size = size_int * 1048576
                elif size_symbol == 'K':#Kilo Byte
                    size = size_int * 1024 
                else : #Byte
                    size = size_int 
            except:
                size = 0
#creating a dictionary from gid and size of files in Bytes 
            gid_size_dict[gid] = size

#sorting 
        gid_sorted_list = sorted(gid_size_dict , key = gid_size_dict.get , reverse = True )

#clearing download_table 
        self.download_table.clearContents()
#entering download rows according to gid_sorted_list
        j = -1
        for gid in gid_sorted_list:
            j = j + 1
            download_info_file = os.path.join(download_info_folder , gid)
            download_info_file_list = readList(download_info_file,'string')
            for i in range(13):
                item = QTableWidgetItem(download_info_file_list[i])

                #adding checkbox to download rows if selectAction is checked in edit menu
                if self.selectAction.isChecked() == True and i == 0 :
                    item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                    item.setCheckState(QtCore.Qt.Unchecked)
 
                self.download_table.setItem(j , i , item)
#telling the CheckDownloadInfoThread that job is done!

        #finding name of selected category
        current_category_tree_text = str(current_category_tree_index.data())

        if current_category_tree_text != 'All Downloads':
            category_file = os.path.join(category_folder , current_category_tree_text)
        else:
            category_file = download_list_file


        #opening category_file for writing changes
        f = Open(category_file , 'w')
        gid_sorted_list.reverse()

        for gid in gid_sorted_list:
            #applying changes to category_file
            f.writelines(gid + '\n')    

        f.close()

        global checking_flag
        checking_flag = 0


#this method is sorting download_table with status
    def sortByStatus(self,item):

#if checking_flag is equal to 1, it means that user pressed remove or delete button or ... . so checking download information must be stopped until job is done!
        if checking_flag != 2 :
            wait_check = WaitThread()
            self.threadPool.append(wait_check)
            self.threadPool[len(self.threadPool) - 1].start()
            self.threadPool[len(self.threadPool) - 1].QTABLEREADY.connect(self.sortByStatus2)
        else:
            self.sortByStatus2()


    def sortByStatus2(self):
#finding gid and status of downloads
        gid_status_dict = {}
        for row in range(self.download_table.rowCount()):
            status = self.download_table.item(row , 1).text()
            gid = self.download_table.item(row , 8).text()
#assigning a number to every status
            if status == 'complete' :
                status_int = 1
            elif status == 'stopped':
                status_int = 2
            elif status == 'error':
                status_int = 3
            elif status == 'downloading':
                status_int = 4
            elif status == 'waiting':
                status_int = 5
            else :
                status_int = 6
#creating a dictionary from gid and size_int of files in Bytes 
            gid_status_dict[gid] = status_int

#sorting 
        gid_sorted_list = sorted(gid_status_dict , key = gid_status_dict.get )

#clearing download_table 
        self.download_table.clearContents()
#entering download rows according to gid_sorted_list
        j = -1
        for gid in gid_sorted_list:
            j = j + 1
            download_info_file = os.path.join(download_info_folder , gid)
            download_info_file_list = readList(download_info_file,'string')
            for i in range(13):
                item = QTableWidgetItem(download_info_file_list[i])

                #adding checkbox to download rows if selectAction is checked in edit menu
                if self.selectAction.isChecked() == True and i == 0  :
                    item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                    item.setCheckState(QtCore.Qt.Unchecked)
 
                self.download_table.setItem(j , i , item)

        #finding name of selected category
        current_category_tree_text = str(current_category_tree_index.data())

        if current_category_tree_text != 'All Downloads':
            category_file = os.path.join(category_folder , current_category_tree_text)
        else:
            category_file = download_list_file


        #opening category_file for writing changes
        f = Open(category_file , 'w')
        gid_sorted_list.reverse()

        for gid in gid_sorted_list:
            #applying changes to category_file
            f.writelines(gid + '\n')    

        f.close()


#telling the CheckDownloadInfoThread that job is done!
        global checking_flag
        checking_flag = 0

#this method is sorting download table with date added information
    def sortByFirstTry(self,item) :

#if checking_flag is equal to 1, it means that user pressed remove or delete button or ... . so checking download information must be stopped until job is done!
        if checking_flag != 2 :
            wait_check = WaitThread()
            self.threadPool.append(wait_check)
            self.threadPool[len(self.threadPool) - 1].start()
            self.threadPool[len(self.threadPool) - 1].QTABLEREADY.connect(self.sortByFirstTry2)
        else:
            self.sortByFirstTry2()

    def sortByFirstTry2(self):
#finding gid and first try date
        gid_try_dict = {}
        for row in range(self.download_table.rowCount()):
            first_try_date = self.download_table.item(row , 10).text()
            gid = self.download_table.item(row , 8).text()
#this section is converting date and hour in first_try_date to a number for example , first_try_date = '2016/11/05 , 07:45:38' is converted to 20161105074538
            first_try_date_splited = first_try_date.split(' , ')
            date_list = first_try_date_splited[0].split('/')
            hour_list = first_try_date_splited[1].split(':')
            date_joind = "".join(date_list)
            hour_joind = "".join(hour_list)
            date_hour_str = date_joind + hour_joind
            date_hour = int(date_hour_str)

            gid_try_dict[gid] = date_hour

#sorting 
        gid_sorted_list = sorted(gid_try_dict , key = gid_try_dict.get  , reverse = True)

#clearing download_table 
        self.download_table.clearContents()
#entering download rows according to gid_sorted_list
        j = -1
        for gid in gid_sorted_list:
            j = j + 1
            download_info_file = os.path.join(download_info_folder , gid)
            download_info_file_list = readList(download_info_file,'string')
            for i in range(13):
                item = QTableWidgetItem(download_info_file_list[i])

                #adding checkbox to download rows if selectAction is checked in edit menu
                if self.selectAction.isChecked() == True and i == 0  :
                    item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                    item.setCheckState(QtCore.Qt.Unchecked)
 
                self.download_table.setItem(j , i , item)

        #finding name of selected category
        current_category_tree_text = str(current_category_tree_index.data())

        if current_category_tree_text != 'All Downloads':
            category_file = os.path.join(category_folder , current_category_tree_text)
        else:
            category_file = download_list_file


        #opening category_file for writing changes
        f = Open(category_file , 'w')
        gid_sorted_list.reverse()

        for gid in gid_sorted_list:
            #applying changes to category_file
            f.writelines(gid + '\n')    

        f.close()

#telling the CheckDownloadInfoThread that job is done!
        global checking_flag
        checking_flag = 0


#this method is sorting download_table with order of last modify date
    def sortByLastTry(self,item) :
#if checking_flag is equal to 1, it means that user pressed remove or delete button or ... . so checking download information must be stopped until job is done!
        if checking_flag != 2 :
            wait_check = WaitThread()
            self.threadPool.append(wait_check)
            self.threadPool[len(self.threadPool) - 1].start()
            self.threadPool[len(self.threadPool) - 1].QTABLEREADY.connect(self.sortByLastTry2)
        else:
            self.sortByLastTry2()

    def sortByLastTry2(self):
 
#finding gid and last try date
        gid_try_dict = {}
        for row in range(self.download_table.rowCount()):
            last_try_date = self.download_table.item(row , 11).text()
            gid = self.download_table.item(row , 8).text()
#this section is converting date and hour in last_try_date to a number for example , last_try_date = '2016/11/05 , 07:45:38' is converted to 20161105074538
            last_try_date_splited = last_try_date.split(' , ')
            date_list = last_try_date_splited[0].split('/')
            hour_list = last_try_date_splited[1].split(':')
            date_joind = "".join(date_list)
            hour_joind = "".join(hour_list)
            date_hour_str = date_joind + hour_joind
            date_hour = int(date_hour_str)

            gid_try_dict[gid] = date_hour

#sorting 
        gid_sorted_list = sorted(gid_try_dict , key = gid_try_dict.get  , reverse = True)

#clearing download_table 
        self.download_table.clearContents()
#entering download rows according to gid_sorted_list
        j = -1
        for gid in gid_sorted_list:
            j = j + 1
            download_info_file = os.path.join(download_info_folder , gid)
            download_info_file_list = readList(download_info_file,'string')
            for i in range(13):
                item = QTableWidgetItem(download_info_file_list[i])

                #adding checkbox to download rows if selectAction is checked in edit menu
                if self.selectAction.isChecked() == True and i == 0  :
                    item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                    item.setCheckState(QtCore.Qt.Unchecked)
 
                self.download_table.setItem(j , i , item)


        #finding name of selected category
        current_category_tree_text = str(current_category_tree_index.data())

        if current_category_tree_text != 'All Downloads':
            category_file = os.path.join(category_folder , current_category_tree_text)
        else:
            category_file = download_list_file


        #opening category_file for writing changes
        f = Open(category_file , 'w')
        gid_sorted_list.reverse()

        for gid in gid_sorted_list:
            #applying changes to category_file
            f.writelines(gid + '\n')    

        f.close()

#telling the CheckDownloadInfoThread that job is done!
        global checking_flag
        checking_flag = 0

#this method called , when user clicks on 'create new queue' button in main window.
    def createQueue(self,item):
        text, ok = QInputDialog.getText(self, 'Queue', 'Enter queue name:' , text = 'queue' )
        if not(ok) :
            return None
        queue_name = str(text)
        if ok and queue_name != '' and queue_name != 'Single Downloads' :
        #check queue_name if existed!
            f = Open(queues_list_file)
            f_lines = f.readlines()
            f.close()
            for line in f_lines :
                name = str(line.strip())
                if name == queue_name: #showng Error if queue existed before
                    error_messageBox = QMessageBox()                
                    error_messageBox.setText( '<b>"' + queue_name + '</b>" is already existed!')
                    error_messageBox.setWindowTitle('Error!')
                    error_messageBox.exec_()
                    return None
 

         #inserting items in category_tree
            new_queue_category = QStandardItem(queue_name)
            font = QtGui.QFont()
            font.setBold(True)
            new_queue_category.setFont(font)
            new_queue_category.setEditable(False)
            self.category_tree_model.appendRow(new_queue_category)

        #adding queue name to queues_list_file
            f = Open(queues_list_file , 'a')
            f.writelines(queue_name + '\n')
            f.close()
       
        #creating a file for this queue in category_folder
            osCommands.touch(os.path.join(category_folder , queue_name) )

        #creating a file for queue information in queue_info_folder
            queue_info_file = os.path.join(queue_info_folder , queue_name)

        #queue_info_file contains start time and end time information and ... for queue
            queue_info_dict = {'start_time_enable' : 'no' , 'end_time_enable' : 'no' , 'start_minute' : '0' , 'start_hour' : '0' , 'end_hour': '0' , 'end_minute' : '0' , 'reverse' : 'no' , 'limit_speed' : 'yes' , 'limit' : '0K' , 'after' : 'yes' }

            f = Open(queue_info_file , 'w' )
            f.writelines(str(queue_info_dict))
            f.close()

        #highlighting selected category in category_tree
        #finding item 
            for i in range(self.category_tree_model.rowCount()):
                category_tree_item_text = str(self.category_tree_model.index(i,0).data())
                if category_tree_item_text == queue_name:
                    category_index = i
                    break
        #highliting
            category_tree_model_index = self.category_tree_model.index(category_index , 0)
            self.category_tree.setCurrentIndex(category_tree_model_index)
            self.categoryTreeSelected(category_tree_model_index)
            
            #return queue_name
            return queue_name


    def flashgotQueue(self , flashgot_lines):
        flashgot_queue_window = FlashgotQueue(self , flashgot_lines , self.queueCallback , self.persepolis_setting)
        self.flashgot_queue_window_list.append(flashgot_queue_window)
        self.flashgot_queue_window_list[len(self.flashgot_queue_window_list) - 1].show()
        self.flashgot_queue_window_list[len(self.flashgot_queue_window_list) - 1].raise_()

        

#this method is importing text file for creating queue . text file must contain links . 1 link per line!
    def importText(self , item) :
        #getting file path
        f_path , filters = QFileDialog.getOpenFileName(self , 'Select the text file that contains links')
        if os.path.isfile(str(f_path)) == True :
            #creating a text_queue_window for getting information.
            text_queue_window = TextQueue(self , f_path , self.queueCallback , self.persepolis_setting )
            self.text_queue_window_list.append(text_queue_window)
            self.text_queue_window_list[len(self.text_queue_window_list) - 1].show()
            

#callback of text_queue_window.See importText method for more information.
    def queueCallback(self,add_link_dictionary_list , category):
        #defining path of category_file
        selected_category = str(category)
        category_file = os.path.join(category_folder , selected_category)

        #highlighting selected category in category_tree
        #finding item 
        for i in range(self.category_tree_model.rowCount()):
            category_tree_item_text = str(self.category_tree_model.index(i,0).data())
            if category_tree_item_text == selected_category:
                category_index = i
                break
        #highliting
        category_tree_model_index = self.category_tree_model.index(category_index , 0)
        self.category_tree.setCurrentIndex(category_tree_model_index)
        self.categoryTreeSelected(category_tree_model_index)

        #creating download_info_file for every add_link_dictionary in add_link_dictionary_list 
        for add_link_dictionary in add_link_dictionary_list:

            #aria2 identifies each download by the ID called GID. The GID must be hex string of 16 characters.
            gid = self.gidGenerator()

	    #download_info_file_list is a list that contains ['file_name' , 'status' , 'size' , 'downloaded size' ,'download percentage' , 'number of connections' ,'Transfer rate' , 'estimate_time_left' , 'gid' , 'add_link_dictionary' , 'firs_try_date' , 'last_try_date']
            try:
                file_name = str(add_link_dictionary['out'])
            except:
                file_name = '***'


            download_info_file_list = [ file_name ,'stopped', '***' ,'***','***','***','***','***',gid , add_link_dictionary , '***' ,'***' , selected_category ]


            #gid is generating for download and a file (with name of gid) is creating in download_info_folder . this file is containing download_info_file_list
            download_info_file = os.path.join( download_info_folder , gid)  
            osCommands.touch(download_info_file)
         
            writeList(download_info_file , download_info_file_list)
        
            #creating a row in download_table
            self.download_table.insertRow(0)
            j = 0
            download_info_file_list[9] = str(download_info_file_list[9])
            for i in download_info_file_list :
                item = QTableWidgetItem(i)
                self.download_table.setItem(0,j,item)
                j = j + 1

            #this section is adding checkBox to the row , if user selected selectAction
            if self.selectAction.isChecked() == True:
                item = self.download_table.item(0 , 0)
                item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                item.setCheckState(QtCore.Qt.Unchecked)

            # adding gid of download to download_list_file and download_list_file_active and category_file 
            for i in [ download_list_file , download_list_file_active , category_file]:
                f = Open ( i , "a")
                f.writelines(gid + "\n")
                f.close()

            #spider is finding file size and file name
            new_spider = SpiderThread(add_link_dictionary , gid )
            self.threadPool.append(new_spider)
            self.threadPool[len(self.threadPool) - 1].start()

#this method is called , when user is clicking on an item in category_tree (left side panel)
    def categoryTreeSelected(self,item):
        new_selection = item
        if current_category_tree_index != new_selection :
#if checking_flag is equal to 1, it means that user pressed remove or delete button or ... . so checking download information must be stopped until job is done!
            if checking_flag != 2 :

                wait_check = WaitThread()
                self.threadPool.append(wait_check)
                self.threadPool[len(self.threadPool) - 1].start()
                self.threadPool[len(self.threadPool) - 1].QTABLEREADY.connect(partial(self.categoryTreeSelected2 , new_selection ))
            else:
                self.categoryTreeSelected2(new_selection)
 
    def categoryTreeSelected2(self , new_selection):
        global current_category_tree_index

#clearing download_table 
        self.download_table.setRowCount(0)


#updating queue_info_file for old_selection before any changes!

        #old_selection_index
        old_selection_index = current_category_tree_index

        #finding name of old_selection_index
        old_category_tree_item_text = str(old_selection_index.data())


        #queue_info_file contains start time and end time information and ... for queue
        #finding queue_info_file path
        queue_info_file = os.path.join(queue_info_folder , old_category_tree_item_text)

        #queue_info_dict default format >> queue_info_dict = {'start_time_enable' : 'no' , 'end_time_enable' : 'no' , 'start_minute' : '0' , 'start_hour' : '0' , 'end_hour': '0' , 'end_minute' : '0' , 'reverse' : 'no' , 'limit_speed' : 'yes' , 'limit' : '0K'  , 'after': 'yes' }
        queue_info_dict = {}

        #start_checkBox
        if self.start_checkBox.isChecked() :
            queue_info_dict['start_time_enable'] = 'yes'
        else:
            queue_info_dict['start_time_enable'] = 'no'

        #end_checkBox
        if self.end_checkBox.isChecked():
            queue_info_dict['end_time_enable'] = 'yes'
        else:
            queue_info_dict['end_time_enable'] = 'no'


        #start_hour_spinBox
        start_hour = self.start_hour_spinBox.value()
        queue_info_dict['start_hour'] = str(start_hour)

        #start_minute_spinBox
        start_minute = self.start_minute_spinBox.value()
        queue_info_dict['start_minute'] = str(start_minute)

        #end_hour_spinBox
        end_hour = self.end_hour_spinBox.value()
        queue_info_dict ['end_hour'] = str(end_hour)

        #end_minute_spinBox
        end_minute = self.end_minute_spinBox.value()
        queue_info_dict['end_minute'] = str(end_minute)


        #reverse_checkBox
        if self.reverse_checkBox.isChecked():
            queue_info_dict['reverse'] = 'yes'
        else:
            queue_info_dict['reverse'] = 'no'

        #limit_checkBox
        if self.limit_checkBox.isChecked() :
            queue_info_dict['limit_speed'] = 'yes'
        else :
            queue_info_dict['limit_speed'] = 'no'

        #limit_comboBox and limit_spinBox
        if self.limit_comboBox.currentText() == "KB/S" :
            limit = str(self.limit_spinBox.value()) + str("K")
        else :
            limit = str(self.limit_spinBox.value()) + str("M")

        queue_info_dict['limit'] = str(limit)


        #after_checkBox
        if self.after_checkBox.isChecked():
            queue_info_dict['after'] = 'yes'
        else:
            queue_info_dict['after'] = 'no'

        
        if old_selection_index.data() != None : #if old_selection_index.data() is equal to None >> It means queue deleted! and no text (data) available for it
            #saving values
            f = Open(queue_info_file , 'w' )
            f.writelines(str(queue_info_dict))
            f.close()


#updating download_table
        current_category_tree_index = new_selection 

        #finding category name
        current_category_tree_text = str(self.category_tree.currentIndex().data())

        #findin path of gid_list_file , gid_list_file cantains gid of downloads for selected category 
        if current_category_tree_text == 'All Downloads':
            gid_list_file = download_list_file
        else:
            gid_list_file = os.path.join(category_folder , current_category_tree_text)
                    
        f_download_list_file = Open(gid_list_file)
        download_list_file_lines = f_download_list_file.readlines()
        f_download_list_file.close()
            
        for line in download_list_file_lines:
            gid = line.strip()
            self.download_table.insertRow(0)
            download_info_file = os.path.join(download_info_folder , gid)
            download_info_file_list = readList(download_info_file,'string')
            for i in range(13):
                item = QTableWidgetItem(download_info_file_list[i])
                    
                    #adding checkbox to download rows if selectAction is checked in edit menu
                if self.selectAction.isChecked() == True and i == 0:
                    item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                    item.setCheckState(QtCore.Qt.Unchecked)
 
                self.download_table.setItem(0 , i , item)

#telling the CheckDownloadInfoThread that job is done!
        global checking_flag
        checking_flag = 0

#updating toolBar and tablewidget_menu items
        self.toolBarAndContextMenuItems(str(current_category_tree_text)) 
                

#this method changing toolabr and cotext menu items when new item highlited by user in category_tree
    def toolBarAndContextMenuItems(self,category):
        self.toolBar.clear()
        self.download_table.tablewidget_menu.clear()
        self.category_tree.category_tree_menu.clear()

        #adding selectAction to context menu
        self.download_table.tablewidget_menu.addAction(self.selectAction)


        queueAction = QAction(QIcon(icons + 'add') , 'Single Downloads' , self , statusTip = "Add to Single Downloads"  , triggered = partial(self.addToQueue , 'Single Downloads' ) ) 

        #checking if user checked selection mode
        if self.selectAction.isChecked() == True :
            mode = 'selection'
            self.download_table.sendMenu = self.download_table.tablewidget_menu.addMenu('Send selected downloads to')

        else:
            mode = 'None'
            self.download_table.sendMenu = self.download_table.tablewidget_menu.addMenu('Send to')

        if category != 'Single Downloads':
            self.download_table.sendMenu.addAction(queueAction)

        #adding sendMenu items
        f = Open(queues_list_file)
        f_lines = f.readlines()
        f.close()
        for i in f_lines:
            if i.strip() != category:
                queueAction = QAction(QIcon(icons + 'add_queue') , str(i.strip()) , self , statusTip = "Add to" + str(i.strip()) , triggered = partial(self.addToQueue , str(i.strip())) ) 
                self.download_table.sendMenu.addAction(queueAction)


        if category == 'All Downloads' and mode == 'None':

            #hiding queue_panel_widget(left side down panel)
            self.queue_panel_widget.hide()

            #updating toolBar
            for i in self.addlinkAction,self.resumeAction, self.pauseAction , self.stopAction, self.removeAction , self.deleteFileAction , self.propertiesAction , self.progressAction ,self.minimizeAction , self.exitAction :
                self.toolBar.addAction(i)
 
            self.toolBar.insertSeparator(self.addlinkAction)
            self.toolBar.insertSeparator(self.resumeAction) 
            self.toolBar.insertSeparator(self.removeSelectedAction)
            self.toolBar.insertSeparator(self.exitAction)

 
#add actions to download_table's context menu
            for action in [self.openFileAction , self.openDownloadFolderAction , self.resumeAction , self.pauseAction , self.stopAction , self.removeAction , self.deleteFileAction , self.propertiesAction , self.progressAction]:
                self.download_table.tablewidget_menu.addAction(action)


        elif category == 'All Downloads' and mode == 'selection':
         
            self.queue_panel_widget.hide()

            for i in self.addlinkAction,self.resumeAction, self.pauseAction , self.stopAction, self.removeSelectedAction , self.deleteSelectedAction , self.propertiesAction, self.progressAction, self.minimizeAction , self.exitAction :
                self.toolBar.addAction(i)
 
            self.toolBar.insertSeparator(self.addlinkAction)
            self.toolBar.insertSeparator(self.resumeAction)     
            self.toolBar.insertSeparator(self.removeSelectedAction)
            self.toolBar.insertSeparator(self.exitAction)
            self.toolBar.addSeparator()
 
 
#add actions to download_table's context menu
            for action in [self.openFileAction , self.openDownloadFolderAction , self.resumeAction , self.pauseAction , self.stopAction , self.removeSelectedAction , self.deleteSelectedAction , self.propertiesAction , self.progressAction]:
                self.download_table.tablewidget_menu.addAction(action)


        if category == 'Single Downloads' and mode == 'None':

            self.queue_panel_widget.hide()

            for i in self.addlinkAction,self.resumeAction, self.pauseAction , self.stopAction, self.removeAction , self.deleteFileAction , self.propertiesAction, self.progressAction ,self.minimizeAction , self.exitAction :
                self.toolBar.addAction(i)
 
            self.toolBar.insertSeparator(self.addlinkAction)
            self.toolBar.insertSeparator(self.resumeAction) 
            self.toolBar.insertSeparator(self.removeSelectedAction)
            self.toolBar.insertSeparator(self.exitAction)
    
 
#add actions to download_table's context menu
            for action in [self.openFileAction , self.openDownloadFolderAction , self.resumeAction , self.pauseAction , self.stopAction , self.removeAction , self.deleteFileAction , self.propertiesAction , self.progressAction]:
                self.download_table.tablewidget_menu.addAction(action)


        elif category == 'Single Downloads' and mode == 'selection':
         
            self.queue_panel_widget.hide()
            self.queuePanelWidget(category)

            for i in self.addlinkAction,self.resumeAction, self.pauseAction , self.stopAction, self.removeSelectedAction , self.deleteSelectedAction , self.propertiesAction, self.progressAction, self.minimizeAction , self.exitAction :
                self.toolBar.addAction(i)
 
            self.toolBar.insertSeparator(self.addlinkAction)
            self.toolBar.insertSeparator(self.removeSelectedAction)
            self.toolBar.insertSeparator(self.exitAction)
            self.toolBar.addSeparator()

#add actions to download_table's context menu
            for action in [self.openFileAction , self.openDownloadFolderAction , self.resumeAction , self.pauseAction , self.stopAction , self.removeSelectedAction , self.deleteSelectedAction , self.propertiesAction , self.progressAction]:
                self.download_table.tablewidget_menu.addAction(action)


        elif (category != 'All Downloads' and category != 'Single Downloads') and mode == 'None':
            self.queue_panel_widget.show()
            self.queuePanelWidget(category)

            for i in self.addlinkAction,self.removeAction , self.deleteFileAction , self.propertiesAction,self.startQueueAction , self.stopQueueAction , self.removeQueueAction , self.moveUpAction , self.moveDownAction , self.minimizeAction , self.exitAction :
                self.toolBar.addAction(i)
 
            self.toolBar.insertSeparator(self.addlinkAction)
            self.toolBar.insertSeparator(self.startQueueAction)
            self.toolBar.insertSeparator(self.minimizeAction)
            self.toolBar.insertSeparator(self.exitAction)
            self.toolBar.addSeparator()

#add actions to download_table's context menu
            for action in [self.openFileAction , self.openDownloadFolderAction , self.removeAction , self.deleteFileAction , self.propertiesAction ]:
                self.download_table.tablewidget_menu.addAction(action)

#updating category_tree_menu
            for i in self.startQueueAction , self.stopQueueAction , self.removeQueueAction :
                self.category_tree.category_tree_menu.addAction(i)


            #checking queue condition
            if str(category) in self.queue_list_dict.keys():
                queue_status = self.queue_list_dict[str(category)].start
            else:
                queue_status = False

            if queue_status : #if queue started before 
                self.stopQueueAction.setEnabled(True)
                self.startQueueAction.setEnabled(False)
                self.removeQueueAction.setEnabled(False)
            else:            #if queue didn't start 
                self.stopQueueAction.setEnabled(False)
                self.startQueueAction.setEnabled(True)
                self.removeQueueAction.setEnabled(True)

        elif (category != 'All Downloads' and category != 'Single Downloads') and mode == 'selection':
            self.queue_panel_widget.show()
            self.queuePanelWidget(category)

            for i in self.addlinkAction,self.removeSelectedAction , self.deleteSelectedAction , self.propertiesAction,self.startQueueAction , self.stopQueueAction , self.removeQueueAction  , self.moveUpSelectedAction , self.moveDownSelectedAction , self.minimizeAction , self.exitAction :
                self.toolBar.addAction(i)
 
            self.toolBar.insertSeparator(self.addlinkAction)
            self.toolBar.insertSeparator(self.startQueueAction)
            self.toolBar.insertSeparator(self.minimizeAction)
            self.toolBar.insertSeparator(self.exitAction)
            self.toolBar.addSeparator()

#add actions to download_table's context menu
            for action in [self.openFileAction , self.openDownloadFolderAction , self.removeAction , self.deleteFileAction , self.propertiesAction ]:
                self.download_table.tablewidget_menu.addAction(action)

#updating category_tree_menu(right click menu for category_tree items)
            for i in self.startQueueAction , self.stopQueueAction , self.removeQueueAction :
                self.category_tree.category_tree_menu.addAction(i)


        #checking queue condition
        if category != 'All Downloads' and category != 'Single Downloads':
            if str(category) in self.queue_list_dict.keys():
                queue_status = self.queue_list_dict[str(category)].start
            else:
                queue_status = False

            if queue_status : #if queue started befor 
                self.stopQueueAction.setEnabled(True)
                self.startQueueAction.setEnabled(False)
                self.removeQueueAction.setEnabled(False)
                self.moveUpAction.setEnabled(False)
                self.moveDownAction.setEnabled(False)
                self.moveUpSelectedAction.setEnabled(False)
                self.moveDownSelectedAction.setEnabled(False)
            else:            #if queue didn't start 
                self.stopQueueAction.setEnabled(False)
                self.startQueueAction.setEnabled(True)
                self.removeQueueAction.setEnabled(True)
                if mode != 'selection':
                    self.moveUpAction.setEnabled(True)
                    self.moveDownAction.setEnabled(True)
                    self.moveUpSelectedAction.setEnabled(False)
                    self.moveDownSelectedAction.setEnabled(False)
                else:
                    self.moveUpAction.setEnabled(False)
                    self.moveDownAction.setEnabled(False)
                    self.moveUpSelectedAction.setEnabled(True)
                    self.moveDownSelectedAction.setEnabled(True)

           
        else: #if category is All Downloads  or Single Downloads
            self.stopQueueAction.setEnabled(False)
            self.startQueueAction.setEnabled(False)
            self.removeQueueAction.setEnabled(False)
            self.moveUpAction.setEnabled(False)
            self.moveDownAction.setEnabled(False)
            self.moveUpSelectedAction.setEnabled(False)
            self.moveDownSelectedAction.setEnabled(False)
 
        #adding sortMenu to download_table context menu
        sortMenu = self.download_table.tablewidget_menu.addMenu('Sort by')
        sortMenu.addAction(self.sort_file_name_Action)

        sortMenu.addAction(self.sort_file_size_Action)


        sortMenu.addAction(self.sort_first_try_date_Action)


        sortMenu.addAction(self.sort_last_try_date_Action)

        sortMenu.addAction(self.sort_download_status_Action)



 
#this method removes the queue that selected in category_tree
    def removeQueue(self,menu):
        #finding name of queue
        current_category_tree_text = str(current_category_tree_index.data())

        if current_category_tree_text != 'All Downloads' and current_category_tree_text != 'Single Downloads' :

            #removing queue from category_tree
            row_number = current_category_tree_index.row()
            self.category_tree_model.removeRow(row_number)

            #finding path of queue in category_folder
            queue_gid_file = os.path.join(category_folder , current_category_tree_text)

            #getting gids from queue_gid_file 
            f = Open(queue_gid_file)
            gid_list = f.readlines()
            f.close()
            #deleting queue's file
            f.remove()

            for j in gid_list :
                gid = j.strip()
                #removing gid from download_list_file , download_list_file_active 
                for file in [download_list_file , download_list_file_active ] :
                    f = Open(file)
                    f_lines = f.readlines()
                    f.close()
                    f = Open(file , "w")
                    for i in f_lines:
                        if i.strip() != gid:
                            f.writelines(i.strip() + "\n")
                    f.close()


           #removing name of the queu from queues_list_file 
            f = Open(queues_list_file)
            f_lines = f.readlines()
            f.close()
            
            f = Open(queues_list_file , 'w')
            for i in f_lines:
                if i.strip() != current_category_tree_text:
                    f.writelines(i.strip() + '\n')
            f.close()

            #removing queue_info_file
            #finding queue_info_file path
            queue_info_file = os.path.join(queue_info_folder , current_category_tree_text)

            #removing file
            osCommands.remove(queue_info_file)


#highlighting "All Downloads" in category_tree
        all_download_index = self.category_tree_model.index(0,0)
        self.category_tree.setCurrentIndex(all_download_index)
        self.categoryTreeSelected(all_download_index)

    def startQueue(self,menu):
        self.startQueueAction.setEnabled(False)

        #current_category_tree_text is the name of queue that selected by user
        current_category_tree_text = str(current_category_tree_index.data())

#checking start time and end time
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

#create new Queue thread
        new_queue = Queue(current_category_tree_text , start_hour , start_minute , end_hour , end_minute , self)

#queue_list_dict contains queue threads >> queue_list_dict[name of queue] = Queue(name of queue , parent)
        self.queue_list_dict [current_category_tree_text] = new_queue
        self.queue_list_dict[current_category_tree_text].start()
        self.queue_list_dict[current_category_tree_text].REFRESHTOOLBARSIGNAL.connect(self.toolBarAndContextMenuItems)

        self.toolBarAndContextMenuItems(current_category_tree_text)
 
    def stopQueue(self , menu):
        self.stopQueueAction.setEnabled(False)

        #current_category_tree_text is the name of queue that selected by user
        current_category_tree_text = str(current_category_tree_index.data())

        queue = self.queue_list_dict[current_category_tree_text]
        queue.start = False
        queue.stop = True
 
        self.startQueueAction.setEnabled(True)
                 
#this method is called , when user want to add a download to a queue with context menu. see also toolBarAndContextMenuItems() method
    def addToQueue(self , data, menu ):
#if checking_flag is equal to 1, it means that user pressed remove or delete button or ... . so checking download information must be stopped until job is done!

        if checking_flag != 2 :
            wait_check = WaitThread()
            self.threadPool.append(wait_check)
            self.threadPool[len(self.threadPool) - 1].start()
            self.threadPool[len(self.threadPool) - 1].QTABLEREADY.connect(partial(self.addToQueue2 , data ))
        else:
            self.addToQueue2(data)
 
    def addToQueue2(self , data):
        

        send_message = False
        new_category = str(data) #new selected category
        gid_list = []
        #checking if user checked selectAction in edit menu
        if self.selectAction.isChecked() == True :
#finding checked rows! and appending gid of checked rows to gid_list
            for row in range(self.download_table.rowCount()):
                status = self.download_table.item(row , 1).text() 
                item = self.download_table.item(row , 0)
                category = self.download_table.item(row , 12).text()

                if category in self.queue_list_dict.keys():
                    if self.queue_list_dict[category].start :
                        status = 'downloading' #It means queue is in download progress

                if (item.checkState() == 2) and (status == 'error' or status == 'stopped' or status == 'complete' ):
                    gid = self.download_table.item(row , 8 ).text()
                    gid_list.append(gid)
                if not  (status == 'error' or status == 'stopped' or status == 'complete' ):
                    send_message = True

        else:
            #finding selected_row
            selected_row_return = self.selectedRow() #finding user selected row

#appending gid of selected_row to gid_list
            if selected_row_return != None:
                gid = self.download_table.item(selected_row_return , 8 ).text()
                status = self.download_table.item(selected_row_return , 1).text() 
                category = self.download_table.item(selected_row_return , 12).text()

                if category in self.queue_list_dict.keys():
                    if self.queue_list_dict[category].start :
                        status = 'downloading' #It means queue is in download progress


                if  (status == 'error' or status == 'stopped' or status == 'complete' ):
                    gid_list.append(gid)
                else:
                    send_message = True

        for gid in gid_list:        

        #finding row number for specific gid
            for i in range(self.download_table.rowCount()):
                row_gid = self.download_table.item(i , 8).text()
                if gid == row_gid :
                    row = i 
                    break

            current_category = self.download_table.item(row ,12).text() #current_category = former selected category

            if current_category != new_category :
                
        #first download must eliminated form former category (current_category)
        #reading current_category_file
                current_category_file = os.path.join(category_folder , current_category)

                f = Open(current_category_file)
                f_list = f.readlines()
                f.close()

                #eliminating gid of download from queue_current_file
                f = Open(current_category_file , 'w')
                for line in f_list:
                    gid_line = line.strip()
                    if gid_line != gid :
                        f.writelines(gid_line + '\n')

                f.close()
 
                #adding download to the new queue
                new_category_file = os.path.join(category_folder , new_category)

                f = Open(new_category_file , 'a')
                f.writelines(gid + '\n')
                f.close()
 
#updating download_info_file
                download_info_file = os.path.join(download_info_folder , gid)
                download_info_file_list = readList(download_info_file )
                download_info_file_list [12] = new_category

                add_link_dictionary = download_info_file_list[9]
#eliminating start_hour and start_minute and end_hour and end_minute!         
                add_link_dictionary['start_hour'] = None
                add_link_dictionary['start_minute'] = None
                add_link_dictionary['end_hour'] = None
                add_link_dictionary['end_minute'] = None
 
                download_info_file_list [9] = add_link_dictionary
                writeList(download_info_file , download_info_file_list)

#updating category in download_table
                current_category_tree_text = str(current_category_tree_index.data())
                if current_category_tree_text == 'All Downloads': 
                    item = QTableWidgetItem(new_category)
                    #if user checked selectAction , then a checkbox added to item
                    if self.selectAction.isChecked() == True:
                        item = self.download_table.item(0 , 0)
                        item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                        item.setCheckState(QtCore.Qt.Unchecked)

                    self.download_table.setItem(row , 12 , item)
                else:
                    self.download_table.removeRow(row)

        if send_message:
            notifySend("sending some items was unsuccessful!", "Please stop download progress first" , '5000' , 'no', systemtray = self.system_tray_icon )

        global checking_flag
        checking_flag = 0


#this method activating or deactivating start_frame according to situation
    def startFrame(self,checkBox):

        if self.start_checkBox.isChecked() == True :
            self.start_frame.setEnabled(True)
        else :
            self.start_frame.setEnabled(False)

#this method activating or deactivating end_frame according to situation
    def endFrame(self,checkBox):

        if self.end_checkBox.isChecked() == True :
            self.end_frame.setEnabled(True)
        else :
            self.end_frame.setEnabled(False)


#this method showing/hiding queue_panel_widget according to queue_panel_show_button text 
    def showQueuePanelOptions(self,button):
        if (self.queue_panel_show_button.text() == 'Show options'):
            self.queue_panel_widget_frame.show()
            self.queue_panel_show_button.setText('Hide options')
        else:
            self.queue_panel_widget_frame.hide()
            self.queue_panel_show_button.setText('Show options')

#this metode is activating after_pushButton whith limit_comboBox changing
    def limitComboBoxChanged(self , connect):
        self.limit_pushButton.setEnabled(True)
 

#this method is activating or deactivating limit_frame according to limit_checkBox situation
    def limitFrame(self , checkBox):
        if self.limit_checkBox.isChecked() == True:
            self.limit_frame.setEnabled(True)
        else:
            self.limit_frame.setEnabled(False)

        #current_category_tree_text is the name of queue that selected by user
            current_category_tree_text = str(current_category_tree_index.data())
    
        #informing queue about changes
            if current_category_tree_text in self.queue_list_dict.keys() :
                self.queue_list_dict[current_category_tree_text].limit = False
                self.queue_list_dict[current_category_tree_text].limit_changed = True


#this method is limiting download speed in queue
    def limitPushButtonPressed(self,button):
        self.limit_pushButton.setEnabled(False)

        #current_category_tree_text is the name of queue that selected by user
        current_category_tree_text = str(current_category_tree_index.data())

        #informing queue about changes
        self.queue_list_dict[current_category_tree_text].limit = True
        self.queue_list_dict[current_category_tree_text].limit_changed = True

#this method is handling user's shutdown request in queue downloading
    def afterPushButtonPressed(self , button):
        #current_category_tree_text is the name of queue that selected by user
        current_category_tree_text = str(current_category_tree_index.data())

        self.after_pushButton.setEnabled(False)

        if os_type != 'Windows': #For Linu and Mac OSX

        #getting root password from user
            passwd, ok = QInputDialog.getText(self, 'PassWord','Please enter root password:' , QtWidgets.QLineEdit.Password)
            if ok :
                answer = os.system("echo '" + passwd+"' |sudo -S echo 'checking passwd'  "  )
                while answer != 0 :
                    passwd, ok = QInputDialog.getText(self, 'PassWord','Wrong Password!\nTry again!' , QtWidgets.QLineEdit.Password)
                    if ok :
                        #checking password
                        answer = os.system("echo '" + passwd +"' |sudo -S echo 'checking passwd'  "  )
                    else:
                        ok = False
                        break

                if ok != False :
                        self.queue_list_dict[current_category_tree_text].after = True

                    #sending password and queue name to ShutDownThread
                    #this script is creating a file with the name of queue in  this folder "persepolis_tmp/shutdown/" . and writing a "wait" word in this file 
                    #shutdown_script_root is checking that file every second . when "wait" changes to "shutdown" in that file then script is shutting down system 
                        shutdown_enable = ShutDownThread( current_category_tree_text , passwd)
                        self.threadPool.append(shutdown_enable)
                        self.threadPool[len(self.threadPool) - 1].start()
 
                else:
                    self.after_checkBox.setChecked(False)
                    self.queue_list_dict[current_category_tree_text].after = False

            else:
                self.after_checkBox.setChecked(False)
                self.queue_list_dict[current_category_tree_text].after = False

        else: #for windows
            
            shutdown_enable = ShutDownThread( current_category_tree_text)
            self.threadPool.append(shutdown_enable)
            self.threadPool[len(self.threadPool) - 1].start()
 

#this method is activating or deactivating after_frame according to after_checkBox situation
    def afterFrame(self , checkBox):
        #current_category_tree_text is the name of queue that selected by user
        current_category_tree_text = str(current_category_tree_index.data())

        if self.after_checkBox.isChecked() == True: #enabling after_frame
            self.after_frame.setEnabled(True)
            self.after_pushButton.setEnabled(True)
        else:
            self.after_frame.setEnabled(False) #disabaling after_frame

            #writing 'canceled' word in persepolis_tmp/shutdown/queue_name . this is informing shutdown_script_root for canceling shutdown operation after download
            if current_category_tree_text in self.queue_list_dict.keys():
                if self.queue_list_dict[current_category_tree_text].after == True:
                    shutdown_file = os.path.join(persepolis_tmp , 'shutdown' , current_category_tree_text )
                    f = Open( shutdown_file , 'w')
                    f.writelines('canceled')
                    f.close()
                    self.queue_list_dict[current_category_tree_text].after = False


#queue_panel_widget
#this method checking that queue started or not , and it showing or hiding widgets in queue_panel_widget according to situation and set widgets value.
    def queuePanelWidget(self,category):
        #updating queue_panel_widget items
        #finding queue_info_file path
        queue_info_file = os.path.join(queue_info_folder , category)

        #queue_info_dict default format >> queue_info_dict = {'start_time_enable' : 'no' , 'end_time_enable' : 'no' , 'start_minute' : '0' , 'start_hour' : '0' , 'end_hour': '0' , 'end_minute' : '0' , 'reverse' : 'no' , 'limit_speed' : 'yes' , 'limit' : '0K'  , 'after': 'yes' }
        #reading queue_info_dict
        queue_info_dict = readDict(queue_info_file)
    
 
               
           
            #after download options
#             if queue_info_dict['after'] == 'yes':
#                 self.after_checkBox.setChecked(True)
#             else:
#                 self.after_checkBox.setChecked(False)
 


        #checking queue condition
        if str(category) in self.queue_list_dict.keys():
            queue_status = self.queue_list_dict[str(category)].start
        else:
            queue_status = False

        if queue_status : #queue started
            self.start_end_frame.hide()
            self.limit_after_frame.show()

            #checking that if user set limit speed
            limit_status = self.queue_list_dict[str(category)].limit

            #checking that if user selected 'shutdown after download'
            after_status =  self.queue_list_dict[str(category)].after

            if limit_status == True : #It means queue's download speed limited by user 
                #getting limit_spinBox value and limit_comboBox value 
                limit_number =  self.queue_list_dict[str(category)].limit_spinBox_value
                limit_unit = self.queue_list_dict[str(category)].limit_comboBox_value

                #setting limit_spinBox value
                self.limit_spinBox.setValue(limit_number)

                #setting limit_comboBox value
                if limit_unit == 'K':
                    self.after_comboBox.setCurrentIndex(0)
                else:
                    self.after_comboBox.setCurrentIndex(1)
                
                #enabling limit_frame
                self.limit_checkBox.setChecked(True)

            else:

                #disabaling limit_frame
                self.limit_checkBox.setChecked(False)

            #limit speed
            #limit_checkBox
#                 if queue_info_dict['limit_speed'] == 'yes':
#                     self.limit_checkBox.setChecked(True)
#                 else:
#                     self.limit_checkBox.setChecked(False)

                limit = str(queue_info_dict['limit'])

            #limit values
                limit_number = limit[0:-1]
                limit_unit = limit[-1]
 
            #limit_spinBox
                self.limit_spinBox.setValue(int(limit_number))

            #limit_comboBox
                if limit_unit == 'K':
                    self.limit_comboBox.setCurrentIndex(0)
                else:
                    self.limit_comboBox.setCurrentIndex(1)
 

            #so user was selected shutdown option , after queue completed.
            if after_status == True:
                self.after_checkBox.setChecked(True)

            else:
                self.after_checkBox.setChecked(False)
        else:     #queue stopped
            self.start_end_frame.show()
            self.limit_after_frame.hide()

            #start time
            #start_checkBox
            if queue_info_dict['start_time_enable'] == 'yes':
                self.start_checkBox.setChecked(True)
            else:
                self.start_checkBox.setChecked(False)

            #start_hour_spinBox
            self.start_hour_spinBox.setValue(int(queue_info_dict['start_hour']))

            #start_minute_spinBox
            self.start_minute_spinBox.setValue(int(queue_info_dict['start_minute']))

            #end time
            #end_checkBox
            if queue_info_dict['end_time_enable'] == 'yes':
                self.end_checkBox.setChecked(True)
            else:
                self.end_checkBox.setChecked(False)


            #end_hour_spinBox
            self.end_hour_spinBox.setValue(int(queue_info_dict['end_hour']))

            #end_minute_spinBox
            self.end_minute_spinBox.setValue(int(queue_info_dict['end_minute']))

            #reverse_checkBox
            if queue_info_dict['reverse'] == 'yes' :
                self.reverse_checkBox.setChecked(True)
            else:
                self.reverse_checkBox.setChecked(False)
 
 
        self.limitFrame(category)
        self.afterFrame(category)
        self.startFrame(category)
        self.endFrame(category)

#this method is openning issues page in github 
    def reportIssue(self,menu):
        osCommands.xdgOpen('https://github.com/persepolisdm/persepolis/issues')

#this method is opening releases page in github
    def newUpdate(self,menu):
        osCommands.xdgOpen('https://github.com/persepolisdm/persepolis/releases')


#this method is called when user pressed moveUpAction
#this method is subtituting selected download item with upper one
    def moveUp(self,menu):
        global button_pressed_counter
        button_pressed_counter = button_pressed_counter + 1
#if checking_flag is equal to 1, it means that user pressed remove or delete button or ... . so checking download information must be stopped until job is done!

        if checking_flag != 2 :
            button_pressed_thread = ButtonPressedThread()
            self.threadPool.append(button_pressed_thread)
            self.threadPool[len(self.threadPool) - 1].start()

            wait_check = WaitThread()
            self.threadPool.append(wait_check)
            self.threadPool[len(self.threadPool) - 1].start()
            self.threadPool[len(self.threadPool) - 1].QTABLEREADY.connect(self.moveUp2)
        else:
            self.moveUp2()
 
    def moveUp2(self):
        old_row = self.selectedRow() #finding user selected row

        #current_category_tree_text is the name of queue that selected by user
        current_category_tree_text = str(current_category_tree_index.data())

#an old row and new row must replaced  by each other
        if old_row != None:
            new_row = int(old_row) - 1
            if new_row >= 0 :

                #opening and reading queue_file
                queue_file = os.path.join(category_folder , current_category_tree_text)

                f = Open(queue_file)
                queue_file_lines = f.readlines()
                f.close()


                #old index and new index of item in queue file
                old_index_in_file = len(queue_file_lines) - old_row - 1
                new_index_in_file = old_index_in_file + 1
                #replacing lines in queue_file
                queue_file_lines[old_index_in_file] , queue_file_lines[new_index_in_file] = queue_file_lines [new_index_in_file] , queue_file_lines[old_index_in_file]

                f = Open(queue_file , 'w')
                for line in queue_file_lines:
                    f.writelines(line)

                f.close()

        
                old_row_items_list = [] 
                new_row_items_list = []
                
                #reading current items in download_table
                for i in range(13):
                    old_row_items_list.append(self.download_table.item(old_row , i).text())
                    new_row_items_list.append(self.download_table.item(new_row , i).text())
            
                #replacing
                for i in range(13):
                    #old row
                    item = QTableWidgetItem(new_row_items_list[i])

                    self.download_table.setItem(old_row , i , item)

                    #new row
                    item = QTableWidgetItem(old_row_items_list[i])
                    self.download_table.setItem(new_row , i , item)

                self.download_table.selectRow(new_row)


#this method is called when user pressed moveUpSelectedAction
#this method is subtituting selected  items with upper one

    def moveUpSelected(self , menu):
        global button_pressed_counter
        button_pressed_counter = button_pressed_counter + 1
#if checking_flag is equal to 1, it means that user pressed remove or delete button or ... . so checking download information must be stopped until job is done!

        if checking_flag != 2 :
            button_pressed_thread = ButtonPressedThread()
            self.threadPool.append(button_pressed_thread)
            self.threadPool[len(self.threadPool) - 1].start()

            wait_check = WaitThread()
            self.threadPool.append(wait_check)
            self.threadPool[len(self.threadPool) - 1].start()
            self.threadPool[len(self.threadPool) - 1].QTABLEREADY.connect(self.moveUpSelected2)
        else:
            self.moveUpSelected2()
 

    def moveUpSelected2(self):
        index_list = []

        #current_category_tree_text is the name of queue that selected by user
        current_category_tree_text = str(current_category_tree_index.data())


        #finding checked rows
        for row in range(self.download_table.rowCount()):
            item = self.download_table.item(row , 0)
            if (item.checkState() == 2) :
                index_list.append(row) #appending index of checked rows to index_list

        #moving up selected rows
        for old_row in index_list:
            new_row = int(old_row) - 1
            if new_row >= 0 :

                #opening and reading queue_file
                queue_file = os.path.join(category_folder , current_category_tree_text)

                f = Open(queue_file)
                queue_file_lines = f.readlines()
                f.close()


                #old index and new index of item in queue file
                old_index_in_file = len(queue_file_lines) - old_row - 1
                new_index_in_file = old_index_in_file + 1
                #replacing lines in queue_file
                queue_file_lines[old_index_in_file] , queue_file_lines[new_index_in_file] = queue_file_lines [new_index_in_file] , queue_file_lines[old_index_in_file]

                f = Open(queue_file , 'w')
                for line in queue_file_lines:
                    f.writelines(line)

                f.close()

        
                old_row_items_list = [] 
                new_row_items_list = []


                #reading current items in download_table
                for i in range(13):
                    old_row_items_list.append(self.download_table.item(old_row , i).text())
                    new_row_items_list.append(self.download_table.item(new_row , i).text())
            
                #replacing
                for i in range(13):
                    #old row
                    item = QTableWidgetItem(new_row_items_list[i])
                    #adding checkbox
                    if i == 0:
                        item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                        #set Unchecked
                        item.setCheckState(QtCore.Qt.Unchecked)

                    self.download_table.setItem(old_row , i , item)

                    #new row
                    item = QTableWidgetItem(old_row_items_list[i])
                    #adding checkbox
                    if i == 0 :
                        item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                        #set Checked
                        item.setCheckState(QtCore.Qt.Checked)

                    self.download_table.setItem(new_row , i , item)


#this method is called if user pressed moveDown action 
#this method is subtituting selected download item with lower download item
    def moveDown(self,menu):
        global button_pressed_counter
        button_pressed_counter = button_pressed_counter + 1
#if checking_flag is equal to 1, it means that user pressed remove or delete button or ... . so checking download information must be stopped until job is done!
        if checking_flag != 2 :
            button_pressed_thread = ButtonPressedThread()
            self.threadPool.append(button_pressed_thread)
            self.threadPool[len(self.threadPool) - 1].start()

            wait_check = WaitThread()
            self.threadPool.append(wait_check)
            self.threadPool[len(self.threadPool) - 1].start()
            self.threadPool[len(self.threadPool) - 1].QTABLEREADY.connect(self.moveDown2)
        else:
            self.moveDown2()
 
    def moveDown2(self):
        old_row = self.selectedRow() #finding user selected row

        #current_category_tree_text is the name of queue that selected by user
        current_category_tree_text = str(current_category_tree_index.data())

#an old row and new row must replaced  by each other
        if old_row != None:
            new_row = int(old_row) + 1
            if new_row < self.download_table.rowCount():

                #opening and reading queue_file
                queue_file = os.path.join(category_folder , current_category_tree_text)

                f = Open(queue_file)
                queue_file_lines = f.readlines()
                f.close()


                #old index and new index of item in queue file
                old_index_in_file = len(queue_file_lines) - old_row - 1
                new_index_in_file = old_index_in_file - 1
                #replacing lines in queue_file
                queue_file_lines[old_index_in_file] , queue_file_lines[new_index_in_file] = queue_file_lines [new_index_in_file] , queue_file_lines[old_index_in_file]

                f = Open(queue_file , 'w')
                for line in queue_file_lines:
                    f.writelines(line)

                f.close()

        
                old_row_items_list = [] 
                new_row_items_list = []
                
                #reading current items in download_table
                for i in range(13):
                    old_row_items_list.append(self.download_table.item(old_row , i).text())
                    new_row_items_list.append(self.download_table.item(new_row , i).text())
            
                #replacing
                for i in range(13):
                    #old_row
                    item = QTableWidgetItem(new_row_items_list[i])
                    self.download_table.setItem(old_row , i , item)

                    #new_row
                    item = QTableWidgetItem(old_row_items_list[i])
                    self.download_table.setItem(new_row , i , item)
                self.download_table.selectRow(new_row)


#this method is called if user pressed moveDownSelected action 
#this method is subtituting selected download item with lower download item
    def moveDownSelected(self,menu):
        global button_pressed_counter
        button_pressed_counter = button_pressed_counter + 1
#if checking_flag is equal to 1, it means that user pressed remove or delete button or ... . so checking download information must be stopped until job is done!
        if checking_flag != 2 :
            button_pressed_thread = ButtonPressedThread()
            self.threadPool.append(button_pressed_thread)
            self.threadPool[len(self.threadPool) - 1].start()

            wait_check = WaitThread()
            self.threadPool.append(wait_check)
            self.threadPool[len(self.threadPool) - 1].start()
            self.threadPool[len(self.threadPool) - 1].QTABLEREADY.connect(self.moveDownSelected2)
        else:
            self.moveDownSelected2()
 
    def moveDownSelected2(self):

#an old row and new row must replaced  by each other
        index_list = []

        #current_category_tree_text is the name of queue that selected by user
        current_category_tree_text = str(current_category_tree_index.data())


        #finding checked rows
        for row in range(self.download_table.rowCount()):
            item = self.download_table.item(row , 0)
            if (item.checkState() == 2) :
                index_list.append(row) #appending index of checked rows to index_list

        index_list.reverse()

        #moving up selected rows
        for old_row in index_list:
 
            new_row = int(old_row) + 1
            if new_row < self.download_table.rowCount():

                #opening and reading queue_file
                queue_file = os.path.join(category_folder , current_category_tree_text)

                f = Open(queue_file)
                queue_file_lines = f.readlines()
                f.close()


                #old index and new index of item in queue file
                old_index_in_file = len(queue_file_lines) - old_row - 1
                new_index_in_file = old_index_in_file - 1
                #replacing lines in queue_file
                queue_file_lines[old_index_in_file] , queue_file_lines[new_index_in_file] = queue_file_lines [new_index_in_file] , queue_file_lines[old_index_in_file]

                f = Open(queue_file , 'w')
                for line in queue_file_lines:
                    f.writelines(line)

                f.close()

        
                old_row_items_list = [] 
                new_row_items_list = []
                
                #reading current items in download_table
                for i in range(13):
                    old_row_items_list.append(self.download_table.item(old_row , i).text())
                    new_row_items_list.append(self.download_table.item(new_row , i).text())
            
                #replacing
                for i in range(13):
                    #old row
                    item = QTableWidgetItem(new_row_items_list[i])
                    
                    #adding checkbox
                    if i == 0:
                        item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                        #set Unchecked
                        item.setCheckState(QtCore.Qt.Unchecked)

                    self.download_table.setItem(old_row , i , item)

                    
                    #new_row
                    item = QTableWidgetItem(old_row_items_list[i])

                    #adding checkbox
                    if i == 0 :
                        item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                        #set Checked
                        item.setCheckState(QtCore.Qt.Checked)


                    self.download_table.setItem(new_row , i , item)

#see flashgot_queue.py file
    def queueSpiderCallBack(self, filename , child , row_number ):
        item = QTableWidgetItem(str(filename))

        #adding checkbox to the item
        item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        if child.links_table.item(int(row_number) , 0 ).checkState() == 2: 
            item.setCheckState(QtCore.Qt.Checked)
        else:
            item.setCheckState(QtCore.Qt.Unchecked)


        child.links_table.setItem(int(row_number) , 0 , item )

#Chrome and Chromium Integration Window
    def browserIntegration(self,menu):
        browser_integration_window = ChromiumIntegrationWindow(self.persepolis_setting)
        self.browser_integration_window_list.append(browser_integration_window)
        self.browser_integration_window_list[len(self.browser_integration_window_list) - 1].show()

