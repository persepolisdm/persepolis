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
from PyQt5.QtWidgets import QGridLayout , QVBoxLayout , QMenu , QTableWidgetItem ,QAbstractItemView , QApplication , QToolBar , QMenuBar , QStatusBar, QTableWidget , QAction , QMainWindow , QWidget , QFrame , QAbstractItemView
from PyQt5.QtGui import QIcon  
from PyQt5.QtCore import QCoreApplication , QRect , QSize  
import ast , os
from newopen import Open
import icons_resource

home_address = os.path.expanduser("~")
config_folder = str(home_address) + "/.config/persepolis_download_manager"

#setting
setting_file = config_folder + '/setting'
f = Open(setting_file)
setting_file_lines = f.readlines()
f.close()
setting_dict_str = str(setting_file_lines[0].strip())
setting_dict = ast.literal_eval(setting_dict_str) 

icons = ':/' + str(setting_dict['icons']) + '/'


class MainWindow_Ui(QMainWindow):
    def __init__(self):
        super().__init__()
#MainWindow
#finding windows_size
        windows_size = config_folder + '/windows_size'
        f = Open(windows_size)
        windows_size_file_lines = f.readlines()
        f.close()
        windows_size_dict_str = str(windows_size_file_lines[0].strip())
        windows_size_dict = ast.literal_eval(windows_size_dict_str) 
        MainWindow_Ui_size = windows_size_dict['MainWindow_Ui']

        self.resize(int(MainWindow_Ui_size[0]),int(MainWindow_Ui_size[1]) )
        self.setWindowTitle("Persepolis Download Manager")
        self.setWindowIcon(QIcon.fromTheme('persepolis',QIcon(':/icon.svg') ))
       
        self.centralwidget = QWidget(self)
        self.verticalLayout = QVBoxLayout(self.centralwidget)
#enable drag and drop 
        self.setAcceptDrops(True)
#frame
        self.frame = QFrame(self.centralwidget)


#tablewidget
        self.download_table = QTableWidget(self.frame)
        self.download_table_verticalLayout = QVBoxLayout()
        self.download_table_verticalLayout.addWidget(self.download_table)
        self.download_table.setColumnCount(12)
        self.download_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.download_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.download_table.verticalHeader().hide()
#hide gid and download dictioanry section
        self.download_table.setColumnHidden(8 , True)
        self.download_table.setColumnHidden(9 , True)

        self.frame.setLayout(self.download_table_verticalLayout)
        self.verticalLayout.addWidget(self.frame)
 
        self.setCentralWidget(self.centralwidget)

        download_table_header = ['File Name' , 'Status' , 'Size' , 'Downloaded' , 'Percentage' , 'Connections' , 'Transfer rate' , 'Estimate time left' , 'Gid' , 'Info' , 'First try date' , 'Last try date']
        self.download_table.setHorizontalHeaderLabels(download_table_header)    
#fixing the size of download_table when window is Maximized!
        self.download_table.horizontalHeader().setSectionResizeMode(0)
        self.download_table.horizontalHeader().setStretchLastSection(True)
#finding number od row that user selected!
        self.download_table.itemSelectionChanged.connect(self.selectedRow)
   



#menubar
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QRect(0, 0, 600, 24))
        self.setMenuBar(self.menubar)
        fileMenu = self.menubar.addMenu('File')
        editMenu = self.menubar.addMenu('Edit')
        viewMenu = self.menubar.addMenu('View')
        downloadMenu = self.menubar.addMenu('Download')
        helpMenu = self.menubar.addMenu('Help')


#statusbar
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Persepolis Download Manager")
#toolBar
        self.toolBar = QToolBar(self)
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.toolBar.setWindowTitle("toolBar")
        self.toolBar.setIconSize(QSize(38 , 38))
        self.toolBar.setFloatable(False)
        self.toolBar.setMovable(False)

#toolBar and menubar and actions
        self.stopAllAction = QAction(QIcon(icons + 'stop_all') , 'Stop all active downloads' , self , statusTip = 'Stop all active downloads', triggered = self.stopAllDownloads )
        downloadMenu.addAction(self.stopAllAction)

        self.pauseAllAction = QAction(QIcon(icons + 'pause_all') , 'Pause all active downloads' , self , statusTip = 'Pause all active downloads', triggered = self.pauseAllDownloads )
        downloadMenu.addAction(self.pauseAllAction)

        self.trayAction = QAction('Show system tray icon' , self  , statusTip = "Show/Hide system tray icon" , triggered = self.showTray) 
        self.trayAction.setCheckable(True)
        self.trayAction.setChecked(True)
        viewMenu.addAction(self.trayAction)



        self.minimizeAction = QAction(QIcon(icons + 'minimize') , 'Minimize to system tray' , self , shortcut = "Ctrl+W" , statusTip = "Minimize to system tray" , triggered = self.minMaxTray) 
        viewMenu.addAction(self.minimizeAction)

    

        self.addlinkAction = QAction(QIcon(icons + 'add') , 'Add New Download Link' , self , shortcut = "Ctrl+N" , statusTip = "Add New Download Link" , triggered = self.addLinkButtonPressed) 
        fileMenu.addAction(self.addlinkAction)


        self.resumeAction = QAction(QIcon(icons + 'play') , 'Resume Download' , self , shortcut = "Ctrl+R" , statusTip = "Resume Download" , triggered = self.resumeButtonPressed)
        downloadMenu.addAction(self.resumeAction)


        self.pauseAction = QAction(QIcon(icons + 'pause') , 'Pause Download' , self , shortcut = "Ctrl+C" , statusTip = "Pause Download" , triggered = self.pauseButtonPressed)
        downloadMenu.addAction(self.pauseAction)

       

        self.stopAction = QAction(QIcon(icons + 'stop') , 'Stop Download' , self , shortcut = "Ctrl+S" , statusTip = "Stop/Cancel Download" , triggered = self.stopButtonPressed)
        downloadMenu.addAction(self.stopAction)

        self.removeAction = QAction(QIcon(icons + 'remove') , 'Remove Download' , self , shortcut = "Ctrl+D" , statusTip = "Remove Download" , triggered = self.removeButtonPressed)
        downloadMenu.addAction(self.removeAction)

        self.propertiesAction = QAction(QIcon(icons + 'setting') , 'Properties' , self , shortcut = "Ctrl+P" , statusTip = "Properties" , triggered = self.propertiesButtonPressed )
        downloadMenu.addAction(self.propertiesAction)

        self.progressAction = QAction(QIcon(icons + 'window') , 'Progress' , self , shortcut = "Ctrl+Z" , statusTip = "Progress" , triggered = self.progressButtonPressed )
        downloadMenu.addAction(self.progressAction)

        self.openFileAction = QAction(QIcon(icons + 'file') , 'Open file' , self , statusTip = 'Open file', triggered = self.openFile )
        fileMenu.addAction(self.openFileAction)

        self.openDownloadFolderAction = QAction(QIcon(icons + 'folder') , 'Open download folder' , self , statusTip = 'Open download folder', triggered = self.openDownloadFolder )
        fileMenu.addAction(self.openDownloadFolderAction)

        self.deleteFileAction = QAction(QIcon(icons + 'trash') , 'delete file' , self , statusTip = 'delete file', triggered = self.deleteFile )
        fileMenu.addAction(self.deleteFileAction)
 

        self.openDefaultDownloadFolderAction = QAction(QIcon(icons + 'folder') , 'Open default download folder' , self , statusTip = 'Open default download folder', triggered = self.openDefaultDownloadFolder )
        fileMenu.addAction(self.openDefaultDownloadFolderAction)
   
        self.exitAction = QAction(QIcon(icons + 'exit') , 'Exit' , self , shortcut = "Ctrl+Q" , statusTip = "Exit" , triggered = self.closeEvent)
        fileMenu.addAction(self.exitAction)

        self.selectAction = QAction('Enable selectection mode' , self , statusTip = 'Select Downloads' , triggered = self.selectDownloads)
        self.selectAction.setCheckable(True)
        editMenu.addAction(self.selectAction)

        self.selectAllAction = QAction(QIcon(icons + 'select_all') , 'Select All' , self , statusTip = 'Select All' , triggered = self.selectAll)
        editMenu.addAction(self.selectAllAction)
        self.selectAllAction.setEnabled(False)

        self.removeSelectedAction = QAction(QIcon(icons + 'multi_remove') , 'Remove selected downloads form list' , self , statusTip = 'Remove selected downloads form list' , triggered = self.removeSelected)
        editMenu.addAction(self.removeSelectedAction)
        self.removeSelectedAction.setEnabled(False)

        self.deleteSelectedAction = QAction(QIcon(icons + 'multi_trash') , 'Delete selected download files' , self , statusTip = 'Delete selected download files' , triggered = self.deleteSelected)
        editMenu.addAction(self.deleteSelectedAction)
        self.deleteSelectedAction.setEnabled(False)




        self.preferencesAction = QAction(QIcon(icons + 'preferences') , 'Preferences' , self , statusTip = 'Preferences' , triggered = self.openPreferences)
        editMenu.addAction(self.preferencesAction)

        self.aboutAction = QAction(QIcon(icons + 'about') , 'About' , self , statusTip = 'About' , triggered = self.openAbout)
        helpMenu.addAction(self.aboutAction)
        


        


        for i in self.addlinkAction,self.resumeAction, self.pauseAction , self.stopAction, self.removeAction , self.deleteFileAction , self.propertiesAction, self.progressAction ,self.minimizeAction , self.exitAction :
            self.toolBar.addAction(i)
         

        self.toolBar.insertSeparator(self.addlinkAction)
        self.toolBar.insertSeparator(self.resumeAction)     
        self.toolBar.insertSeparator(self.removeAction)
        self.toolBar.insertSeparator(self.exitAction)
        self.toolBar.addSeparator()
        
