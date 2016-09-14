Persepolis Download Manager 
=============
+ version : 2.1.1 Unstable
+ Persepolis Download Manager is a GUI for aria2.
+ Persepolis written in PYQT5.


![ScreenShot](http://s1.picofile.com/file/8264685926/persepolis.jpg)


### Before running install file make sure that all dependencies are installed on your system!
You must install `aria2` , `vorbis-tools` , `libnotify-bin` , `python 3` , `pyqt5` , `qt5-svg`

## Dependencies for Archlinux

    $ sudo pacman -S aria2 vorbis-tools libnotify python-pyqt5 qt5-svg

## Dependencies for Debian and Debian base distro.s (ubuntu 16.04 , ... )

    $ sudo apt-get install aria2 vorbis-tools libnotify-bin python3-pyqt5 libqt5svg5

## Dependencies for Fedora

    $ sudo dnf install aria2 vorbis-tools libnotify python3-qt5 qt5-qtsvg

After installing dependencies, change your directory with cd command and run install file

    $ sh install

for uninstall,

    $ sh uninstall

### or...

    $ cd
    $ cd /tmp
    $ wget -O persepolis.tar.gz https://github.com/alireza-amirsamimi/persepolis/archive/master.tar.gz
    $ tar  --overwrite-dir -xf persepolis.tar.gz
    $ cd persepolis-master
    $ sh install

##Alternative way for installing in ArchLinux

    $ yaourt -S persepolis-git

##Configuring PersepolisDM to use with FlashGot
open firefox
open menu
click add-ons
click on get add-ons
in the search box search the flashgot
then click on install and install it
restart the firefox (close and open it again)

![ScreenShot](http://s6.picofile.com/file/8259833184/flashgot.jpg)

then after opening firefox go to Extensions and find flashgot
then click on preferences and click add
write Persepolis Download Manager and select this file for executble path

	$ /usr/bin/persepolis


then in the white field copy/paste the following codes

	$  [--link URL][--name FNAME][--referer REFERER][--headers HEADERS][--agent UA][--cookie COOKIE]

![ScreenShot](http://s1.picofile.com/file/8264685818/flashgot1.png)

then at the end click on the advance tab and uncheck automatic download manager detection

![ScreenShot](http://s2.picofile.com/file/8264685876/flashgot4.png)

and on media tab select Persepolis Download Manager

![ScreenShot](http://s1.picofile.com/file/8264685868/flashgot3.png)

uncheck this too!

![ScreenShot](http://s2.picofile.com/file/8264685834/flashgot2.png)

then Click OK and enjoy!!

you can use flashgot for download from youtube , ...

![ScreenShot](http://s4.picofile.com/file/8179632850/11.jpg)

![ScreenShot](http://s6.picofile.com/file/8179631500/10.jpg)



## Contact us
Persepolis code developer : Alireza Amirsamimi
https://github.com/alireza-amirsamimi
alireza.amirsamimi@ubuntu.ir

Arch repository maintainer : Mohammadreza Abdollahzadeh
https://github.com/morealaz
morealaz@gmail.com

Persepolis website developer : Sadegh Alirezaei
https://github.com/Alirezaies
Alirezaie.Sadegh@gmail.Com


Persepolis persian website:
http://amirsamimi.ir/persepolis2


PersepolisDM Telegram Channel:
https://telegram.me/persepolisdm

## Read more about PERSEPOLIS
https://en.wikipedia.org/wiki/Persepolis
