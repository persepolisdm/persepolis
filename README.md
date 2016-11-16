Persepolis Download Manager 
=============
+ version : 2.2.2 Unstable
+ Persepolis Download Manager is a GUI for aria2.
+ Persepolis written in PYQT5.


![ScreenShot](http://s1.picofile.com/file/8264685926/persepolis.jpg)



### Installation on GNU/Linux
##For Ubuntu bases(Ubuntu16.04 , Kubuntu , Xubuntu , Linux Mint , ... ):

	$ sudo add-apt-repository ppa:persepolis/ppa
	$ sudo apt-get update
	$ sudo apt-get install persepolis


##For installing in ArchLinux and Arch bases
#Installing last release (recommended)

    $ yaourt -S persepolis

#Installing with latest chang on github

	$ yaourt -S persepolis-git
Obviously you can't install both of persepolis and persepolis-git simoltaneously . and you must uninstall one of them(with pacman) for installing another one.
##For installing in Fedora

	$ sudo dnf copr enable amirsamimi/persepolis
	$ sudo dnf install persepolis

##For installing in openSUSE
	please visit this link : https://software.opensuse.org/download.html?project=home%3Ahayyan71&package=persepolis




### For other distributions (Installing from github)
## Before running install file make sure that all dependencies are installed on your system!
You must install `aria2` , `pulseaudio-utils` , `libnotify-bin` , `python 3` , `pyqt5` , `qt5-svg` , `python3-requests`

## Dependencies for Archlinux

    $ sudo pacman -S aria2 vorbis-tools libnotify python-pyqt5 qt5-svg python-requests

## Dependencies for Debian and Debian base distro.s (ubuntu 16.04 , ... )

    $ sudo apt-get install aria2 pulseaudio-utils libnotify-bin python3-pyqt5 libqt5svg5 python3-requests

## Dependencies for Fedora

    $ sudo dnf install aria2 pulseaudio-utils libnotify python3-qt5 qt5-qtsvg python3-requests

After installing dependencies, change your directory with cd command and run install file

    $ bash install

for uninstall,

    $ bash uninstall

### or...

    $ cd
    $ cd /tmp
    $ wget -O persepolis.tar.gz https://github.com/persepolisdm/persepolis/archive/master.tar.gz
    $ tar  --overwrite-dir -xf persepolis.tar.gz
    $ cd persepolis-master
    $ bash install

### or ...

    $ git clone "https://github.com/persepolisdm/persepolis.git" 
    $ cd persepolis
    $ bash install 

### Installation on Mac OS X
you must install aria2 python3 python3-requests python3-pyqt5 first! you can use homebrew for it.

    $ brew install python3
    $ brew install aria2
    $ brew install pyqt5
    $ pip3 install requests 

when dependencies installed :

    $ git clone "https://github.com/persepolisdm/persepolis.git" 
    $ cd persepolis
    $ bash install mac

for uninstallation

    $ git clone "https://github.com/persepolisdm/persepolis.git" 
    $ cd persepolis
    $ bash uninstall mac


in mac os x >> after installation run persepolis from terminal with this command

	$ persepolis
we started developing persepolis for mac in just few days ago!It's not finished yet!


##Configuring PersepolisDM to use with FlashGot
open firefox
open menu
click add-ons
![ScreenShot](http://s9.picofile.com/file/8269073968/addons.jpg)
click on get add-ons
in the search box search the flashgot
then click on install and install it
restart the firefox (close and open it again)

then after opening firefox go to Extensions and find flashgot

![ScreenShot](http://s9.picofile.com/file/8269074242/prefrences.jpg)

then click on preferences and click add
write Persepolis Download Manager and select this file for executble path (in linux)

	$ /usr/bin/persepolis

and (in Mac)

    $ /usr/local/bin/persepolis 

then in the white field copy/paste the following codes

	$  [--link URL][--name FNAME][--referer REFERER][--headers HEADERS][--agent UA][--cookie COOKIE]

![ScreenShot](http://s1.picofile.com/file/8264685818/flashgot1.png)

then at the end click on the advance tab and uncheck automatic download manager detection

![ScreenShot](http://s9.picofile.com/file/8269073134/flashgot4.jpg)

and on media tab select Persepolis Download Manager

![ScreenShot](http://s9.picofile.com/file/8269073384/flashgot3.jpg)

uncheck this too!

![ScreenShot](http://s8.picofile.com/file/8269073684/flashgot2.jpg)

then Click OK and enjoy!!

you can use flashgot for download from youtube , ...

![ScreenShot](http://s9.picofile.com/file/8269074434/mediafire_download.jpg)

![ScreenShot](http://s8.picofile.com/file/8269074500/youtube_download.jpg)



## Contact us
Persepolis code developer : Alireza Amirsamimi
https://github.com/alireza-amirsamimi
alireza.amirsamimi@ubuntu.ir

Arch repository maintainer : Mohammadreza Abdollahzadeh
https://github.com/morealaz
morealaz@gmail.com

Launchpad repository maintainer : Mostafa Asadi
https://github.com/mostafaasadi
mostafaasadi73@gmail.com

Persepolis website developer : Sadegh Alirezaei
https://github.com/Alirezaies
alirezaie.sadegh@gmail.com

Persepolis website :
https://persepolisdm.github.io/

Persepolis persian website:
http://amirsamimi.ir/persepolis2


PersepolisDM Telegram Channel:
https://telegram.me/persepolisdm

## Read more about PERSEPOLIS
https://en.wikipedia.org/wiki/Persepolis
