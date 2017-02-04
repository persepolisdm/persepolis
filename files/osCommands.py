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

import platform
import os
import shutil
import subprocess
import PyQt5
from PyQt5 import QtCore

os_type = platform.system()

def touch(file_path):
    if not(os.path.isfile(file_path)) :
        f = open(file_path , 'w') 
        f.close()

#xdgOpen is openning files or folders
def xdgOpen(file_path):
    if os_type == 'Linux' or os_type == 'FreeBSD' : #GNU/Linux systems
        os.system('xdg-open "' + file_path + '" &')
    elif os_type == 'Darwin': # OS X systems
        os.system('open "' + file_path + '" &' )
    elif os_type == 'Windows':
        CREATE_NO_WINDOW = 0x08000000
        subprocess.Popen(['cmd' , '/C' ,'start', file_path  ,  file_path  ] , shell = False , creationflags = CREATE_NO_WINDOW )


def remove(file_path): #removing file with path of file_path
    if os.path.isfile(file_path):
        try:
            os.remove(file_path)
            return 'ok' #function returning  this , if opertation was successful
        except:
            return 'cant' #function is returning this , if operation was not successful
    else:
         return 'no' #function is returning this , if file is not existed 

def removeDir(folder_path): #removeDir is removing folder : folder_path 
    if os.path.isdir(folder_path): #checking folder_path existance
        try:
            shutil.rmtree(folder_path) #removing folder
            return 'ok'
        except:
            return 'cant' #returning 'cant' if removing was not successful
    else:
        return 'no' #returning 'no' if file didn't existed

def makeDirs(folder_path): #making new folders
    os.makedirs(folder_path , exist_ok=True)

