#!/usr/bin/env python
import os
from time import sleep
class Open():
    def __init__(self,file_name , mode = None):
        self.file_name = file_name
        self.lock_file = self.file_name + ".lock"
        while os.path.isfile(self.lock_file) == True :
            sleep(0.1)
        os.system("touch " + self.lock_file)
        if mode == "w":
            self.f = open(self.file_name , "w")
        elif mode == "a":
            self.f = open(self.file_name , "a" )
        else:
            self.f = open (self.file_name , "r")
     
    def readlines(self):
        return self.f.readlines()

    def writelines(self , content ):
        self.f.writelines(content)
    def remove(self):
        while os.path.isfile(self.lock_file) == True :
            sleep(0.1)
        os.remove(self.file_name)


    def close(self):
        self.f.close()
        try:
            os.remove(self.lock_file)
        except:
            pass


    
