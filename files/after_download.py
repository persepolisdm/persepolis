#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
        self.close()


