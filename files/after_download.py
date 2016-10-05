#!/usr/bin/env python3
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

from newopen import Open , readList , writeList
from after_download_ui import AfterDownloadWindow_Ui
import os , ast
from play import playNotification

class AfterDownloadWindow(AfterDownloadWindow_Ui):
    def __init__(self,download_info_file_list , setting_file) :
        super().__init__()
        self.download_info_file_list = download_info_file_list
        self.setting_file = setting_file
#connecting buttons
        self.open_pushButtun.clicked.connect(self.openFile)
        self.open_folder_pushButtun.clicked.connect(self.openFolder)
        self.ok_pushButton.clicked.connect(self.okButtonPressed)

#labels
        add_link_dictionary = self.download_info_file_list[9]
        final_download_path = add_link_dictionary['final_download_path']
        save_as = final_download_path + "/" + str(self.download_info_file_list[0])
        self.save_as_lineEdit.setText(save_as)
        self.save_as_lineEdit.setToolTip(save_as)
        link = str(add_link_dictionary ['link'])
        self.link_lineEdit.setText(link)
        self.link_lineEdit.setToolTip(link)
        file_name = "<b>File name</b> : " + str(self.download_info_file_list[0]) 
        self.file_name_label.setText(file_name)
        self.setWindowTitle(str(self.download_info_file_list[0])) 

        size = "<b>Size</b> : " + str(download_info_file_list[2])
        self.size_label.setText(size)
#play notifications
        playNotification('notifications/ok.ogg')

#disabling link_lineEdit and save_as_lineEdit
        self.link_lineEdit.setEnabled(False)
        self.save_as_lineEdit.setEnabled(False)
    def openFile(self):
#executing file
        add_link_dictionary = self.download_info_file_list[9]
        file_path = add_link_dictionary['file_path']
        if os.path.isfile(file_path):
            os.system("xdg-open '" + file_path  + "' &" )
        self.saveWindowSize()
        self.close()

    def openFolder(self):
#open download folder
        add_link_dictionary = self.download_info_file_list[9]
        file_path = add_link_dictionary ['file_path']
        file_path_split = file_path.split('/')
        del file_path_split[-1]
        download_path = '/'.join(file_path_split)
        if os.path.isdir(download_path):
            os.system("xdg-open '" + download_path + "' &" )
        self.saveWindowSize()
        self.close()
 
    def okButtonPressed(self):
        if self.dont_show_checkBox.isChecked() == True :
            f = Open(self.setting_file)
            setting_file_lines = f.readlines()
            f.close()
            setting_dict_str = str(setting_file_lines[0].strip())
            setting_dict = ast.literal_eval(setting_dict_str) 
            setting_dict['after-dialog'] = 'no'
            f = Open(self.setting_file , 'w')
            f.writelines(str(setting_dict))
            f.close()
        self.saveWindowSize()
        self.close()

    def saveWindowSize(self):
#finding last windows_size that saved in windows_size file
        home_address = os.path.expanduser("~")

        config_folder = str(home_address) + "/.config/persepolis_download_manager"

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
        windows_size_dict ['AfterDownloadWindow_Ui'] = [ width , height ]
        f = Open(windows_size, 'w')
        f.writelines(str(windows_size_dict))
        f.close()


