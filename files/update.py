import urllib
from urllib import request
import webbrowser
import platform
import newopen

#finding os_type
os_type = platform.system()

# latest stable version
# get information dictionary from github
updatesource = urllib.request.urlopen('https://persepolisdm.github.io/version',data=None)
serverdict = updatesource.read().decode("utf-8")
# save information to file
file = open('serverdictfile','w') # store in tmp
file.write(str(serverdict))
file.close()
# read as dictionary
dictvalue = newopen.readDict('serverdictfile') #read from tmp

# Foundation for download latest windows installer
def winupdatedl():
    # find system architect
    if platform.architecture()[0] == '64bit':
        webbrowser.open(dictvalue['win64dlurl'])
    elif platform.architecture()[0] == '32bit':
        webbrowser.open(dictvalue['win32dlurl'])
    else:
        print("we can't detect your system architect")

# update check
def updatecheck():
    # installed version
    clientversion = '2.3'
    # get latest stable version
    serverversion = dictvalue['version']

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
