
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
    from PySide6.QtWidgets import QCheckBox, QProgressBar, QFrame, QDoubleSpinBox, QComboBox, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
    from PySide6.QtCore import Qt, QTranslator, QCoreApplication, QLocale, QSize
    from PySide6.QtGui import QIcon
except:
    from PyQt5.QtWidgets import QCheckBox, QProgressBar, QFrame, QDoubleSpinBox, QComboBox, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
    from PyQt5.QtCore import Qt, QTranslator, QCoreApplication, QLocale, QSize
    from PyQt5.QtGui import QIcon

from persepolis.gui import resources


class ProgressWindow_Ui(QWidget):
    def __init__(self, persepolis_setting):
        super().__init__()
        self.persepolis_setting = persepolis_setting
        icons = ':/' + str(persepolis_setting.value('settings/icons')) + '/'

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


# window
        self.setMinimumSize(QSize(595, 284))

        self.setWindowIcon(QIcon.fromTheme('persepolis', QIcon(':/com.github.persepolisdm.persepolis.svg')))
        self.setWindowTitle(QCoreApplication.translate("progress_ui_tr", "Persepolis Download Manager"))

        verticalLayout = QVBoxLayout(self)

# progress_tabWidget
        self.progress_tabWidget = QTabWidget(self)

# information_tab
        self.information_tab = QWidget()
        information_verticalLayout = QVBoxLayout(self.information_tab)

# link_label
        self.link_label = QLabel(self.information_tab)
        information_verticalLayout.addWidget(self.link_label)

# status_label
        self.status_label = QLabel(self.information_tab)
        information_verticalLayout.addWidget(self.status_label)

# downloaded_label
        self.downloaded_label = QLabel(self.information_tab)
        information_verticalLayout.addWidget(self.downloaded_label)

# rate_label
        self.rate_label = QLabel(self.information_tab)
        information_verticalLayout.addWidget(self.rate_label)

# time_label
        self.time_label = QLabel(self.information_tab)
        information_verticalLayout.addWidget(self.time_label)

# connections_label
        self.connections_label = QLabel(self.information_tab)
        information_verticalLayout.addWidget(self.connections_label)

        information_verticalLayout.addStretch(1)

# add information_tab to progress_tabWidget
        self.progress_tabWidget.addTab(self.information_tab, "")

# options_tab
        self.options_tab = QWidget()
        options_tab_verticalLayout = QVBoxLayout(self.options_tab)
        options_tab_horizontalLayout = QHBoxLayout()
#         options_tab_horizontalLayout.setContentsMargins(11, 11, 11, 11)


# limit_checkBox
        self.limit_checkBox = QCheckBox(self.options_tab)

        limit_verticalLayout = QVBoxLayout()
        limit_verticalLayout.addWidget(self.limit_checkBox)

# limit_frame
        self.limit_frame = QFrame(self.options_tab)
        self.limit_frame.setFrameShape(QFrame.StyledPanel)
        self.limit_frame.setFrameShadow(QFrame.Raised)
        limit_frame_verticalLayout = QVBoxLayout(self.limit_frame)
        limit_frame_horizontalLayout = QHBoxLayout()

# limit_spinBox
        self.limit_spinBox = QDoubleSpinBox(self.options_tab)
        self.limit_spinBox.setMinimum(1)
        self.limit_spinBox.setMaximum(1023)
        limit_frame_horizontalLayout.addWidget(self.limit_spinBox)

# limit_comboBox
        self.limit_comboBox = QComboBox(self.options_tab)
        self.limit_comboBox.addItem("")
        self.limit_comboBox.addItem("")

        limit_frame_horizontalLayout.addWidget(self.limit_comboBox)

# limit_pushButton
        self.limit_pushButton = QPushButton(self.options_tab)

        limit_frame_verticalLayout.addLayout(limit_frame_horizontalLayout)
        limit_frame_verticalLayout.addWidget(self.limit_pushButton)

        limit_verticalLayout.addWidget(self.limit_frame)

        limit_verticalLayout.setContentsMargins(11, 11, 11, 11)

        options_tab_horizontalLayout.addLayout(limit_verticalLayout)

        options_tab_verticalLayout.addLayout(options_tab_horizontalLayout)
        options_tab_verticalLayout.addStretch(1)

# after_checkBox
        self.after_checkBox = QCheckBox(self.options_tab)

        after_verticalLayout = QVBoxLayout()
        after_verticalLayout.addWidget(self.after_checkBox)

# after_frame
        self.after_frame = QFrame(self.options_tab)
        self.after_frame.setFrameShape(QFrame.StyledPanel)
        self.after_frame.setFrameShadow(QFrame.Raised)

        after_frame_verticalLayout = QVBoxLayout(self.after_frame)


# after_comboBox
        self.after_comboBox = QComboBox(self.options_tab)
        self.after_comboBox.addItem("")

        after_frame_verticalLayout.addWidget(self.after_comboBox)

# after_pushButton
        self.after_pushButton = QPushButton(self.options_tab)
        after_frame_verticalLayout.addWidget(self.after_pushButton)

        after_verticalLayout.addWidget(self.after_frame)

        after_verticalLayout.setContentsMargins(11, 11, 11, 11)
        options_tab_horizontalLayout.addLayout(after_verticalLayout)

        self.progress_tabWidget.addTab(self.options_tab, "")

        verticalLayout.addWidget(self.progress_tabWidget)


# download_progressBar
        self.download_progressBar = QProgressBar(self)
        verticalLayout.addWidget(self.download_progressBar)
        self.download_progressBar.setTextVisible(False)

# buttons
        button_horizontalLayout = QHBoxLayout()
        button_horizontalLayout.addStretch(1)

# resume_pushButton
        self.resume_pushButton = QPushButton(self)
        self.resume_pushButton.setIcon(QIcon(icons + 'play'))
        button_horizontalLayout.addWidget(self.resume_pushButton)

# pause_pushButton
        self.pause_pushButton = QPushButton(self)
        self.pause_pushButton.setIcon(QIcon(icons + 'pause'))
        button_horizontalLayout.addWidget(self.pause_pushButton)

# stop_pushButton
        self.stop_pushButton = QPushButton(self)
        self.stop_pushButton.setIcon(QIcon(icons + 'stop'))
        button_horizontalLayout.addWidget(self.stop_pushButton)

        verticalLayout.addLayout(button_horizontalLayout)

        self.progress_tabWidget.setCurrentIndex(0)
# labels
        self.link_label.setText(QCoreApplication.translate("progress_ui_tr", "Link: "))
        self.status_label.setText(QCoreApplication.translate("progress_ui_tr", "Status: "))
        self.downloaded_label.setText(QCoreApplication.translate("progress_ui_tr", "Downloaded:"))
        self.rate_label.setText(QCoreApplication.translate("progress_ui_tr", "Transfer rate: "))
        self.time_label.setText(QCoreApplication.translate("progress_ui_tr", "Estimated time left:"))
        self.connections_label.setText(QCoreApplication.translate("progress_ui_tr", "Number of connections: "))
        self.progress_tabWidget.setTabText(self.progress_tabWidget.indexOf(
            self.information_tab), QCoreApplication.translate("progress_ui_tr", "Download Information"))
        self.limit_checkBox.setText(QCoreApplication.translate("progress_ui_tr", "Limit speed"))
        self.after_checkBox.setText(QCoreApplication.translate("progress_ui_tr", "After download"))
        self.limit_comboBox.setItemText(0, "KiB/s")
        self.limit_comboBox.setItemText(1, "MiB/s")
        self.limit_pushButton.setText(QCoreApplication.translate("progress_ui_tr", "Apply"))

        self.after_comboBox.setItemText(0, QCoreApplication.translate("progress_ui_tr", "Shut Down"))

        self.progress_tabWidget.setTabText(
            self.progress_tabWidget.indexOf(self.options_tab), QCoreApplication.translate("progress_ui_tr", "Download Options"))
        self.resume_pushButton.setText(QCoreApplication.translate("progress_ui_tr", "Resume"))
        self.pause_pushButton.setText(QCoreApplication.translate("progress_ui_tr", "Pause"))
        self.stop_pushButton.setText(QCoreApplication.translate("progress_ui_tr", "Stop"))
        self.after_pushButton.setText(QCoreApplication.translate("progress_ui_tr", "Apply"))
