Persepolis Download Manager 
=============
+ version : 2.0.0 Unstable
+ Persepolis Download Manager is a GUI for aria2.
+ Persepolis written in PYQT5.

![ScreenShot](http://s7.picofile.com/file/8259824642/persepolis1.jpg)

![ScreenShot](http://s6.picofile.com/file/8259824918/persepolis3.jpg)

![ScreenShot](http://s6.picofile.com/file/8259824992/persepolis2.jpg)

### Before running install file make sure that all dependencies are installed on your system!
You must install `aria2` , `vorbis-tools` , `libnotify-bin` , `python 3` , `pyqt5`

## Dependencies for Debian and Deabian base distro.s (ubuntu 16.04 , ... )

    $ sudo apt-get install aria2 vorbis-tools libnotify-bin python3-pyqt5

## Dependencies for Archlinux

    $ sudo pacman -S aria2 vorbis-tools libnotify python-pyq5

After installing dependencies, change your directory with cd command and run install file

    $ sh install

for uninstall,

    $ sh unistall

### or...

    $ cd
    $ cd /tmp
    $ wget -O persepolis.tar.gz https://github.com/alireza-amirsamimi/persepolis/archive/master.tar.gz
    $ tar  --overwrite-dir -xf persepolis.tar.gz
    $ cd persepolis-master
    $ sh install



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

	$  [--link URL][--name FNAME][--referer REFERER][--cookie COOKIE][--headers HEADERS][--agent UA]

![ScreenShot](http://s7.picofile.com/file/8259833218/flashgot2.jpg)

then at the end click on the advance tab and uncheck automatic download manager detection

![ScreenShot](http://s6.picofile.com/file/8259833276/flashgot5.jpg)

and on media tab select Persepolis Download Manager

![ScreenShot](http://s6.picofile.com/file/8259833242/flashgot4.jpg)

uncheck this too!

![ScreenShot](http://s6.picofile.com/file/8259833226/flashgot3.jpg)

then Click OK and enjoy!!

you can use flashgot for download from youtube , ...

![ScreenShot](http://s4.picofile.com/file/8179632850/11.jpg)

![ScreenShot](http://s6.picofile.com/file/8179631500/10.jpg)



## Contact me
Me on twiter:
https://twitter.com/AR_AmirSamimi

My website:
http://amirsamimi.ir

My email adress:
alireza.amirsamimi@ubuntu.ir

PersepolisDM Telegram Channel:
https://telegram.me/persepolisdm

## Read more about PERSEPOLIS
https://en.wikipedia.org/wiki/Persepolis
