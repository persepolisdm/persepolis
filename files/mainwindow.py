#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys , ast
from PyQt5 import QtCore, QtGui, QtWidgets  
from PyQt5.QtWidgets import QSystemTrayIcon , QMenu , QTableWidgetItem ,QAbstractItemView , QApplication , QToolBar , QMenuBar , QStatusBar, QTableWidget , QAction , QMainWindow , QWidget , QFrame , QAbstractItemView
from PyQt5.QtGui import QIcon , QColor , QPalette 
from PyQt5.QtCore import QCoreApplication , QRect , QSize , QThread , pyqtSignal  , Qt
import os
from time import sleep
import random  
from addlink import AddLinkWindow
from properties import PropertiesWindow
from progress import ProgressWindow
import download
from mainwindow_ui import MainWindow_Ui
from newopen import Open
from play import playNotification
from bubble import notifySend
from setting import PreferencesWindow
from about import AboutWindow
import icons_resource


#shutdown_notification = 0 >> persepolis running , 1 >> persepolis is ready for close(closeEvent called) , 2 >> OK, let's close application!
global shutdown_notification
shutdown_notification = 0

home_address = os.path.expanduser("~")
config_folder = str(home_address) + "/.config/persepolis_download_manager"

download_info_folder = config_folder + "/download_info"

temp_download_folder = str(home_address) + "/.persepolis"

#download_list_file contains GID of all downloads
download_list_file = config_folder + "/download_list_file"
#download_list_file_active for active downloads
download_list_file_active = config_folder + "/download_list_file_active"

#setting
setting_file = config_folder + '/setting'
f = Open(setting_file)
setting_file_lines = f.readlines()
f.close()
setting_dict_str = str(setting_file_lines[0].strip())
setting_dict = ast.literal_eval(setting_dict_str) 
#finding icons folder path
icons = ':/' + str(setting_dict['icons']) + '/'


#start aria2 when Persepolis starts
class StartAria2Thread(QThread):
    ARIA2RESPONDSIGNAL = pyqtSignal(str)
    def __init__(self):
        QThread.__init__(self)
        
    def run(self):
        global aria_startup_answer
        aria_startup_answer = 'None'
        answer = download.startAria()
        #if Aria2 doesn't respond to Persepolis ,ARIA2RESPONDSIGNAL is emitting no  
        if answer == 'did not respond':
            signal_str = 'no'
        else :
            signal_str = 'yes'

        self.ARIA2RESPONDSIGNAL.emit(signal_str)



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
        global shutdown_notification
        while True:

            while shutdown_notification == 0 and aria_startup_answer != 'ready':
                sleep (1)

            while shutdown_notification != 1:
                sleep(0.2)
                f = Open(download_list_file_active) 
                download_list_file_active_lines = f.readlines()
                f.close()
                if len(download_list_file_active_lines) != 0 :
                    for line in download_list_file_active_lines:
                        gid = line.strip()
                        try:
                            answer = download.downloadStatus(gid)
                        except:
                            answer = 'None'
                        if answer == 'ready' :
                            sleep(0.2)
                            download_info_file = download_info_folder + "/" + gid
                            if os.path.isfile(download_info_file) == True:
                                self.DOWNLOAD_INFO_SIGNAL.emit(gid)
            shutdown_notification = 2
            break
                            
                                
                            
                        




            
class DownloadLink(QThread):
    def __init__(self,gid):
        QThread.__init__(self)
        self.gid = gid

    def run(self):
        answer = download.downloadAria(self.gid)
        if answer == 'None':
            notifySend('Aria2 did not respond' , 'Try again' , 5000 , 'critical')

        

class CheckFlashgot(QThread):
    CHECKFLASHGOTSIGNAL = pyqtSignal()
    def __init__(self):
        QThread.__init__(self)

    def run(self):
        global shutdown_notification
        while shutdown_notification == 0 and aria_startup_answer != 'ready':
            sleep (2)
        while shutdown_notification == 0:
            sleep(2)
            if os.path.isfile("/tmp/persepolis-flashgot")  == True and os.path.isfile("/tmp/persepolis-flashgot.lock") == False:
                self.CHECKFLASHGOTSIGNAL.emit()




class MainWindow(MainWindow_Ui):
    def __init__(self):
        super().__init__()
        self.statusbar.showMessage('Please Wait ...')
        self.checkSelectedRow()

#touch download_list_file
        if not(os.path.isfile(download_list_file)):
            f = Open(download_list_file , 'w')
            f.close()

#touch download_list_file_active
        if not(os.path.isfile(download_list_file_active)):
            f = Open(download_list_file_active , 'w')
            f.close()


#lock files perventing to access a file simultaneously

#removing lock files in starting persepolis
        os.system("rm " + config_folder +"/*.lock" + "  2>/dev/null" )
        os.system("rm " + download_info_folder + "/*.lock" + "   2>/dev/null" )


#threads     
        self.threadPool=[]
#starting aria
        start_aria = StartAria2Thread()
        self.threadPool.append(start_aria)
        self.threadPool[0].start() 
        self.threadPool[0].ARIA2RESPONDSIGNAL.connect(self.startAriaMessage)

#initializing    

#add downloads to the download_table
        f_download_list_file = Open(download_list_file)
        download_list_file_lines = f_download_list_file.readlines()
        f_download_list_file.close()
            
        for line in download_list_file_lines:
            gid = line.strip()
            self.download_table.insertRow(0)
            download_info_file = download_info_folder + "/" + gid
            f = Open(download_info_file)
            download_info_file_lines = f.readlines()
            f.close()
            for i in range(10):
                item = QTableWidgetItem(download_info_file_lines[i].strip())
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

                download_info_file = download_info_folder + "/" + gid
                f = Open(download_info_file)
                download_info_file_lines = f.readlines()
                f.close()

                f = Open(download_info_file , "w")
                for i in range(10):
                    if i == 1 :
                        f.writelines("stopped" + "\n")
                        item = QTableWidgetItem('stopped')
                        self.download_table.setItem(row , i , item )
                    elif i == 9 :
                        f.writelines(str(add_link_dictionary) + "\n")
                        item = QTableWidgetItem(str(add_link_dictionary))
                        self.download_table.setItem(row,i , item)
                    else:
                        f.writelines(download_info_file_lines[i].strip() + "\n")

                f.close()
        self.addlinkwindows_list = []
        self.propertieswindows_list = []
        self.progress_window_list = []
        self.progress_window_list_dict = {}

        check_download_info = CheckDownloadInfoThread()
        self.threadPool.append(check_download_info)
        self.threadPool[1].start()
        self.threadPool[1].DOWNLOAD_INFO_SIGNAL.connect(self.checkDownloadInfo)

        check_selected_row = CheckSelectedRowThread()
        self.threadPool.append(check_selected_row)
        self.threadPool[2].start()
        self.threadPool[2].CHECKSELECTEDROWSIGNAL.connect(self.checkSelectedRow)

        check_flashgot = CheckFlashgot()
        self.threadPool.append(check_flashgot)
        self.threadPool[3].start()
        self.threadPool[3].CHECKFLASHGOTSIGNAL.connect(self.checkFlashgot)

        self.download_table.itemDoubleClicked.connect(self.openFile)
        
        self.system_tray_icon = QSystemTrayIcon() 
        self.system_tray_icon.setIcon(QIcon(':/icon'))
        system_tray_menu = QMenu()
        system_tray_menu.addAction(self.addlinkAction)
        system_tray_menu.addAction(self.pauseAllAction)
        system_tray_menu.addAction(self.stopAllAction)
        system_tray_menu.addAction(self.minimizeAction)
        system_tray_menu.addAction(self.exitAction)
        self.system_tray_icon.setContextMenu(system_tray_menu)
        self.system_tray_icon.activated.connect(self.systemTrayPressed)
        self.system_tray_icon.show()

        f = Open(setting_file)
        setting_file_lines = f.readlines()
        f.close()
        setting_dict_str = str(setting_file_lines[0].strip())
        setting_dict = ast.literal_eval(setting_dict_str) 
        if setting_dict['tray-icon'] != 'yes': 
            self.minimizeAction.setEnabled(False)
            self.system_tray_icon.hide()

    def startAriaMessage(self,message):
        global aria_startup_answer
        if message == 'yes':
            sleep (2)
            self.statusbar.showMessage('Ready...')
            aria_startup_answer = 'ready'
        else:
            self.statusbar.showMessage('Error...')
            notifySend('Persepolis can not connect to Aria2' , 'Restart Persepolis' ,10000,'critical' )

    def checkDownloadInfo(self,gid):
        try:
#get download information from download_info_file according to gid and write them in download_table cells
            download_info_file = config_folder + "/download_info/" + gid
            f = Open(download_info_file)
            download_info_file_lines = f.readlines()
            f.close()
#finding row of this gid!
            for i in range(self.download_table.rowCount()):
                row_gid = self.download_table.item(i , 8).text()
                if gid == row_gid :
                    row = i 
                    break

            for i in range(10):
#check flag of download!
                if i == 0 :
                    flag = int(self.download_table.item(row , i).flags())

#remove gid of completed download from active downloads list file
                elif i == 1 :
                    status = download_info_file_lines[i].strip()
                    status = str(status)
                    status_download_table = str(self.download_table.item(row , 1 ) . text())

                    if status == "complete":
                        f = Open(download_list_file_active)
                        download_list_file_active_lines = f.readlines()
                        f.close()
                        f = Open(download_list_file_active , "w")
                        for line in download_list_file_active_lines :
                            if line.strip() != gid :
                                f.writelines(line.strip() + "\n")
                        f.close()
                    
#update download_table cells
                item = QTableWidgetItem(download_info_file_lines[i].strip())
#48 means item is checkable and enabled
                if i == 0 and flag == 48:
                    item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                    if self.download_table.item(row,0).isChecked()  == False:
                        item_num.setCheckState(QtCore.Qt.Unchecked)

                self.download_table.setItem(row , i , item)
                self.download_table.viewport().update()
#update progresswindow
            try :
            
                member_number = self.progress_window_list_dict[gid]
                progress_window = self.progress_window_list[member_number]
                #link
                add_link_dictionary_str = str(download_info_file_lines[9].strip())
                add_link_dictionary = ast.literal_eval(add_link_dictionary_str) 
                link = "<b>Link</b> : " +  str(add_link_dictionary ['link'])
                progress_window.link_label.setText(link)
                progress_window.link_label.setToolTip(link)

                #Save as
                final_download_path = add_link_dictionary['final_download_path']
                if final_download_path == None :
                    final_download_path = str(add_link_dictionary['download_path'])
                        
                save_as = "<b>Save as</b> : " + final_download_path + "/" + str(download_info_file_lines[0].strip())
                progress_window.save_label.setText(save_as)
                file_name = str(download_info_file_lines[0].strip())
                if file_name != "***":
                    progress_window.setWindowTitle(file_name ) 

                #status
                progress_window.status = download_info_file_lines[1].strip()
                status = "<b>status</b> : " + progress_window.status 
                progress_window.status_label.setText(status)
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
                    progress_window.stop_pushButton.setEnabled(False)
                    progress_window.pause_pushButton.setEnabled(False)
                elif progress_window.status == "scheduled":
                    progress_window.resume_pushButton.setEnabled(False)
                    progress_window.stop_pushButton.setEnabled(True)
                    progress_window.pause_pushButton.setEnabled(False)
                elif progress_window.status == "stopped" or progress_window.status == "error" or progress_window.status == "complete" :
                    progress_window.close()
                    self.progress_window_list[member_number] = []
                    del self.progress_window_list_dict[gid]
                    if progress_window.status == "complete":
                        notifySend("Download Complete" ,str(download_info_file_lines[0])  , 10000 , 'ok' )
                    elif progress_window.status == "stopped":
                        notifySend("Download Stopped" , str(download_info_file_lines[0]) , 10000 , 'no')

                    elif progress_window.status == "error":
                        notifySend("Error - " + add_link_dictionary['error'] , str(download_info_file_lines[0]) , 10000 , 'fail')
               
                        add_link_dictionary['start_hour'] = None
                        add_link_dictionary['start_minute'] = None
                        add_link_dictionary['end_hour'] = None
                        add_link_dictionary['end_minute'] = None
                        add_link_dictionary['after_download'] = 'None'

                        f = Open(download_info_file , "w")
                        for i in range(10):
                            if i == 9 :
                                f.writelines(str(add_link_dictionary) + "\n")
                            else:
                                f.writelines(download_info_file_lines[i].strip() + "\n")

                        f.close()
                    
                    if os.path.isfile('/tmp/persepolis/shutdown/' + gid ) == True and progress_window.status != 'stopped':
                        answer = download.shutDown()
                        if answer == 'error':
                            os.system('killall aria2c')
                        f = Open('/tmp/persepolis/shutdown/' + gid , 'w')
                        f.writelines('shutdown')
                        f.close()
                    elif os.path.isfile('/tmp/persepolis/shutdown/' + gid ) == True and progress_window.status == 'stopped':
                        f = Open('/tmp/persepolis/shutdown/' + gid , 'w')
                        f.writelines('canceled')
                        f.close()



             
                #downloaded
                downloaded = "<b>Downloaded</b> : " + str(download_info_file_lines[3].strip()) + "/" + str(download_info_file_lines[2].strip())
                progress_window.downloaded_label.setText(downloaded)

                #Transfer rate
                rate = "<b>Transfer rate</b> : " + str(download_info_file_lines[6].strip())
                progress_window.rate_label.setText(rate)

                #Estimate time left
                estimate_time_left = "<b>Estimate time left</b> : " + str(download_info_file_lines[7].strip()) 
                progress_window.time_label.setText(estimate_time_left)

                #Connections
                connections = "<b>Connections</b> : " + str(download_info_file_lines[5].strip())
                progress_window.connections_label.setText(connections)


                #progressbar
                value = download_info_file_lines[4].strip()
                value = value[:-1]
                progress_window.download_progressBar.setValue(int(value))
            except :
                pass
        except:
            pass
                   



#contex menu
    def contextMenuEvent(self, event):
        self.tablewidget_menu = QMenu(self)
        self.tablewidget_menu.addAction(self.openFileAction)
        self.tablewidget_menu.addAction(self.openDownloadFolderAction)
        self.tablewidget_menu.addAction(self.resumeAction)
        self.tablewidget_menu.addAction(self.pauseAction)
        self.tablewidget_menu.addAction(self.stopAction)
        self.tablewidget_menu.addAction(self.removeAction)
        self.tablewidget_menu.addAction(self.deleteFileAction)
        self.tablewidget_menu.addAction(self.propertiesAction)
        self.tablewidget_menu.addAction(self.progressAction)
        self.tablewidget_menu.popup(QtGui.QCursor.pos())
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
                self.stopAction.setEnabled(False)
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
            self.progressAction.setEnabled(False)
            self.resumeAction.setEnabled(False)
            self.stopAction.setEnabled(False)
            self.pauseAction.setEnabled(False)
            self.removeAction.setEnabled(False)
            self.propertiesAction.setEnabled(False)
            self.openDownloadFolderAction.setEnabled(False)
            self.openFileAction.setEnabled(False)            
            self.deleteFileAction.setEnabled(False)



           
    def checkFlashgot(self):
        sleep(0.5)
        flashgot_file = Open("/tmp/persepolis-flashgot")
        flashgot_line = flashgot_file.readlines()
        flashgot_file.close()
        flashgot_file.remove()
        flashgot_add_link_dictionary_str = flashgot_line[0]
        flashgot_add_link_dictionary = ast.literal_eval(flashgot_add_link_dictionary_str) 
        self.flashgotAddLink(flashgot_add_link_dictionary)


    def flashgotAddLink(self,flashgot_add_link_dictionary):
        addlinkwindow = AddLinkWindow(self.callBack , flashgot_add_link_dictionary)
        self.addlinkwindows_list.append(addlinkwindow)
        self.addlinkwindows_list[len(self.addlinkwindows_list) - 1].show()

       
            



    def addLinkButtonPressed(self ,button):
        addlinkwindow = AddLinkWindow(self.callBack)
        self.addlinkwindows_list.append(addlinkwindow)
        self.addlinkwindows_list[len(self.addlinkwindows_list) - 1].show()

    def callBack(self , add_link_dictionary):
        gid = self.gidGenerator()

        download_info_file_list = ['***','waiting','***','***','***','***','***','***',gid , str(add_link_dictionary)]
        download_info_file = config_folder + "/download_info/" + gid
        os.system("touch " + download_info_file )
        f = Open(download_info_file , "w")
        for i in range(10):
            f.writelines(download_info_file_list[i] + "\n")

        f.close()
        
        self.download_table.insertRow(0)
        j = 0
        for i in download_info_file_list :
            item = QTableWidgetItem(i)
            self.download_table.setItem(0,j,item)
            j = j + 1

        f = Open (download_list_file , "a")
        f.writelines(gid + "\n")
        f.close()


        f = Open (download_list_file_active , "a")
        f.writelines(gid + "\n")
        f.close()
        new_download = DownloadLink(gid)
        self.threadPool.append(new_download)
        self.threadPool[len(self.threadPool) - 1].start()
        self.progressBarOpen(gid) 
        if add_link_dictionary['start_hour'] == None :
            message = "Download Starts"
        else:
            message = "Download Scheduled"
        notifySend(message ,'' , 10000 , 'no')

 

        
    def resumeButtonPressed(self,button):
        self.resumeAction.setEnabled(False)
        selected_row_return = self.selectedRow()
        if selected_row_return != None:
            gid = self.download_table.item(selected_row_return , 8 ).text()
            download_status = self.download_table.item(selected_row_return , 1).text()
 
                
            if download_status == "paused" :
                answer = download.downloadUnpause(gid)
                if answer == 'None':
                    notifySend("Aria2 did not respond!","Try agian!",10000,'warning' )



            else:
                new_download = DownloadLink(gid)
                self.threadPool.append(new_download)
                self.threadPool[len(self.threadPool) - 1].start()
                sleep(1)
                self.progressBarOpen(gid)




        else:
            self.statusbar.showMessage("Please select an item first!")


    def stopButtonPressed(self,button):
        self.stopAction.setEnabled(False)
        selected_row_return = self.selectedRow()
        if selected_row_return != None:
            gid = self.download_table.item(selected_row_return , 8 ).text()
            answer = download.downloadStop(gid)
            if answer == 'None':
                notifySend("Aria2 did not respond!","Try agian!" , 10000 , 'critical' )



           
               
        else:
            self.statusbar.showMessage("Please select an item first!")

    def pauseButtonPressed(self,button):
        self.pauseAction.setEnabled(False)
        selected_row_return = self.selectedRow()
        if selected_row_return != None:
            gid = self.download_table.item(selected_row_return , 8 ).text()
            answer = download.downloadPause(gid)
            if answer == 'None':
                notifySend("Aria2 did not respond!" , "Try agian!" , 10000 , 'critical' )

        else:
            self.statusbar.showMessage("Please select an item first!")
        sleep(1)

    def removeButtonPressed(self,button):
        self.removeAction.setEnabled(False)
        selected_row_return = self.selectedRow()
        if selected_row_return != None:
            gid = self.download_table.item(selected_row_return , 8 ).text()
            file_name = self.download_table.item(selected_row_return , 0).text()
            sleep(0.5)
            self.download_table.removeRow(selected_row_return)

#remove gid of download from download list file
            f = Open(download_list_file)
            download_list_file_lines = f.readlines()
            f.close()
            f = Open(download_list_file , "w")
            for i in download_list_file_lines:
                if i.strip() != gid:
                    f.writelines(i.strip() + "\n")
            f.close()
#remove gid of download from active download list file
            f = Open(download_list_file_active)
            download_list_file_active_lines = f.readlines()
            f.close()
            f = Open(download_list_file_active , "w")
            for i in download_list_file_active_lines:
                if i.strip() != gid:
                    f.writelines(i.strip() + "\n")
            f.close()
#remove download_info_file
            download_info_file = download_info_folder + "/" + gid
            f = Open(download_info_file)
            f.close()
            f.remove()
#remove file of download form download temp folder
            if file_name != '***' and status != 'complete' :
                file_name_path = temp_download_folder + "/" +  str(file_name)
                os.system('rm "' + str(file_name_path) +'"')
                file_name_aria = file_name_path + str('.aria2')
                os.system('rm "' + str(file_name_aria) +'"')
        else:
            self.statusbar.showMessage("Please select an item first!")
        self.selectedRow()

    def propertiesButtonPressed(self,button):
        self.propertiesAction.setEnabled(False)
        selected_row_return = self.selectedRow()
        if selected_row_return != None :
            add_link_dictionary_str = self.download_table.item(selected_row_return , 9).text() 
            add_link_dictionary = ast.literal_eval(add_link_dictionary_str) 
            gid = self.download_table.item(selected_row_return , 8 ).text()
            propertieswindow = PropertiesWindow(self.propertiesCallback ,gid)
            self.propertieswindows_list.append(propertieswindow)
            self.propertieswindows_list[len(self.propertieswindows_list) - 1].show()

    def propertiesCallback(self,add_link_dictionary , gid ):
        download_info_file = download_info_folder + "/" + gid
        f = Open(download_info_file)
        download_info_file_lines = f.readlines()
        f.close()
        f = Open(download_info_file , "w")
        for i in range(10):
            if i == 9 :
                f.writelines(str(add_link_dictionary) + "\n")
            else:
                f.writelines(download_info_file_lines[i].strip() + "\n")

        f.close()
            
    def progressButtonPressed(self,button):
        selected_row_return = self.selectedRow()
        if selected_row_return != None:
            gid = self.download_table.item(selected_row_return , 8 ).text()
            if gid in self.progress_window_list_dict :
                member_number = self.progress_window_list_dict[gid]
                if self.progress_window_list[member_number].isVisible() == False:
                    self.progress_window_list[member_number].show()
                else :
                    self.progress_window_list[member_number].hide()

    def progressBarOpen(self,gid):
        progress_window = ProgressWindow(parent = self,gid = gid)
        self.progress_window_list.append(progress_window)
        member_number = len(self.progress_window_list) - 1
        self.progress_window_list_dict[gid] = member_number 
        self.progress_window_list[member_number].show()
 
#close event
    def closeEvent(self, event):
        self.hide()
        self.system_tray_icon.hide()
        download.shutDown()
        sleep(0.5)
        global shutdown_notification
        shutdown_notification = 1
        while shutdown_notification != 2:
            sleep (0.1)

        QCoreApplication.instance().closeAllWindows()
        for qthread in self.threadPool :
            try:
                qthread.exit(0)
                sleep(0.1)
                answer = qthread.isRunning()
                print(answer)
            except:
                print("not quit")


        QCoreApplication.instance().quit
        print("Persepolis Closed")
        sys.exit(0)



    def systemTrayPressed(self,click):
        if click == 3 :
            self.minMaxTray(click)
            

    def minMaxTray(self,menu):
        if self.isVisible() == False:
            self.show()
            self.minimizeAction.setText('Minimize to system tray')
            self.minimizeAction.setIcon(QIcon(icons + 'minimize'))
        

        else :
            self.minimizeAction.setText('Show main Window')
            self.minimizeAction.setIcon(QIcon(icons + 'window'))
            self.hide()
    def stopAllDownloads(self,menu):
        active_gids = []
        for i in range(self.download_table.rowCount()):
            try:
                row_status = self.download_table.item(i , 1).text()
                if row_status == 'downloading' or row_status == 'paused' or row_status == 'waiting':
                    row_gid = self.download_table.item(i , 8).text()
                    active_gids.append(row_gid)
            except :
                pass
        for gid in active_gids:
            answer = download.downloadStop(gid)
            if answer == 'None':
                notifySend("Aria2 did not respond!" , "Try agian!" , 10000 , 'critical' )


            sleep(0.3)

           

    def pauseAllDownloads(self,menu):
#get active gid of downloads from aria
        active_gids = download.activeDownloads()
#check that if gid is in download_list_file_active
        f = Open(download_list_file_active)
        download_list_file_active_lines = f.readlines()
        f.close()
        for i in range(len(download_list_file_active_lines)):
            download_list_file_active_lines[i] = download_list_file_active_lines[i].strip()

        for gid in active_gids :
            if gid in download_list_file_active_lines :
                answer = download.downloadPause(gid)
                if answer == 'None':
                    notifySend("Aria2 did not respond!" , "Try agian!" , 10000 , 'critical' )

                sleep(0.3)
            

    def openPreferences(self,menu):
        self.preferenceswindow = PreferencesWindow(self)
        self.preferenceswindow.show()



    def openAbout(self,menu):
        self.about_window = AboutWindow()
        self.about_window.show()


    def openDefaultDownloadFolder(self,menu):
        f = Open(setting_file)
        setting_file_lines = f.readlines()
        f.close()
        setting_dict_str = str(setting_file_lines[0].strip())
        setting_dict = ast.literal_eval(setting_dict_str) 
        download_path = setting_dict ['download_path']
        if os.path.isdir(download_path):
            os.system("xdg-open '" + download_path + "'" )
        else:
            notifySend(str(download_path) ,'Not Found' , 5000 , 'warning' )




    def openDownloadFolder(self,menu):
        selected_row_return = self.selectedRow()
        if selected_row_return != None:
            gid = self.download_table.item(selected_row_return , 8 ).text()
            download_status = self.download_table.item(selected_row_return , 1).text()
            if download_status == 'complete':
                add_link_dictionary_str = self.download_table.item(selected_row_return , 9).text() 
                add_link_dictionary = ast.literal_eval(add_link_dictionary_str) 
                if 'file_path' in add_link_dictionary :
                    file_path = add_link_dictionary ['file_path']
                    file_path_split = file_path.split('/')
                    del file_path_split[-1]
                    download_path = '/'.join(file_path_split)
                    if os.path.isdir(download_path):
                        os.system("xdg-open '" + download_path + "'" )
                    else:
                        notifySend(str(download_path) ,'Not Found' , 5000 , 'warning' )



    def openFile(self,menu):
        selected_row_return = self.selectedRow()
        if selected_row_return != None:
            gid = self.download_table.item(selected_row_return , 8 ).text()
            download_status = self.download_table.item(selected_row_return , 1).text()
            if download_status == 'complete':
                add_link_dictionary_str = self.download_table.item(selected_row_return , 9).text() 
                add_link_dictionary = ast.literal_eval(add_link_dictionary_str) 
                if 'file_path' in add_link_dictionary:
                    file_path = add_link_dictionary['file_path']
                    if os.path.isfile(file_path):
                        os.system("xdg-open '" + file_path  + "' &" )
                    else:
                        notifySend(str(file_path) ,'Not Found' , 5000 , 'warning' )

    def deleteFile(self,menu):
        selected_row_return = self.selectedRow()
        if selected_row_return != None:
            gid = self.download_table.item(selected_row_return , 8 ).text()
            download_status = self.download_table.item(selected_row_return , 1).text()
            if download_status == 'complete':
                add_link_dictionary_str = self.download_table.item(selected_row_return , 9).text() 
                add_link_dictionary = ast.literal_eval(add_link_dictionary_str) 
                if 'file_path' in add_link_dictionary:
                    file_path = add_link_dictionary['file_path']
                    if os.path.isfile(file_path):
                        os.system("rm '" + file_path  + "'" )
                    else:
                        notifySend(str(file_path) ,'Not Found' , 5000 , 'warning' )

                    self.removeButtonPressed(menu)

    def selectDownloads(self,menu):
        if self.selectAction.isChecked() == True:
            for i in range(self.download_table.rowCount()):
                item = self.download_table.item(i , 0)
                item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                item.setCheckState(QtCore.Qt.Unchecked)
                self.selectAllAction.setEnabled(True)
                self.removeSelectedAction.setEnabled(True)
                self.deleteSelectedAction.setEnabled(True)
        else:
            for i in range(self.download_table.rowCount()):
                item_text = self.download_table.item(i , 0).text()
                item = QTableWidgetItem(item_text) 
                self.download_table.setItem(i , 0 , item)
                self.selectAllAction.setEnabled(False)
                self.removeSelectedAction.setEnabled(False)
                self.deleteSelectedAction.setEnabled(False)
                
 

    def selectAll(self,menu):
        for i in range(self.download_table.rowCount()):
            item = self.download_table.item(i , 0)
            item.setCheckState(QtCore.Qt.Checked)
 
    def removeSelected(self,menu):
        gid_list = []
        for row in range(self.download_table.rowCount()):
            status = self.download_table.item(row , 1).text() 
            item = self.download_table.item(row , 0)
            if (item.checkState() == 2) and (status == 'complete' or status == 'error' or status == 'stopped' ):
                gid = self.download_table.item(row , 8 ).text()
                gid_list.append(gid)


        for gid in gid_list:        
            for i in range(self.download_table.rowCount()):
                row_gid = self.download_table.item(i , 8).text()
                if gid == row_gid :
                    row = i 
                    break

           
            file_name = self.download_table.item(row , 0).text()
            sleep(0.5)
            self.download_table.removeRow(row)

#remove gid of download from download list file
            f = Open(download_list_file)
            download_list_file_lines = f.readlines()
            f.close()
            f = Open(download_list_file , "w")
            for i in download_list_file_lines:
                if i.strip() != gid:
                    f.writelines(i.strip() + "\n")
            f.close()
#remove gid of download from active download list file
            f = Open(download_list_file_active)
            download_list_file_active_lines = f.readlines()
            f.close()
            f = Open(download_list_file_active , "w")
            for i in download_list_file_active_lines:
                if i.strip() != gid:
                    f.writelines(i.strip() + "\n")
            f.close()
#remove download_info_file
            download_info_file = download_info_folder + "/" + gid
            f = Open(download_info_file)
            f.close()
            f.remove()
#remove file of download form download temp folder
            if file_name != '***' and status != 'complete' :
                file_name_path = temp_download_folder + "/" +  str(file_name)
                os.system('rm "' + str(file_name_path) +'"')
                file_name_aria = file_name_path + str('.aria2')
                os.system('rm "' + str(file_name_aria) +'"')

    def deleteSelected(self,menu):
        gid_list = []
        for row in range(self.download_table.rowCount()):
            status = self.download_table.item(row , 1).text() 
            item = self.download_table.item(row , 0)
            if (item.checkState() == 2) and (status == 'complete' or status == 'error' or status == 'stopped' ):
                gid = self.download_table.item(row , 8 ).text()
                gid_list.append(gid)


        for gid in gid_list:        
            for i in range(self.download_table.rowCount()):
                row_gid = self.download_table.item(i , 8).text()
                if gid == row_gid :
                    row = i 
                    break
            file_name = self.download_table.item(row , 0).text()
            add_link_dictionary_str = self.download_table.item(row , 9).text() 
            add_link_dictionary = ast.literal_eval(add_link_dictionary_str) 


            sleep(0.5)
            self.download_table.removeRow(row)
#remove gid of download from download list file
            f = Open(download_list_file)
            download_list_file_lines = f.readlines()
            f.close()
            f = Open(download_list_file , "w")
            for i in download_list_file_lines:
                if i.strip() != gid:
                    f.writelines(i.strip() + "\n")
            f.close()
#remove gid of download from active download list file
            f = Open(download_list_file_active)
            download_list_file_active_lines = f.readlines()
            f.close()
            f = Open(download_list_file_active , "w")
            for i in download_list_file_active_lines:
                if i.strip() != gid:
                    f.writelines(i.strip() + "\n")
            f.close()


#remove download_info_file
            download_info_file = download_info_folder + "/" + gid
            f = Open(download_info_file)
            f.close()
            f.remove()

#remove file of download form download temp folder
            if file_name != '***' and status != 'complete' :
                file_name_path = temp_download_folder + "/" +  str(file_name)
                os.system('rm "' + str(file_name_path) +'"')
                file_name_aria = file_name_path + str('.aria2')
                os.system('rm "' + str(file_name_aria) +'"')

#remove download file
            if status == 'complete':
                if 'file_path' in add_link_dictionary:
                    file_path = add_link_dictionary['file_path']
                    if os.path.isfile(file_path):
                        os.system("rm '" + file_path  + "'" )
                    else:
                        notifySend(str(file_path) ,'Not Found' , 5000 , 'warning' )


