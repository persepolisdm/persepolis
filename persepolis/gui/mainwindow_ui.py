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
from PyQt5.QtWidgets import QDoubleSpinBox, QPushButton, QComboBox,  QMenu, QTreeView, QSplitter, QSizePolicy, QGridLayout, QHBoxLayout, QVBoxLayout, QMenu, QTableWidgetItem, QAbstractItemView, QApplication, QToolBar, QMenuBar, QStatusBar, QTableWidget, QAction, QMainWindow, QWidget, QFrame, QAbstractItemView, QCheckBox, QSpinBox, QLabel
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtCore import QCoreApplication, QRect, QSize, Qt
import ast
import os
from persepolis.scripts.newopen import Open
from persepolis.gui import icons_resource


home_address = os.path.expanduser("~")


# align center for items in download table
class QTableWidgetItem(QTableWidgetItem):
    def __init__(self, input):
        super().__init__(input)
        self.setTextAlignment(0x0004 | 0x0080)

class MenuWidget(QPushButton):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        icons = ':/' + \
            str(self.parent.persepolis_setting.value('settings/icons')) + '/'

        # creating context menu
        self.menubar = QMenu(self)
        self.setMenu(self.menubar)
        self.setIcon(QIcon(icons + 'menu'))

        fileMenu = self.menubar.addMenu('File')
        editMenu = self.menubar.addMenu('Edit')
        viewMenu = self.menubar.addMenu('View')
        downloadMenu = self.menubar.addMenu('Download')
        queueMenu = self.menubar.addMenu('Queue')
        helpMenu = self.menubar.addMenu('Help')

        sortMenu = viewMenu.addMenu('Sort by')

        downloadMenu.addAction(self.parent.stopAllAction)

        sortMenu.addAction(self.parent.sort_file_name_Action)

        sortMenu.addAction(self.parent.sort_file_size_Action)

        sortMenu.addAction(self.parent.sort_first_try_date_Action)

        sortMenu.addAction(self.parent.sort_last_try_date_Action)

        sortMenu.addAction(self.parent.sort_download_status_Action)

        viewMenu.addAction(self.parent.trayAction)

        viewMenu.addAction(self.parent.showMenuBarAction)

        viewMenu.addAction(self.parent.showSidePanelAction)

        viewMenu.addAction(self.parent.minimizeAction)

        fileMenu.addAction(self.parent.addlinkAction)

        fileMenu.addAction(self.parent.addtextfileAction)

        downloadMenu.addAction(self.parent.resumeAction)

        downloadMenu.addAction(self.parent.pauseAction)

        downloadMenu.addAction(self.parent.stopAction)

        downloadMenu.addAction(self.parent.removeAction)

        downloadMenu.addAction(self.parent.propertiesAction)

        downloadMenu.addAction(self.parent.progressAction)

        fileMenu.addAction(self.parent.openFileAction)

        fileMenu.addAction(self.parent.openDownloadFolderAction)

        fileMenu.addAction(self.parent.deleteFileAction)

        fileMenu.addAction(self.parent.openDefaultDownloadFolderAction)

        fileMenu.addAction(self.parent.exitAction)

        editMenu.addAction(self.parent.selectAction)

        editMenu.addAction(self.parent.selectAllAction)

        editMenu.addAction(self.parent.removeSelectedAction)

        editMenu.addAction(self.parent.deleteSelectedAction)

        queueMenu.addAction(self.parent.createQueueAction)

        queueMenu.addAction(self.parent.removeQueueAction)

        queueMenu.addAction(self.parent.startQueueAction)

        queueMenu.addAction(self.parent.stopQueueAction)

        queueMenu.addAction(self.parent.moveUpAction)

        queueMenu.addAction(self.parent.moveDownAction)

        queueMenu.addAction(self.parent.moveUpSelectedAction)

        queueMenu.addAction(self.parent.moveDownSelectedAction)

        editMenu.addAction(self.parent.preferencesAction)

        helpMenu.addAction(self.parent.aboutAction)

        helpMenu.addAction(self.parent.issueAction)

        helpMenu.addAction(self.parent.updateAction)

        helpMenu.addAction(self.parent.logAction)

        helpMenu.addAction(self.parent.helpAction)


# viewMenu submenus

# DownloadTableWidget Class adds QMenu to QTableWidget Class
class DownloadTableWidget(QTableWidget):
    def __init__(self, parent):
        super().__init__()
# creating context menu
        self.tablewidget_menu = QMenu(self)
        self.sendMenu = self.tablewidget_menu.addMenu('')

    def contextMenuEvent(self, event):
        self.tablewidget_menu.popup(QtGui.QCursor.pos())


# CategoryTreeView Class adds QMenu to QTreeView
class CategoryTreeView(QTreeView):
    def __init__(self, parent):
        super().__init__()
# creating context menu
        self.category_tree_menu = QMenu(self)

# connecting actication  event
        self.activated.connect(parent.categoryTreeSelected)
        self.pressed.connect(parent.categoryTreeSelected)

    def contextMenuEvent(self, event):
        self.category_tree_menu.popup(QtGui.QCursor.pos())


class MainWindow_Ui(QMainWindow):
    def __init__(self, persepolis_setting):
        super().__init__()
# MainWindow
        self.persepolis_setting = persepolis_setting

        icons = ':/' + \
            str(self.persepolis_setting.value('settings/icons')) + '/'

        self.setWindowTitle("Persepolis Download Manager")
        self.setWindowIcon(QIcon.fromTheme('persepolis', QIcon(':/persepolis.svg')))

        self.centralwidget = QWidget(self)
        self.verticalLayout = QVBoxLayout(self.centralwidget)
# enable drag and drop
        self.setAcceptDrops(True)
# frame
        self.frame = QFrame(self.centralwidget)

# download_table_horizontalLayout
        download_table_horizontalLayout = QHBoxLayout()
        tabels_splitter = QSplitter(Qt.Horizontal)
# category_tree
        self.category_tree_qwidget = QWidget(self)
        category_tree_verticalLayout = QVBoxLayout()
        self.category_tree = CategoryTreeView(self)
        category_tree_verticalLayout.addWidget(self.category_tree)

        self.category_tree_model = QStandardItemModel()
        self.category_tree.setModel(self.category_tree_model)
        category_table_header = ['Category']
        self.category_tree_model.setHorizontalHeaderLabels(
            category_table_header)
        self.category_tree.header().setStretchLastSection(True)

        # inserting items in category_tree
        for item in ['All Downloads', 'Single Downloads']:
            qstandarditem = QStandardItem(item)
            font = QtGui.QFont()
            font.setBold(True)
            qstandarditem.setFont(font)
            qstandarditem.setEditable(False)
            self.category_tree_model.appendRow(qstandarditem)

# queue_panel
        self.queue_panel_widget = QWidget(self)

        queue_panel_verticalLayout_main = QVBoxLayout(self.queue_panel_widget)
# queue_panel_show_button
        self.queue_panel_show_button = QPushButton(self)

        queue_panel_verticalLayout_main.addWidget(self.queue_panel_show_button)
# queue_panel_widget_frame
        self.queue_panel_widget_frame = QFrame(self)
        self.queue_panel_widget_frame.setFrameShape(QFrame.StyledPanel)
        self.queue_panel_widget_frame.setFrameShadow(QFrame.Raised)

        queue_panel_verticalLayout_main.addWidget(
            self.queue_panel_widget_frame)

        queue_panel_verticalLayout = QVBoxLayout(self.queue_panel_widget_frame)
        queue_panel_verticalLayout_main.setContentsMargins(50, -1, 50, -1)

# start_end_frame
        self.start_end_frame = QFrame(self)

# start time
        start_verticalLayout = QVBoxLayout(self.start_end_frame)
        self.start_checkBox = QCheckBox(self)
        start_verticalLayout.addWidget(self.start_checkBox)

        self.start_frame = QFrame(self)
        self.start_frame.setFrameShape(QFrame.StyledPanel)
        self.start_frame.setFrameShadow(QFrame.Raised)

        start_frame_verticalLayout = QVBoxLayout(self.start_frame)
        horizontalLayout_5 = QHBoxLayout()

        self.start_hour_spinBox = QSpinBox(self.start_frame)
        self.start_hour_spinBox.setMaximum(23)
        horizontalLayout_5.addWidget(self.start_hour_spinBox)

        self.start_label = QLabel(self.start_frame)
        horizontalLayout_5.addWidget(self.start_label)

        self.start_minute_spinBox = QSpinBox(self.start_frame)
        self.start_minute_spinBox.setMaximum(59)
        horizontalLayout_5.addWidget(self.start_minute_spinBox)

        start_frame_verticalLayout.addLayout(horizontalLayout_5)

        start_verticalLayout.addWidget(self.start_frame)
# end time

        self.end_checkBox = QCheckBox(self)
        start_verticalLayout.addWidget(self.end_checkBox)

        self.end_frame = QFrame(self)
        self.end_frame.setFrameShape(QFrame.StyledPanel)
        self.end_frame.setFrameShadow(QFrame.Raised)

        end_frame_verticalLayout = QVBoxLayout(self.end_frame)
        horizontalLayout_6 = QHBoxLayout()

        self.end_hour_spinBox = QSpinBox(self.end_frame)
        self.end_hour_spinBox.setMaximum(23)
        horizontalLayout_6.addWidget(self.end_hour_spinBox)

        self.end_label = QLabel(self.end_frame)
        horizontalLayout_6.addWidget(self.end_label)

        self.end_minute_spinBox = QSpinBox(self.end_frame)
        self.end_minute_spinBox.setMaximum(59)
        horizontalLayout_6.addWidget(self.end_minute_spinBox)

        end_frame_verticalLayout.addLayout(horizontalLayout_6)

        start_verticalLayout.addWidget(self.end_frame)

        self.reverse_checkBox = QCheckBox(self)
        start_verticalLayout.addWidget(self.reverse_checkBox)

        queue_panel_verticalLayout.addWidget(self.start_end_frame)

# limit_after_frame
        self.limit_after_frame = QFrame(self)
# limit_checkBox
        limit_verticalLayout = QVBoxLayout(self.limit_after_frame)
        self.limit_checkBox = QCheckBox(self)
        limit_verticalLayout.addWidget(self.limit_checkBox)
# limit_frame
        self.limit_frame = QFrame(self)
        self.limit_frame.setFrameShape(QFrame.StyledPanel)
        self.limit_frame.setFrameShadow(QFrame.Raised)
        limit_verticalLayout.addWidget(self.limit_frame)

        limit_frame_verticalLayout = QVBoxLayout(self.limit_frame)
# limit_spinBox
        limit_frame_horizontalLayout = QHBoxLayout()
        self.limit_spinBox = QDoubleSpinBox(self)
        self.limit_spinBox.setMinimum(1)
        self.limit_spinBox.setMaximum(1023)
        limit_frame_horizontalLayout.addWidget(self.limit_spinBox)
# limit_comboBox
        self.limit_comboBox = QComboBox(self)
        self.limit_comboBox.addItem("")
        self.limit_comboBox.addItem("")
        limit_frame_horizontalLayout.addWidget(self.limit_comboBox)
        limit_frame_verticalLayout.addLayout(limit_frame_horizontalLayout)
# limit_pushButton
        self.limit_pushButton = QPushButton(self)
        limit_frame_verticalLayout.addWidget(self.limit_pushButton)

# after_checkBox
        self.after_checkBox = QtWidgets.QCheckBox(self)
        limit_verticalLayout.addWidget(self.after_checkBox)
# after_frame
        self.after_frame = QtWidgets.QFrame(self)
        self.after_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.after_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        limit_verticalLayout.addWidget(self.after_frame)

        after_frame_verticalLayout = QVBoxLayout(self.after_frame)
# after_comboBox
        self.after_comboBox = QComboBox(self)
        self.after_comboBox.addItem("")

        after_frame_verticalLayout.addWidget(self.after_comboBox)
# after_pushButton
        self.after_pushButton = QPushButton(self)
        after_frame_verticalLayout.addWidget(self.after_pushButton)

        queue_panel_verticalLayout.addWidget(self.limit_after_frame)
        category_tree_verticalLayout.addWidget(self.queue_panel_widget)

# keep_awake_checkBox
        self.keep_awake_checkBox = QCheckBox(self)
        queue_panel_verticalLayout.addWidget(self.keep_awake_checkBox)

        self.category_tree_qwidget.setLayout(category_tree_verticalLayout)
        tabels_splitter.addWidget(self.category_tree_qwidget)

# download table widget
        self.download_table_content_widget = QWidget(self)
        download_table_content_widget_verticalLayout = QVBoxLayout(
            self.download_table_content_widget)

        self.download_table = DownloadTableWidget(self)
        download_table_content_widget_verticalLayout.addWidget(
            self.download_table)
        tabels_splitter.addWidget(self.download_table_content_widget)

        self.download_table.setColumnCount(13)
        self.download_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.download_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.download_table.verticalHeader().hide()

# hide gid and download dictioanry section
        self.download_table.setColumnHidden(8, True)
        self.download_table.setColumnHidden(9, True)

        download_table_header = ['File Name', 'Status', 'Size', 'Downloaded', 'Percentage', 'Connections',
                                 'Transfer rate', 'Estimate time left', 'Gid', 'Link', 'First try date', 'Last try date', 'Category']
        self.download_table.setHorizontalHeaderLabels(download_table_header)

# fixing the size of download_table when window is Maximized!
        self.download_table.horizontalHeader().setSectionResizeMode(0)
        self.download_table.horizontalHeader().setStretchLastSection(True)

        tabels_splitter.setStretchFactor(0, 3) # category_tree width
        tabels_splitter.setStretchFactor(1, 10)  # ratio of tables's width
        download_table_horizontalLayout.addWidget(tabels_splitter)
        self.frame.setLayout(download_table_horizontalLayout)
        self.verticalLayout.addWidget(self.frame)
        self.setCentralWidget(self.centralwidget)

# menubar
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QRect(0, 0, 600, 24))
        self.setMenuBar(self.menubar)
        fileMenu = self.menubar.addMenu('&File')
        editMenu = self.menubar.addMenu('&Edit')
        viewMenu = self.menubar.addMenu('&View')
        downloadMenu = self.menubar.addMenu('&Download')
        queueMenu = self.menubar.addMenu('&Queue')
        helpMenu = self.menubar.addMenu('&Help')


# viewMenu submenus
        sortMenu = viewMenu.addMenu('Sort by')
# statusbar
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Persepolis Download Manager")
# toolBar
        self.toolBar2 = QToolBar(self)
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar2)
        self.toolBar2.setWindowTitle('Menu')
        self.toolBar2.setIconSize(QSize(38, 38))
        self.toolBar2.setFloatable(False)
        self.toolBar2.setMovable(False)

        self.toolBar = QToolBar(self)
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.toolBar.setWindowTitle('Toolbar')
        self.toolBar.setIconSize(QSize(38, 38))
        self.toolBar.setFloatable(False)
        self.toolBar.setMovable(False)


#toolBar and menubar and actions
        self.stopAllAction = QAction(QIcon(icons + 'stop_all'), 'Stop all active downloads',
                                     self, statusTip='Stop all active downloads', triggered=self.stopAllDownloads)
        downloadMenu.addAction(self.stopAllAction)

        self.sort_file_name_Action = QAction(
            'File name', self, triggered=self.sortByName)
        sortMenu.addAction(self.sort_file_name_Action)

        self.sort_file_size_Action = QAction(
            'File size', self, triggered=self.sortBySize)
        sortMenu.addAction(self.sort_file_size_Action)

        self.sort_first_try_date_Action = QAction(
            'First try date', self, triggered=self.sortByFirstTry)
        sortMenu.addAction(self.sort_first_try_date_Action)

        self.sort_last_try_date_Action = QAction(
            'Last try date', self, triggered=self.sortByLastTry)
        sortMenu.addAction(self.sort_last_try_date_Action)

        self.sort_download_status_Action = QAction(
            'Download status', self, triggered=self.sortByStatus)
        sortMenu.addAction(self.sort_download_status_Action)

        self.trayAction = QAction('Show system tray icon', self,
                                  statusTip="Show/Hide system tray icon", triggered=self.showTray)
        self.trayAction.setCheckable(True)
        viewMenu.addAction(self.trayAction)

        self.showMenuBarAction = QAction(
            'Show menubar', self, statusTip='Show menubar', triggered=self.showMenuBar)
        self.showMenuBarAction.setCheckable(True)
        viewMenu.addAction(self.showMenuBarAction)

        self.showSidePanelAction = QAction(
            'Show side panel', self, statusTip='Show side panel', triggered=self.showSidePanel)
        self.showSidePanelAction.setCheckable(True)
        viewMenu.addAction(self.showSidePanelAction)

        self.minimizeAction = QAction(QIcon(icons + 'minimize'), 'Minimize to system tray', self,
                                      shortcut="Ctrl+W", statusTip="Minimize to system tray", triggered=self.minMaxTray)
        viewMenu.addAction(self.minimizeAction)

        self.addlinkAction = QAction(QIcon(icons + 'add'), 'Add New Download Link', self,
                                     shortcut="Ctrl+N", statusTip="Add New Download Link", triggered=self.addLinkButtonPressed)
        fileMenu.addAction(self.addlinkAction)

        self.addtextfileAction = QAction(QIcon(icons + 'file'), 'Import links from text file', self,
                                         statusTip='Create a Text file and put links in it.line by line!', triggered=self.importText)
        fileMenu.addAction(self.addtextfileAction)

        self.resumeAction = QAction(QIcon(icons + 'play'), 'Resume Download', self,
                                    shortcut="Ctrl+R", statusTip="Resume Download", triggered=self.resumeButtonPressed)
        downloadMenu.addAction(self.resumeAction)

        self.pauseAction = QAction(QIcon(icons + 'pause'), 'Pause Download', self,
                                   shortcut="Ctrl+C", statusTip="Pause Download", triggered=self.pauseButtonPressed)
        downloadMenu.addAction(self.pauseAction)

        self.stopAction = QAction(QIcon(icons + 'stop'), 'Stop Download', self, shortcut="Ctrl+S",
                                  statusTip="Stop/Cancel Download", triggered=self.stopButtonPressed)
        downloadMenu.addAction(self.stopAction)

        self.removeAction = QAction(QIcon(icons + 'remove'), 'Remove Download', self,
                                    shortcut="Ctrl+D", statusTip="Remove Download", triggered=self.removeButtonPressed)
        downloadMenu.addAction(self.removeAction)

        self.propertiesAction = QAction(QIcon(icons + 'setting'), 'Properties', self,
                                        shortcut="Ctrl+P", statusTip="Properties", triggered=self.propertiesButtonPressed)
        downloadMenu.addAction(self.propertiesAction)

        self.progressAction = QAction(QIcon(icons + 'window'), 'Progress', self,
                                      shortcut="Ctrl+Z", statusTip="Progress", triggered=self.progressButtonPressed)
        downloadMenu.addAction(self.progressAction)

        self.openFileAction = QAction(QIcon(
            icons + 'file'), 'Open file', self, statusTip='Open file', triggered=self.openFile)
        fileMenu.addAction(self.openFileAction)

        self.openDownloadFolderAction = QAction(QIcon(
            icons + 'folder'), 'Open download folder', self, statusTip='Open download folder', triggered=self.openDownloadFolder)
        fileMenu.addAction(self.openDownloadFolderAction)

        self.deleteFileAction = QAction(QIcon(
            icons + 'trash'), 'Delete file', self, statusTip='Delete file', triggered=self.deleteFile)
        fileMenu.addAction(self.deleteFileAction)

        self.openDefaultDownloadFolderAction = QAction(QIcon(
            icons + 'folder'), 'Open default download folder', self, statusTip='Open default download folder', triggered=self.openDefaultDownloadFolder)
        fileMenu.addAction(self.openDefaultDownloadFolderAction)

        self.exitAction = QAction(QIcon(icons + 'exit'), 'Exit', self,
                                  shortcut="Ctrl+Q", statusTip="Exit", triggered=self.closeEvent)
        fileMenu.addAction(self.exitAction)

        self.selectAction = QAction('Select multiple items ', self,
                                    statusTip='Select multiple items', triggered=self.selectDownloads)
        self.selectAction.setCheckable(True)
        editMenu.addAction(self.selectAction)

        self.selectAllAction = QAction(QIcon(
            icons + 'select_all'), 'Select All', self, statusTip='Select All', triggered=self.selectAll)
        editMenu.addAction(self.selectAllAction)
        self.selectAllAction.setEnabled(False)

        self.removeSelectedAction = QAction(QIcon(icons + 'multi_remove'), 'Remove selected downloads form list',
                                            self, statusTip='Remove selected downloads form list', triggered=self.removeSelected)
        editMenu.addAction(self.removeSelectedAction)
        self.removeSelectedAction.setEnabled(False)

        self.deleteSelectedAction = QAction(QIcon(icons + 'multi_trash'), 'Delete selected download files',
                                            self, statusTip='Delete selected download files', triggered=self.deleteSelected)
        editMenu.addAction(self.deleteSelectedAction)
        self.deleteSelectedAction.setEnabled(False)

        self.createQueueAction = QAction(QIcon(icons + 'add_queue'), 'Create new queue',
                                         self, statusTip='Create new download queue', triggered=self.createQueue)
        queueMenu.addAction(self.createQueueAction)

        self.removeQueueAction = QAction(QIcon(icons + 'remove_queue'), 'Remove this queue',
                                         self, statusTip='Remove this queue', triggered=self.removeQueue)
        queueMenu.addAction(self.removeQueueAction)

        self.startQueueAction = QAction(QIcon(
            icons + 'start_queue'), 'Start this queue', self, statusTip='Start this queue', triggered=self.startQueue)
        queueMenu.addAction(self.startQueueAction)

        self.stopQueueAction = QAction(QIcon(
            icons + 'stop_queue'), 'Stop this queue', self, statusTip='Stop this queue', triggered=self.stopQueue)
        queueMenu.addAction(self.stopQueueAction)

        self.moveUpAction = QAction(QIcon(icons + 'up'), 'Move up this item', self,
                                    statusTip='Move currently selected item up by one row', triggered=self.moveUp)
        queueMenu.addAction(self.moveUpAction)

        self.moveDownAction = QAction(QIcon(icons + 'down'), 'Move down this item', self,
                                      statusTip='Move currently selected item down by one row', triggered=self.moveDown)
        queueMenu.addAction(self.moveDownAction)

        self.moveUpSelectedAction = QAction(QIcon(icons + 'multi_up'), 'Move up selected items', self,
                                            statusTip='Move currently selected items up by one row', triggered=self.moveUpSelected)
        queueMenu.addAction(self.moveUpSelectedAction)

        self.moveDownSelectedAction = QAction(QIcon(icons + 'multi_down'), 'Move down selected items',
                                              self, statusTip='Move currently selected items down by one row', triggered=self.moveDownSelected)
        queueMenu.addAction(self.moveDownSelectedAction)

        self.preferencesAction = QAction(QIcon(icons + 'preferences'), 'Preferences',
                                         self, statusTip='Preferences', triggered=self.openPreferences, menuRole=5)
        editMenu.addAction(self.preferencesAction)

        self.aboutAction = QAction(QIcon(
            icons + 'about'), 'About', self, statusTip='About', triggered=self.openAbout, menuRole=4)
        helpMenu.addAction(self.aboutAction)

        self.issueAction = QAction(QIcon(icons + 'about'), 'Report an issue',
                                   self, statusTip='Report an issue', triggered=self.reportIssue)
        helpMenu.addAction(self.issueAction)

        self.updateAction = QAction(QIcon(icons + 'about'), 'Check for newer version',
                                    self, statusTip='Check for newer release', triggered=self.newUpdate)
        helpMenu.addAction(self.updateAction)

        self.logAction = QAction(QIcon(icons + 'about'), 'Show log file',
                                   self, statusTip='Help', triggered=self.showLog)
        helpMenu.addAction(self.logAction)



        self.helpAction = QAction(QIcon(icons + 'about'), 'Help',
                                   self, statusTip='Help', triggered=self.persepolisHelp)
        helpMenu.addAction(self.helpAction)



        self.qmenu = MenuWidget(self)

        self.toolBar2.addWidget(self.qmenu)

# labels
        self.queue_panel_show_button.setText("Hide options")
        self.start_checkBox.setText("Start Time")
        self.start_label.setText(":")

        self.end_checkBox.setText("End Time")
        self.end_label.setText(":")

        self.reverse_checkBox.setText("Download bottom of\n the list first")

        self.limit_checkBox.setText("Limit Speed")
        self.limit_comboBox.setItemText(0,  "KB/S")
        self.limit_comboBox.setItemText(1,  "MB/S")
        self.limit_pushButton.setText("Apply")

        self.after_checkBox.setText("After download")
        self.after_comboBox.setItemText(0,  "Shut Down")

        self.keep_awake_checkBox.setText("Keep system awake!")
        self.keep_awake_checkBox.setToolTip(
            "<html><head/><body><p>This option is preventing system from going to sleep.\
            This is necessary if your power manager is suspending system automatically. </p></body></html>")
 
        self.after_pushButton.setText("Apply")

    def changeIcon(self, icons):
        icons = ':/' + str(icons) + '/'

        action_icon_dict = {self.stopAllAction: 'stop_all', self.minimizeAction: 'minimize', self.addlinkAction: 'add', self.addtextfileAction: 'file', self.resumeAction: 'play', self.pauseAction: 'pause', self.stopAction: 'stop', self.removeAction: 'remove', self.propertiesAction: 'setting', self.progressAction: 'window', self.openFileAction: 'file', self.openDownloadFolderAction: 'folder', self.deleteFileAction: 'trash', self.openDefaultDownloadFolderAction: 'folder', self.exitAction: 'exit',
                            self.selectAllAction: 'select_all', self.removeSelectedAction: 'multi_remove', self.deleteSelectedAction: 'multi_trash', self.createQueueAction: 'add_queue', self.removeQueueAction: 'remove_queue', self.startQueueAction: 'start_queue', self.stopQueueAction: 'stop_queue', self.moveUpAction: 'up', self.moveDownAction: 'down', self.preferencesAction: 'preferences', self.aboutAction: 'about', self.issueAction: 'about', self.updateAction: 'about', self.qmenu: 'menu'}
        for key in action_icon_dict.keys():
            key.setIcon(QIcon(icons + str(action_icon_dict[key])))
