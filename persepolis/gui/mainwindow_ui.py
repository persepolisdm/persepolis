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
try:
    from PySide6.QtWidgets import QHeaderView, QDoubleSpinBox, QPushButton, QComboBox,  QMenu, QTreeView, QSplitter, QSizePolicy, QGridLayout, QHBoxLayout, QVBoxLayout, QMenu, QTableWidgetItem, QAbstractItemView, QApplication, QToolBar, QMenuBar, QStatusBar, QTableWidget, QMainWindow, QWidget, QFrame, QAbstractItemView, QCheckBox, QSpinBox, QLabel
    from PySide6.QtGui import QShortcut, QAction, QCursor, QKeySequence, QIcon, QStandardItemModel, QStandardItem
    from PySide6.QtCore import QCoreApplication, QRect, QSize, Qt, QTranslator, QLocale
except:
    from PyQt5.QtWidgets import QHeaderView, QShortcut, QDoubleSpinBox, QPushButton, QComboBox,  QMenu, QTreeView, QSplitter, QSizePolicy, QGridLayout, QHBoxLayout, QVBoxLayout, QMenu, QTableWidgetItem, QAbstractItemView, QApplication, QToolBar, QMenuBar, QStatusBar, QTableWidget, QAction, QMainWindow, QWidget, QFrame, QAbstractItemView, QCheckBox, QSpinBox, QLabel
    from PyQt5.QtGui import QCursor, QKeySequence, QIcon, QStandardItemModel, QStandardItem
    from PyQt5.QtCore import QCoreApplication, QRect, QSize, Qt, QTranslator, QLocale

from persepolis.gui import resources
from persepolis.gui.customized_widgets import MyQDateTimeEdit

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

        # add support for other languages
        locale = str(self.parent.persepolis_setting.value('settings/locale'))
        QLocale.setDefault(QLocale(locale))
        self.translator = QTranslator()
        if self.translator.load(':/translations/locales/ui_' + locale, 'ts'):
            QCoreApplication.installTranslator(self.translator)

        # set ui direction
        ui_direction = self.parent.persepolis_setting.value('ui_direction')

        if ui_direction == 'rtl':
            self.setLayoutDirection(Qt.RightToLeft)

        elif ui_direction in 'ltr':
            self.setLayoutDirection(Qt.LeftToRight)

        # creating context menu
        self.menubar = QMenu(self)
        self.setMenu(self.menubar)
        self.setIcon(QIcon(icons + 'menu'))
        self.setStyleSheet("""QPushButton{border: none; background-color: transparent; padding: 0px}""")

        fileMenu = self.menubar.addMenu(QCoreApplication.translate("mainwindow_ui_tr", 'File'))
        editMenu = self.menubar.addMenu(QCoreApplication.translate("mainwindow_ui_tr", 'Edit'))
        viewMenu = self.menubar.addMenu(QCoreApplication.translate("mainwindow_ui_tr", 'View'))
        downloadMenu = self.menubar.addMenu(QCoreApplication.translate("mainwindow_ui_tr", 'Download'))
        queueMenu = self.menubar.addMenu(QCoreApplication.translate("mainwindow_ui_tr", 'Queue'))
        videoFinderMenu = self.menubar.addMenu(QCoreApplication.translate("mainwindow_ui_tr", 'Video Finder'))
        helpMenu = self.menubar.addMenu(QCoreApplication.translate("mainwindow_ui_tr", 'Help'))

        sortMenu = viewMenu.addMenu(QCoreApplication.translate("mainwindow_ui_tr", 'Sort by'))

        videoFinderMenu.addAction(self.parent.videoFinderAddLinkAction)

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

        downloadMenu.addAction(self.parent.propertiesAction)

        downloadMenu.addAction(self.parent.progressAction)

        fileMenu.addAction(self.parent.openFileAction)

        fileMenu.addAction(self.parent.openDownloadFolderAction)

        fileMenu.addAction(self.parent.openDefaultDownloadFolderAction)

        fileMenu.addAction(self.parent.exitAction)

        editMenu.addAction(self.parent.clearAction)

        editMenu.addAction(self.parent.removeSelectedAction)

        editMenu.addAction(self.parent.deleteSelectedAction)

        queueMenu.addAction(self.parent.createQueueAction)

        queueMenu.addAction(self.parent.removeQueueAction)

        queueMenu.addAction(self.parent.startQueueAction)

        queueMenu.addAction(self.parent.stopQueueAction)

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

        # set ui direction
        ui_direction = parent.persepolis_setting.value('ui_direction')

        if ui_direction == 'rtl':
            self.setLayoutDirection(Qt.RightToLeft)

        elif ui_direction in 'ltr':
            self.setLayoutDirection(Qt.LeftToRight)

        # creating context menu
        self.tablewidget_menu = QMenu(self)
        self.sendMenu = self.tablewidget_menu.addMenu('')

    def contextMenuEvent(self, event):
        self.tablewidget_menu.popup(QCursor.pos())


# CategoryTreeView Class adds QMenu to QTreeView
class CategoryTreeView(QTreeView):
    def __init__(self, parent):
        super().__init__()

        # set ui direction
        ui_direction = parent.persepolis_setting.value('ui_direction')

        if ui_direction == 'rtl':
            self.setLayoutDirection(Qt.RightToLeft)

        elif ui_direction in 'ltr':
            self.setLayoutDirection(Qt.LeftToRight)

        # creating context menu
        self.category_tree_menu = QMenu(self)

        # connecting activation  event
        self.activated.connect(parent.categoryTreeSelected)
        self.pressed.connect(parent.categoryTreeSelected)

    def contextMenuEvent(self, event):
        self.category_tree_menu.popup(QCursor.pos())


class MainWindow_Ui(QMainWindow):
    def __init__(self, persepolis_setting):
        super().__init__()
        # MainWindow
        self.persepolis_setting = persepolis_setting

        # add support for other languages
        locale = str(self.persepolis_setting.value('settings/locale'))
        QLocale.setDefault(QLocale(locale))
        self.translator = QTranslator()
        if self.translator.load(':/translations/locales/ui_' + locale, 'ts'):
            QCoreApplication.installTranslator(self.translator)

        # set ui direction
        ui_direction = self.persepolis_setting.value('ui_direction')

        if ui_direction == 'rtl':
            self.setLayoutDirection(Qt.RightToLeft)

        elif ui_direction in 'ltr':
            self.setLayoutDirection(Qt.LeftToRight)

        icons = ':/' + \
            str(self.persepolis_setting.value('settings/icons')) + '/'

        self.setWindowTitle(QCoreApplication.translate("mainwindow_ui_tr", "Persepolis Download Manager"))
        self.setWindowIcon(QIcon.fromTheme('persepolis', QIcon(':/persepolis.svg')))

        self.centralwidget = QWidget(self)
        self.verticalLayout = QVBoxLayout(self.centralwidget)

        # enable drag and drop
        self.setAcceptDrops(True)

        # frame
        self.frame = QFrame(self.centralwidget)

        # download_table_horizontalLayout
        download_table_horizontalLayout = QHBoxLayout()
        horizontal_splitter = QSplitter(Qt.Horizontal)

        vertical_splitter = QSplitter(Qt.Vertical)

        # category_tree
        self.category_tree_qwidget = QWidget(self)
        category_tree_verticalLayout = QVBoxLayout()
        self.category_tree = CategoryTreeView(self)
        category_tree_verticalLayout.addWidget(self.category_tree)

        self.category_tree_model = QStandardItemModel()
        self.category_tree.setModel(self.category_tree_model)
        category_table_header = [QCoreApplication.translate("mainwindow_ui_tr", 'Category')]

        self.category_tree_model.setHorizontalHeaderLabels(
            category_table_header)
        self.category_tree.header().setStretchLastSection(True)

        self.category_tree.header().setDefaultAlignment(Qt.AlignCenter)

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

        self.start_time_qDataTimeEdit = MyQDateTimeEdit(self.start_frame)
        self.start_time_qDataTimeEdit.setDisplayFormat('H:mm')
        start_frame_verticalLayout.addWidget(self.start_time_qDataTimeEdit)

        start_verticalLayout.addWidget(self.start_frame)

        # end time
        self.end_checkBox = QCheckBox(self)
        start_verticalLayout.addWidget(self.end_checkBox)

        self.end_frame = QFrame(self)
        self.end_frame.setFrameShape(QFrame.StyledPanel)
        self.end_frame.setFrameShadow(QFrame.Raised)

        end_frame_verticalLayout = QVBoxLayout(self.end_frame)

        self.end_time_qDateTimeEdit = MyQDateTimeEdit(self.end_frame)
        self.end_time_qDateTimeEdit.setDisplayFormat('H:mm')
        end_frame_verticalLayout.addWidget(self.end_time_qDateTimeEdit)

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
        self.after_checkBox = QCheckBox(self)
        limit_verticalLayout.addWidget(self.after_checkBox)

        # after_frame
        self.after_frame = QFrame(self)
        self.after_frame.setFrameShape(QFrame.StyledPanel)
        self.after_frame.setFrameShadow(QFrame.Raised)
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
        horizontal_splitter.addWidget(self.category_tree_qwidget)

        # download table widget
        self.download_table_content_widget = QWidget(self)
        download_table_content_widget_verticalLayout = QVBoxLayout(
            self.download_table_content_widget)

        # download_table
        self.download_table = DownloadTableWidget(self)
        vertical_splitter.addWidget(self.download_table)

        horizontal_splitter.addWidget(self.download_table_content_widget)

        self.download_table.setColumnCount(13)
        self.download_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.download_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.download_table.verticalHeader().hide()

        # hide column of GID and column of link.
        self.download_table.setColumnHidden(8, True)
        self.download_table.setColumnHidden(9, True)

        download_table_header = [QCoreApplication.translate("mainwindow_ui_tr", 'File Name'), QCoreApplication.translate("mainwindow_ui_tr", 'Status'), QCoreApplication.translate("mainwindow_ui_tr", 'Size'), QCoreApplication.translate("mainwindow_ui_tr", 'Downloaded'), QCoreApplication.translate("mainwindow_ui_tr", 'Percentage'), QCoreApplication.translate("mainwindow_ui_tr", 'Connections'),
                                 QCoreApplication.translate("mainwindow_ui_tr", 'Transfer Rate'), QCoreApplication.translate("mainwindow_ui_tr", 'Estimated Time Left'), 'Gid', QCoreApplication.translate("mainwindow_ui_tr", 'Link'), QCoreApplication.translate("mainwindow_ui_tr", 'First Try Date'), QCoreApplication.translate("mainwindow_ui_tr", 'Last Try Date'), QCoreApplication.translate("mainwindow_ui_tr", 'Category')]

        self.download_table.setHorizontalHeaderLabels(download_table_header)

        # fixing the size of download_table when window is Maximized!
        self.download_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.download_table.horizontalHeader().setStretchLastSection(True)

        horizontal_splitter.setStretchFactor(0, 3)  # category_tree width
        horizontal_splitter.setStretchFactor(1, 10)  # ratio of tables's width

        # video_finder_widget
        self.video_finder_widget = QWidget(self)
        video_finder_horizontalLayout = QHBoxLayout(self.video_finder_widget)

        self.muxing_pushButton = QPushButton(self)
        self.muxing_pushButton.setIcon(QIcon(icons + 'video_finder'))
        video_finder_horizontalLayout.addWidget(self.muxing_pushButton)
        video_finder_horizontalLayout.addSpacing(20)

        video_audio_verticalLayout = QVBoxLayout()

        self.video_label = QLabel(self)
        video_audio_verticalLayout.addWidget(self.video_label)

        self.audio_label = QLabel(self)
        video_audio_verticalLayout.addWidget(self.audio_label)
        video_finder_horizontalLayout.addLayout(video_audio_verticalLayout)

        status_muxing_verticalLayout = QVBoxLayout()

        self.video_finder_status_label = QLabel(self)
        status_muxing_verticalLayout.addWidget(self.video_finder_status_label)

        self.muxing_status_label = QLabel(self)
        status_muxing_verticalLayout.addWidget(self.muxing_status_label)
        video_finder_horizontalLayout.addLayout(status_muxing_verticalLayout)

        vertical_splitter.addWidget(self.video_finder_widget)

        download_table_content_widget_verticalLayout.addWidget(vertical_splitter)

        download_table_horizontalLayout.addWidget(horizontal_splitter)

        self.frame.setLayout(download_table_horizontalLayout)

        self.verticalLayout.addWidget(self.frame)

        self.setCentralWidget(self.centralwidget)

        # menubar
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QRect(0, 0, 600, 24))
        self.setMenuBar(self.menubar)
        fileMenu = self.menubar.addMenu(QCoreApplication.translate("mainwindow_ui_tr", '&File'))
        editMenu = self.menubar.addMenu(QCoreApplication.translate("mainwindow_ui_tr", '&Edit'))
        viewMenu = self.menubar.addMenu(QCoreApplication.translate("mainwindow_ui_tr", '&View'))
        downloadMenu = self.menubar.addMenu(QCoreApplication.translate("mainwindow_ui_tr", '&Download'))
        queueMenu = self.menubar.addMenu(QCoreApplication.translate("mainwindow_ui_tr", '&Queue'))
        videoFinderMenu = self.menubar.addMenu(QCoreApplication.translate("mainwindow_ui_tr", 'V&ideo Finder'))
        helpMenu = self.menubar.addMenu(QCoreApplication.translate("mainwindow_ui_tr", '&Help'))

        # viewMenu submenus
        sortMenu = viewMenu.addMenu(QCoreApplication.translate("mainwindow_ui_tr", 'Sort by'))

        # statusbar
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage(QCoreApplication.translate("mainwindow_ui_tr", "Persepolis Download Manager"))

        # toolBar
        self.toolBar2 = QToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, self.toolBar2)
        self.toolBar2.setWindowTitle(QCoreApplication.translate("mainwindow_ui_tr", 'Menu'))
        self.toolBar2.setFloatable(False)
        self.toolBar2.setMovable(False)

        self.toolBar = QToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, self.toolBar)
        self.toolBar.setWindowTitle(QCoreApplication.translate("mainwindow_ui_tr", 'Toolbar'))
        self.toolBar.setFloatable(False)
        self.toolBar.setMovable(False)

        #toolBar and menubar and actions
        self.persepolis_setting.beginGroup('settings/shortcuts')

        # videoFinderAddLinkAction
        self.videoFinderAddLinkAction = QAction(QIcon(icons + 'video_finder'), QCoreApplication.translate("mainwindow_ui_tr", 'Find Video Links...'), self, statusTip=QCoreApplication.translate("mainwindow_ui_tr", 'Download video or audio from Youtube, Vimeo, etc.'),
                                                triggered=self.showVideoFinderAddLinkWindow)

        self.videoFinderAddLinkAction_shortcut = QShortcut(self.persepolis_setting.value(
            'video_finder_shortcut'), self, self.showVideoFinderAddLinkWindow)

        videoFinderMenu.addAction(self.videoFinderAddLinkAction)

        # stopAllAction
        self.stopAllAction = QAction(QIcon(icons + 'stop_all'), QCoreApplication.translate("mainwindow_ui_tr", 'Stop All Active Downloads'),
                                     self, statusTip='Stop All Active Downloads', triggered=self.stopAllDownloads)
        downloadMenu.addAction(self.stopAllAction)

        # sort_file_name_Action
        self.sort_file_name_Action = QAction(
            QCoreApplication.translate("mainwindow_ui_tr", 'File Name'), self, triggered=self.sortByName)
        sortMenu.addAction(self.sort_file_name_Action)

        # sort_file_size_Action
        self.sort_file_size_Action = QAction(
            QCoreApplication.translate("mainwindow_ui_tr", 'File Size'), self, triggered=self.sortBySize)
        sortMenu.addAction(self.sort_file_size_Action)

        # sort_first_try_date_Action
        self.sort_first_try_date_Action = QAction(
            QCoreApplication.translate("mainwindow_ui_tr", 'First Try Date'), self, triggered=self.sortByFirstTry)
        sortMenu.addAction(self.sort_first_try_date_Action)

        # sort_last_try_date_Action
        self.sort_last_try_date_Action = QAction(
            QCoreApplication.translate("mainwindow_ui_tr", 'Last Try Date'), self, triggered=self.sortByLastTry)
        sortMenu.addAction(self.sort_last_try_date_Action)

        # sort_download_status_Action
        self.sort_download_status_Action = QAction(
            QCoreApplication.translate("mainwindow_ui_tr", 'Download Status'), self, triggered=self.sortByStatus)
        sortMenu.addAction(self.sort_download_status_Action)

        # trayAction
        self.trayAction = QAction(QCoreApplication.translate("mainwindow_ui_tr", 'Show System Tray Icon'), self,
                                  statusTip=QCoreApplication.translate("mainwindow_ui_tr", "Show/Hide system tray icon"), triggered=self.showTray)
        self.trayAction.setCheckable(True)
        viewMenu.addAction(self.trayAction)

        # showMenuBarAction
        self.showMenuBarAction = QAction(
            QCoreApplication.translate("mainwindow_ui_tr", 'Show Menubar'), self, statusTip=QCoreApplication.translate("mainwindow_ui_tr", 'Show Menubar'), triggered=self.showMenuBar)
        self.showMenuBarAction.setCheckable(True)
        viewMenu.addAction(self.showMenuBarAction)

        # showSidePanelAction
        self.showSidePanelAction = QAction(
            QCoreApplication.translate("mainwindow_ui_tr", 'Show Side Panel'), self, statusTip=QCoreApplication.translate("mainwindow_ui_tr", 'Show Side Panel'), triggered=self.showSidePanel)
        self.showSidePanelAction.setCheckable(True)
        viewMenu.addAction(self.showSidePanelAction)

        # minimizeAction
        self.minimizeAction = QAction(QIcon(icons + 'minimize'), QCoreApplication.translate("mainwindow_ui_tr", 'Minimize to System Tray'), self,
                                      statusTip=QCoreApplication.translate("mainwindow_ui_tr", "Minimize to System Tray"), triggered=self.minMaxTray)

        self.minimizeAction_shortcut = QShortcut(
            self.persepolis_setting.value('hide_window_shortcut'), self, self.minMaxTray)
        viewMenu.addAction(self.minimizeAction)

        # addlinkAction
        self.addlinkAction = QAction(QIcon(icons + 'add'), QCoreApplication.translate("mainwindow_ui_tr", 'Add New Download Link...'), self,
                                     statusTip=QCoreApplication.translate("mainwindow_ui_tr", "Add New Download Link"), triggered=self.addLinkButtonPressed)

        self.addlinkAction_shortcut = QShortcut(self.persepolis_setting.value(
            'add_new_download_shortcut'), self, self.addLinkButtonPressed)
        fileMenu.addAction(self.addlinkAction)

        # importText
        self.addtextfileAction = QAction(QIcon(icons + 'file'), QCoreApplication.translate("mainwindow_ui_tr", 'Import Links from Text File...'), self,
                                         statusTip=QCoreApplication.translate("mainwindow_ui_tr", 'Create a text file and put links in it, line by line!'), triggered=self.importText)

        self.addtextfileAction_shortcut = QShortcut(
            self.persepolis_setting.value('import_text_shortcut'), self, self.importText)

        fileMenu.addAction(self.addtextfileAction)

        # resumeAction
        self.resumeAction = QAction(QIcon(icons + 'play'), QCoreApplication.translate("mainwindow_ui_tr", 'Resume Download'), self,
                                    statusTip=QCoreApplication.translate("mainwindow_ui_tr", "Resume Download"), triggered=self.resumeButtonPressed)

        downloadMenu.addAction(self.resumeAction)

        # pauseAction
        self.pauseAction = QAction(QIcon(icons + 'pause'), QCoreApplication.translate("mainwindow_ui_tr", 'Pause Download'), self,
                                   statusTip=QCoreApplication.translate("mainwindow_ui_tr", "Pause Download"), triggered=self.pauseButtonPressed)

        downloadMenu.addAction(self.pauseAction)

        # stopAction
        self.stopAction = QAction(QIcon(icons + 'stop'), QCoreApplication.translate("mainwindow_ui_tr", 'Stop Download'), self,
                                  statusTip=QCoreApplication.translate("mainwindow_ui_tr", "Stop/Cancel Download"), triggered=self.stopButtonPressed)

        downloadMenu.addAction(self.stopAction)

        # propertiesAction
        self.propertiesAction = QAction(QIcon(icons + 'setting'), QCoreApplication.translate("mainwindow_ui_tr", 'Properties'), self,
                                        statusTip=QCoreApplication.translate("mainwindow_ui_tr", "Properties"), triggered=self.propertiesButtonPressed)

        downloadMenu.addAction(self.propertiesAction)

        # progressAction
        self.progressAction = QAction(QIcon(icons + 'window'), QCoreApplication.translate("mainwindow_ui_tr", 'Progress'), self,
                                      statusTip=QCoreApplication.translate("mainwindow_ui_tr", "Progress"), triggered=self.progressButtonPressed)

        downloadMenu.addAction(self.progressAction)

        # openFileAction
        self.openFileAction = QAction(QIcon(
            icons + 'file'), QCoreApplication.translate("mainwindow_ui_tr", 'Open File...'), self, statusTip=QCoreApplication.translate("mainwindow_ui_tr", 'Open File...'), triggered=self.openFile)
        fileMenu.addAction(self.openFileAction)

        # openDownloadFolderAction
        self.openDownloadFolderAction = QAction(QIcon(
            icons + 'folder'), QCoreApplication.translate("mainwindow_ui_tr", 'Open Download Folder'), self, statusTip=QCoreApplication.translate("mainwindow_ui_tr", 'Open Download Folder'), triggered=self.openDownloadFolder)

        fileMenu.addAction(self.openDownloadFolderAction)

        # openDefaultDownloadFolderAction
        self.openDefaultDownloadFolderAction = QAction(QIcon(
            icons + 'folder'), QCoreApplication.translate("mainwindow_ui_tr", 'Open Default Download Folder'), self, statusTip=QCoreApplication.translate("mainwindow_ui_tr", 'Open Default Download Folder'), triggered=self.openDefaultDownloadFolder)

        fileMenu.addAction(self.openDefaultDownloadFolderAction)

        # exitAction
        self.exitAction = QAction(QIcon(icons + 'exit'), QCoreApplication.translate("mainwindow_ui_tr", 'Exit'), self,
                                  statusTip=QCoreApplication.translate("mainwindow_ui_tr", "Exit"), triggered=self.closeAction)

        self.exitAction_shortcut = QShortcut(self.persepolis_setting.value('quit_shortcut'), self, self.closeAction)

        fileMenu.addAction(self.exitAction)

        # clearAction
        self.clearAction = QAction(QIcon(icons + 'multi_remove'), QCoreApplication.translate("mainwindow_ui_tr", 'Clear Download List'),
                                   self, statusTip=QCoreApplication.translate("mainwindow_ui_tr", 'Clear all items in download list'), triggered=self.clearDownloadList)
        editMenu.addAction(self.clearAction)

        # removeSelectedAction
        self.removeSelectedAction = QAction(QIcon(icons + 'remove'), QCoreApplication.translate("mainwindow_ui_tr", 'Remove Selected Downloads from List'),
                                            self, statusTip=QCoreApplication.translate("mainwindow_ui_tr", 'Remove Selected Downloads from List), triggered=self.removeSelected)

        self.removeSelectedAction_shortcut = QShortcut(
            self.persepolis_setting.value('remove_shortcut'), self, self.removeSelected)

        editMenu.addAction(self.removeSelectedAction)
        self.removeSelectedAction.setEnabled(False)

        # deleteSelectedAction
        self.deleteSelectedAction = QAction(QIcon(icons + 'trash'), QCoreApplication.translate("mainwindow_ui_tr", 'Delete Selected Download Files'),
                                            self, statusTip=QCoreApplication.translate("mainwindow_ui_tr", 'Delete Selected Download Files'), triggered=self.deleteSelected)

        self.deleteSelectedAction_shortcut = QShortcut(
            self.persepolis_setting.value('delete_shortcut'), self, self.deleteSelected)

        editMenu.addAction(self.deleteSelectedAction)
        self.deleteSelectedAction.setEnabled(False)

        # moveSelectedDownloadsAction
        self.moveSelectedDownloadsAction = QAction(QIcon(icons + 'folder'), QCoreApplication.translate("mainwindow_ui_tr", 'Move Selected Download Files to Another Folder...'),
                                                   self, statusTip=QCoreApplication.translate("mainwindow_ui_tr", 'Move Selected Download Files to Another Folder'), triggered=self.moveSelectedDownloads)

        editMenu.addAction(self.moveSelectedDownloadsAction)
        self.moveSelectedDownloadsAction.setEnabled(False)

        # createQueueAction
        self.createQueueAction = QAction(QIcon(icons + 'add_queue'), QCoreApplication.translate("mainwindow_ui_tr", 'Create New Queue...'),
                                         self, statusTip=QCoreApplication.translate("mainwindow_ui_tr", 'Create new download queue'), triggered=self.createQueue)
        queueMenu.addAction(self.createQueueAction)

        # removeQueueAction
        self.removeQueueAction = QAction(QIcon(icons + 'remove_queue'), QCoreApplication.translate("mainwindow_ui_tr", 'Remove Queue'),
                                         self, statusTip=QCoreApplication.translate("mainwindow_ui_tr", 'Remove this queue'), triggered=self.removeQueue)
        queueMenu.addAction(self.removeQueueAction)

        # startQueueAction
        self.startQueueAction = QAction(QIcon(
            icons + 'start_queue'), QCoreApplication.translate("mainwindow_ui_tr", 'Start this queue'), self, statusTip=QCoreApplication.translate("mainwindow_ui_tr", 'Start Queue'), triggered=self.startQueue)

        queueMenu.addAction(self.startQueueAction)

        # stopQueueAction
        self.stopQueueAction = QAction(QIcon(
            icons + 'stop_queue'), QCoreApplication.translate("mainwindow_ui_tr", 'Stop this queue'), self, statusTip=QCoreApplication.translate("mainwindow_ui_tr", 'Stop Queue'), triggered=self.stopQueue)

        queueMenu.addAction(self.stopQueueAction)

        # moveUpSelectedAction
        self.moveUpSelectedAction = QAction(QIcon(icons + 'multi_up'), QCoreApplication.translate("mainwindow_ui_tr", 'Move Selected Items Up'), self,
                                            statusTip=QCoreApplication.translate("mainwindow_ui_tr", 'Move currently selected items up by one row'), triggered=self.moveUpSelected)

        self.moveUpSelectedAction_shortcut = QShortcut(self.persepolis_setting.value(
            'move_up_selection_shortcut'), self, self.moveUpSelected)

        queueMenu.addAction(self.moveUpSelectedAction)

        # moveDownSelectedAction
        self.moveDownSelectedAction = QAction(QIcon(icons + 'multi_down'), QCoreApplication.translate("mainwindow_ui_tr", 'Move Selected Items Down'),
                                              self, statusTip=QCoreApplication.translate("mainwindow_ui_tr", 'Move currently selected items down by one row'), triggered=self.moveDownSelected)
        self.moveDownSelectedAction_shortcut = QShortcut(self.persepolis_setting.value(
            'move_down_selection_shortcut'), self, self.moveDownSelected)

        queueMenu.addAction(self.moveDownSelectedAction)

        # preferencesAction
        self.preferencesAction = QAction(QIcon(icons + 'preferences'), QCoreApplication.translate("mainwindow_ui_tr", 'Preferences'),
                                         self, statusTip=QCoreApplication.translate("mainwindow_ui_tr", 'Preferences'), triggered=self.openPreferences, menuRole=QAction.MenuRole.PreferencesRole)
        editMenu.addAction(self.preferencesAction)

        # aboutAction
        self.aboutAction = QAction(QIcon(
            icons + 'about'), QCoreApplication.translate("mainwindow_ui_tr", 'About'), self, statusTip=QCoreApplication.translate("mainwindow_ui_tr", 'About'), triggered=self.openAbout, menuRole=QAction.MenuRole.AboutRole)
        helpMenu.addAction(self.aboutAction)

        # issueAction
        self.issueAction = QAction(QIcon(icons + 'about'), QCoreApplication.translate("mainwindow_ui_tr", 'Report an Issue'),
                                   self, statusTip=QCoreApplication.translate("mainwindow_ui_tr", 'Report an issue'), triggered=self.reportIssue)
        helpMenu.addAction(self.issueAction)

        # updateAction
        self.updateAction = QAction(QIcon(icons + 'about'), QCoreApplication.translate("mainwindow_ui_tr", 'Check for Newer Version'),
                                    self, statusTip=QCoreApplication.translate("mainwindow_ui_tr", 'Check for newer release'), triggered=self.newUpdate)
        helpMenu.addAction(self.updateAction)

        # logAction
        self.logAction = QAction(QIcon(icons + 'about'), QCoreApplication.translate("mainwindow_ui_tr", 'Show Log File'),
                                 self, statusTip=QCoreApplication.translate("mainwindow_ui_tr", 'Help'), triggered=self.showLog)
        helpMenu.addAction(self.logAction)

        # helpAction
        self.helpAction = QAction(QIcon(icons + 'about'), QCoreApplication.translate("mainwindow_ui_tr", 'Help'),
                                  self, statusTip=QCoreApplication.translate("mainwindow_ui_tr", 'Help'), triggered=self.persepolisHelp)
        helpMenu.addAction(self.helpAction)

        self.persepolis_setting.endGroup()

        self.qmenu = MenuWidget(self)

        self.toolBar2.addWidget(self.qmenu)


# labels
        self.queue_panel_show_button.setText(QCoreApplication.translate("mainwindow_ui_tr", "Hide Options"))
        self.start_checkBox.setText(QCoreApplication.translate("mainwindow_ui_tr", "Start Time"))

        self.end_checkBox.setText(QCoreApplication.translate("mainwindow_ui_tr", "End Time"))

        self.reverse_checkBox.setText(QCoreApplication.translate(
            "mainwindow_ui_tr", "Download bottom of\n the list first"))

        self.limit_checkBox.setText(QCoreApplication.translate("mainwindow_ui_tr", "Limit Speed"))
        self.limit_comboBox.setItemText(0, "KiB/s")
        self.limit_comboBox.setItemText(1, "MiB/s")
        self.limit_pushButton.setText(QCoreApplication.translate("mainwindow_ui_tr", "Apply"))

        self.after_checkBox.setText(QCoreApplication.translate("mainwindow_ui_tr", "After download"))
        self.after_comboBox.setItemText(0, QCoreApplication.translate("mainwindow_ui_tr", "Shut Down"))

        self.keep_awake_checkBox.setText(QCoreApplication.translate("mainwindow_ui_tr", "Keep System Awake!"))
        self.keep_awake_checkBox.setToolTip(
            QCoreApplication.translate("mainwindow_ui_tr", "<html><head/><body><p>This option will prevent the system from going to sleep.\
            It is necessary if your power manager is suspending the system automatically. </p></body></html>"))

        self.after_pushButton.setText(QCoreApplication.translate("mainwindow_ui_tr", "Apply"))

        self.muxing_pushButton.setText(QCoreApplication.translate("mainwindow_ui_tr", "Start Mixing"))

        self.video_label.setText(QCoreApplication.translate("mainwindow_ui_tr", "<b>Video File Status: </b>"))
        self.audio_label.setText(QCoreApplication.translate("mainwindow_ui_tr", "<b>Audio File Status: </b>"))

        self.video_finder_status_label.setText(QCoreApplication.translate("mainwindow_ui_tr", "<b>Status: </b>"))
        self.muxing_status_label.setText(QCoreApplication.translate("mainwindow_ui_tr", "<b>Mixing status: </b>"))
