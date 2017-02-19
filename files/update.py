import urllib
from urllib import request
import webbrowser
import platform

#finding os_type
os_type = platform.system()

# Foundation for download latest windows installer
def winupdatedl():
    # find system architect
    if platform.architecture()[0] == '64bit':
        webbrowser.open('http://137.74.154.122/persepolis/latest_64.exe')
    elif platform.architecture()[0] == '32bit':
        webbrowser.open('http://137.74.154.122/persepolis/latest_32.exe')
    else:
        print("we can't detect your system architect")

# update check
def updatecheck():
    # installed version
    clientversion = '2.3'
    # latest stable version
    updatesource = urllib.request.urlopen("http://137.74.154.122/persepolis/version",data=None)
    serverversion = updatesource.read()
    # Comparison
    if serverversion != clientversion :
        return False # means client version is dead
    else:
        return True # means client version is alive

# respons about update
if updatecheck():
    print ("you are using latest version")
else:
    print ("update availible")
    # check if it is Windows
    if os_type == "Windows" :
        winupdatedl()
