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

import os , ast , random , shutil
from time import sleep
import osCommands

home_address = os.path.expanduser("~")
user_name_split = home_address.split('/')
user_name = user_name_split[2]

#persepolis tmp folder in /tmp
persepolis_tmp = '/tmp/persepolis_' + user_name


class Open():
#safer way to read and write files.
    def __init__(self,file_name , mode = 'r'):
#random_number for temporary file name
        random_number = random.randint(1152921504606846976,18446744073709551615)
#temporary file
        self.temp_file_path = persepolis_tmp + str(random_number) 
# r = read mode , w = write mode , a = append mode
        self.mode = mode
        self.file_name = file_name
#Creating a lock file
#lock file prevents accessing a file simoltaneously
#If mode is 'w' or 'a' (write or append) , all changes is saving in a temporary file and after closing, original file replaced by temporary file
#If mode is 'r' (Read) , original file is copying in temp_file_path and then content of temporary file is reading.
        self.lock_file = self.file_name + ".lock"
        while os.path.isfile(self.lock_file) == True :
            sleep(0.1)
        osCommands.touch(self.lock_file)
        if self.mode == "w":
            self.f = open(self.temp_file_path, "w")
        elif self.mode == "a":
            shutil.copy(str(self.file_name) , str(self.temp_file_path)) 
            self.f = open(self.temp_file_path , "a" )
        else:
            shutil.copy(str(self.file_name) , str(self.temp_file_path)) 
            self.f = open (self.temp_file_path , "r")
     
    def readlines(self):
        return self.f.readlines()

    def readline(self):
        return self.f.readline()


    def writelines(self , content ):
        self.f.writelines(content)

    def remove(self):
        while os.path.isfile(self.lock_file) == True :
            sleep(0.1)
        os.remove(self.file_name)


    def close(self):
        self.f.close()
        if self.mode == 'w' or self.mode == 'a':
            try:
                shutil.move(str(self.temp_file_path) ,str(self.file_name) )
            except:
                pass
        else :
            os.remove(self.temp_file_path)

 
        try:
            os.remove(self.lock_file)
        except:
            pass


#This function is writting a list in file_path in dictionary format    
def writeList(file_path , list):
    dictionary =  {'list' : list }
    f = Open(file_path, 'w')
    f.writelines(str(dictionary)) 
    f.close()

#This function is reading file_path and return content of file in list format
def readList(file_path , mode = 'dictionary' ):
    f = Open(file_path , 'r')
    f_string = f.readline()
    f.close()
    dictionary = ast.literal_eval(f_string.strip())
    list = dictionary ['list']
 
    if mode == 'string':
        list[9] = str(list[9]) 
        
    return list

def readDict(file_path) :
    f = Open(file_path)
    f_lines = f.readlines()
    f.close()
    dict_str = str(f_lines[0].strip())
    return_dict = ast.literal_eval(dict_str) 
    return return_dict


