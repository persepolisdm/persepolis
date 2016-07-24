#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setting_ui import Setting_Ui
import ast , os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog 
from PyQt5.QtGui import QFont
from newopen import Open

home_address = os.path.expanduser("~")
config_folder = str(home_address) + "/.config/persepolis_download_manager"

#setting
setting_file = config_folder + '/setting'


class PreferencesWindow(Setting_Ui):
    def __init__(self,parent):
        super().__init__(parent)

        f = Open(setting_file)
        setting_file_lines = f.readlines()
        f.close()
        setting_dict_str = str(setting_file_lines[0].strip())
        self.setting_dict = ast.literal_eval(setting_dict_str) 
#initialization
        self.tries_spinBox.setValue(int(self.setting_dict['max-tries']))
        self.wait_spinBox.setValue(int(self.setting_dict['retry-wait']))
        self.time_out_spinBox.setValue(int(self.setting_dict['timeout']))
        self.connections_spinBox.setValue(int(self.setting_dict['connections']))

        self.download_folder_lineEdit.setText(str(self.setting_dict['download_path']))
        self.temp_download_lineEdit.setText(str(self.setting_dict['download_path_temp']))
        
        self.volume_label.setText('Volume : ' + str(self.setting_dict['sound-volume']) )
        self.volume_dial.setValue(int(self.setting_dict['sound-volume']))
#set style 
        available_styles = QtWidgets.QStyleFactory.keys()
        for style in available_styles :
            self.style_comboBox.addItem(style)

        self.style_comboBox.addItem('System')
        
        current_style_index = self.style_comboBox.findText(str(self.setting_dict['style']))
        if current_style_index != -1 :
            self.style_comboBox.setCurrentIndex(current_style_index)
#set color_scheme
        color_scheme = ['System' , 'Persepolis Dark Red' , 'Persepolis Dark Blue']
        self.color_comboBox.addItems(color_scheme)
            
        current_color_index = self.color_comboBox.findText(str(self.setting_dict['color-scheme']))
        if current_color_index != -1 :
            self.color_comboBox.setCurrentIndex(current_color_index)
#set icons
        icons = ['Archdroid-Red' , 'Archdroid-Blue']
        self.icon_comboBox.addItems(icons)

        current_icons_index = self.icon_comboBox.findText(str(self.setting_dict['icons']))
        if current_icons_index != -1 :
            self.icon_comboBox.setCurrentIndex(current_icons_index)

#set font 
        font_setting = QFont() 
        font_setting.setFamily(str(self.setting_dict['font']))
        self.fontComboBox.setCurrentFont(font_setting)
    
        self.font_size_spinBox.setValue(int(self.setting_dict['font-size']))

#sound frame 
        self.sound_frame.setEnabled(False)
        self.enable_notifications_checkBox.toggled.connect(self.soundFrame)
        if str(self.setting_dict['sound']) == 'yes':
            self.enable_notifications_checkBox.setChecked(True) 
        else:
            self.enable_notifications_checkBox.setChecked(False)
#connect folder buttons
        self.download_folder_lineEdit.setEnabled(False)
        self.download_folder_pushButton.clicked.connect(self.downloadFolderPushButtonClicked)
        self.temp_download_lineEdit.setEnabled(False)
        self.temp_download_pushButton.clicked.connect(self.tempDownloadPushButtonClicked)
#font change 
        
        self.fontComboBox.currentFontChanged.connect(self.fontChanged)

#dial
        self.volume_dial.setNotchesVisible(True)
        self.volume_dial.valueChanged.connect(self.dialChanged)

#tray icon
       
        if str(self.setting_dict['tray-icon']) == 'yes':
            self.enable_system_tray_checkBox.setChecked(True)
        else:
            self.enable_notifications_checkBox.setChecked(False)
            

#ok cancel default button
        self.cancel_pushButton.clicked.connect(self.cancelButtonPressed)
        self.defaults_pushButton.clicked.connect(self.defaultsPushButtonPressed)
        self.ok_pushButton.clicked.connect(self.okPushButtonPressed)


    def soundFrame(self,checkBox):
        if self.enable_notifications_checkBox.isChecked() == True :
            self.sound_frame.setEnabled(True)
        else :
            self.sound_frame.setEnabled(False)
 

    def downloadFolderPushButtonClicked(self,button):
        download_path = str(self.setting_dict['download_path'])
        fname = QFileDialog.getExistingDirectory(self,'Open f', download_path )
        if fname:
            self.download_folder_lineEdit.setText(fname)
            self.setting_dict['download_path'] = str(fname)

    def tempDownloadPushButtonClicked(self , button):
        download_path_temp = str(self.setting_dict['download_path_temp'])
        fname = QFileDialog.getExistingDirectory(self,'Open f', download_path_temp )
        if fname:
            self.temp_download_lineEdit.setText(fname)
            self.setting_dict['download_path_temp'] = str(fname)

    def fontChanged(self,combo):
        current_font = self.fontComboBox.currentFont()
        current_font = current_font.key()
        current_font = current_font.split(',')
        self.setting_dict['font'] = str(current_font[0])


    def dialChanged(self,dial):
        self.volume_label.setText('Volume : ' + str(self.volume_dial.value()))

    def cancelButtonPressed(self , button):
        self.close()

    def defaultsPushButtonPressed(self , button):
        download_path_temp_default = str(home_address) + '/.persepolis'
        download_path_default = str(home_address) + '/Downloads/Persepolis'
 
        self.setting_dict = {'tray-icon':'yes', 'max-tries' : 5 , 'retry-wait': 0 , 'timeout' : 60 , 'connections' : 16 , 'download_path_temp' : download_path_temp_default , 'download_path':download_path_default , 'sound' : 'yes' , 'sound-volume':100 , 'style':'Fusion' , 'color-scheme' : 'Persepolis Dark Red' , 'icons':'Archdroid-Red','font' : 'Ubuntu' , 'font-size' : 9  }

        self.tries_spinBox.setValue(int(self.setting_dict['max-tries']))
        self.wait_spinBox.setValue(int(self.setting_dict['retry-wait']))
        self.time_out_spinBox.setValue(int(self.setting_dict['timeout']))
        self.connections_spinBox.setValue(int(self.setting_dict['connections']))

        self.download_folder_lineEdit.setText(str(self.setting_dict['download_path']))
        self.temp_download_lineEdit.setText(str(self.setting_dict['download_path_temp']))


        
        self.volume_label.setText('Volume : ' + str(self.setting_dict['sound-volume']) )
        self.volume_dial.setValue(int(self.setting_dict['sound-volume']))
#set style 
        current_style_index = self.style_comboBox.findText(str(self.setting_dict['style']))
        if current_style_index != -1 :
            self.style_comboBox.setCurrentIndex(current_style_index)
#set color_scheme
        current_color_index = self.color_comboBox.findText(str(self.setting_dict['color-scheme']))
        if current_color_index != -1 :
            self.color_comboBox.setCurrentIndex(current_color_index)
#set icons
        current_icons_index = self.icon_comboBox.findText(str(self.setting_dict['icons']))
        if current_icons_index != -1 :
            self.icon_comboBox.setCurrentIndex(current_icons_index)

#set font 
        font_setting = QFont() 
        font_setting.setFamily(str(self.setting_dict['font']))
        self.fontComboBox.setCurrentFont(font_setting)
    
        self.font_size_spinBox.setValue(int(self.setting_dict['font-size']))

#sound frame 
        if str(self.setting_dict['sound']) == 'yes':
            self.enable_notifications_checkBox.setChecked(True) 
        else:
            self.enable_notifications_checkBox(False)

#tray icon
       
        if str(self.setting_dict['tray-icon']) == 'yes':
            self.enable_system_tray_checkBox.setChecked(True)
        else:
            self.enable_notifications_checkBox.setChecked(False)
 

    def okPushButtonPressed(self,button):
        self.setting_dict['max-tries'] = self.tries_spinBox.value()
        self.setting_dict['retry-wait'] = self.wait_spinBox.value()
        self.setting_dict['timeout'] = self.time_out_spinBox.value()
        self.setting_dict['connections'] = self.connections_spinBox.value()
        self.setting_dict['download_path'] = self.download_folder_lineEdit.text()
        self.setting_dict['download_path_temp'] = self.temp_download_lineEdit.text()
        self.setting_dict['sound-volume'] = self.volume_dial.value()
        self.setting_dict['style'] = self.style_comboBox.currentText()
        self.setting_dict['color-scheme'] = self.color_comboBox.currentText()
        self.setting_dict['icons'] = self.icon_comboBox.currentText()
        self.setting_dict['font-size'] = self.font_size_spinBox.value()

        if self.enable_system_tray_checkBox.isChecked() == True :
            self.setting_dict['tray-icon'] = 'yes'
        else:
            self.setting_dict['tray-icon'] = 'no'

#this section  creates temporary download folder and download folder and download sub folders if they did not existed.
        download_path_temp  = self.setting_dict ['download_path_temp']
        download_path = self.setting_dict [ 'download_path']
        folder_list = [download_path_temp , download_path]
        for folder in [ 'Audios' , 'Videos', 'Others','Documents','Compressed' ]:
            folder_list.append(download_path + '/' + folder )

        for folder in folder_list :
            if os.path.isdir(folder) == False :
                os.mkdir(folder)


        if self.enable_notifications_checkBox.isChecked() == True :
            self.setting_dict['sound'] = 'yes'
        else:
            self.setting_dict['sound'] = 'no'

        f = Open(setting_file , 'w')
        f.writelines(str(self.setting_dict))
        f.close()

        self.close()

