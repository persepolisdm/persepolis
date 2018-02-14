# -*- coding: utf-8 -*-
"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QTabWidget, QHBoxLayout, QVBoxLayout, QLabel, QTextEdit, QPushButton
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QSize, QPoint, QTranslator, QCoreApplication, QLocale
from persepolis.gui import resources 


class AboutWindow_Ui(QWidget):
    def __init__(self,persepolis_setting):
        super().__init__()

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

        self.setMinimumSize(QtCore.QSize(545, 375))
        self.setWindowIcon(QIcon.fromTheme('persepolis', QIcon(':/persepolis.svg')))

        verticalLayout = QVBoxLayout(self)

        self.about_tabWidget = QTabWidget(self)

        # developers_tab
        self.developers_tab = QWidget(self)

        developers_verticalLayout = QVBoxLayout(self.developers_tab)

        self.title_label = QLabel(self.developers_tab)
        font = QFont()
        font.setBold(True)
        font.setWeight(75)
        self.title_label.setFont(font)
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        developers_verticalLayout.addWidget(self.title_label)

        self.version_label = QLabel(self.developers_tab)
        self.version_label.setAlignment(QtCore.Qt.AlignCenter)

        developers_verticalLayout.addWidget(self.version_label)

        self.name_label = QLabel(self.developers_tab)
        self.name_label.setAlignment(QtCore.Qt.AlignCenter)
        developers_verticalLayout.addWidget(self.name_label)

        self.site2_label = QLabel(self.developers_tab)
        self.site2_label.setTextFormat(QtCore.Qt.RichText)
        self.site2_label.setAlignment(QtCore.Qt.AlignCenter)
        self.site2_label.setOpenExternalLinks(True)
        self.site2_label.setTextInteractionFlags(
            QtCore.Qt.TextBrowserInteraction)
        developers_verticalLayout.addWidget(self.site2_label)

        self.telegram_label = QLabel(self.developers_tab)
        self.telegram_label.setTextFormat(QtCore.Qt.RichText)
        self.telegram_label.setAlignment(QtCore.Qt.AlignCenter)
        self.telegram_label.setOpenExternalLinks(True)
        self.telegram_label.setTextInteractionFlags(
            QtCore.Qt.TextBrowserInteraction)
        developers_verticalLayout.addWidget(self.telegram_label)

        self.twitter_label = QLabel(self.developers_tab)
        self.twitter_label.setTextFormat(QtCore.Qt.RichText)
        self.twitter_label.setAlignment(QtCore.Qt.AlignCenter)
        self.twitter_label.setOpenExternalLinks(True)
        self.twitter_label.setTextInteractionFlags(
            QtCore.Qt.TextBrowserInteraction)
        developers_verticalLayout.addWidget(self.twitter_label)


        # translators tab
        self.translators_tab = QWidget(self)
        translators_tab_verticalLayout = QVBoxLayout(self.translators_tab)

        # persian translators
        self.persian_translators_label = QLabel(self.translators_tab)
        self.persian_translators_label.setFont(font)
        self.persian_translators_label.setAlignment(QtCore.Qt.AlignCenter)

        translators_tab_verticalLayout.addWidget(self.persian_translators_label)

        self.persian_translatos_name_label = QLabel(self.translators_tab)
        self.persian_translatos_name_label.setAlignment(QtCore.Qt.AlignCenter)
        translators_tab_verticalLayout.addWidget(self.persian_translatos_name_label)

        # chinese translators
        self.chinese_translators_label = QLabel(self.translators_tab)
        self.chinese_translators_label.setFont(font)
        self.chinese_translators_label.setAlignment(QtCore.Qt.AlignCenter)
        translators_tab_verticalLayout.addWidget(self.chinese_translators_label)

        self.chinese_translatos_name_label = QLabel(self.translators_tab)
        self.chinese_translatos_name_label.setAlignment(QtCore.Qt.AlignCenter)
        translators_tab_verticalLayout.addWidget(self.chinese_translatos_name_label)

        translators_tab_verticalLayout.addStretch(1)
   
        # License tab
        self.license_tab = QWidget(self)
        license_tab_verticalLayout = QVBoxLayout(self.license_tab)

        self.license_text = QTextEdit(self.license_tab)
        self.license_text.setReadOnly(True)

        license_tab_verticalLayout.addWidget(self.license_text)



        verticalLayout.addWidget(self.about_tabWidget)

        # buttons
        button_horizontalLayout = QHBoxLayout()
        button_horizontalLayout.addStretch(1)

        self.pushButton = QPushButton(self)
        self.pushButton.setIcon(QIcon(icons + 'ok'))
        self.pushButton.clicked.connect(self.close)

        button_horizontalLayout.addWidget(self.pushButton)

        verticalLayout.addLayout(button_horizontalLayout)

        self.setWindowTitle(QCoreApplication.translate("about_ui_tr", "About Persepolis"))

        # developers_tab
        self.title_label.setText(QCoreApplication.translate("about_ui_tr", "Persepolis Download Manager"))
        self.version_label.setText(QCoreApplication.translate("about_ui_tr", "Version 3.0.1"))
        self.name_label.setText(QCoreApplication.translate("about_ui_tr", 
                                                           "\nAliReza AmirSamimi\nMohammadreza Abdollahzadeh\nSadegh Alirezaie\nMostafa Asadi\nMohammadAmin Vahedinia\nJafar Akhondali\nH.Rostami", "TRANSLATORS NOTE: YOU REALLY DON'T NEED TO TRANSLATE THIS PART!"))
        self.site2_label.setText(QCoreApplication.translate("about_ui_tr", 
            "<a href=https://persepolisdm.github.io>https://persepolisdm.github.io</a>", "TRANSLATORS NOTE: YOU REALLY DON'T NEED TO TRANSLATE THIS PART!"))
        self.telegram_label.setText(QCoreApplication.translate("about_ui_tr", 
            "<a href=https://telegram.me/persepolisdm>https://telegram.me/persepolisdm</a>", "TRANSLATORS NOTE: YOU REALLY DON'T NEED TO TRANSLATE THIS PART!"))
        self.twitter_label.setText(QCoreApplication.translate("about_ui_tr", 
            "<a href=https://twitter.com/persepolisdm>https://twitter.com/persepolisdm</a>", "TRANSLATORS NOTE: YOU REALLY DON'T NEED TO TRANSLATE THIS PART!"))
        
        # translators_tab
        self.persian_translators_label.setText(QCoreApplication.translate("about_ui_tr", "Persian translators:"))

        self.persian_translatos_name_label.setText(QCoreApplication.translate("about_ui_tr", "H.Rostami\nMostafa Asadi"))

        self.chinese_translators_label.setText(QCoreApplication.translate("about_ui_tr", "Chinese translators:"))

        self.chinese_translatos_name_label.setText(QCoreApplication.translate("about_ui_tr", "Davinma\n210hcl\nleoxxx"))

        # License
        self.license_text.setPlainText(QCoreApplication.translate("about_ui_tr", """
            This program is free software: you can redistribute it and/or modify
            it under the terms of the GNU General Public License as published by
            the Free Software Foundation, either version 3 of the License, or
            (at your option) any later version.

            This program is distributed in the hope that it will be useful,
            but WITHOUT ANY WARRANTY; without even the implied warranty of
            MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
            GNU General Public License for more details.

            You should have received a copy of the GNU General Public License
            along with this program.  If not, see http://www.gnu.org/licenses/.
            """))


        # tabs
        self.about_tabWidget.addTab(self.developers_tab, QCoreApplication.translate("about_ui_tr", "Developers"))
        self.about_tabWidget.addTab(self.translators_tab, QCoreApplication.translate("about_ui_tr", "Translators"))
        self.about_tabWidget.addTab(self.license_tab, QCoreApplication.translate("about_ui_tr", "License"))

        # button
        self.pushButton.setText(QCoreApplication.translate("about_ui_tr", "OK"))


