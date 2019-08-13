FROM gitpod/workspace-full

USER root

RUN apt-get install aria2 sound-theme-freedesktop libnotify-bin python3-pyqt5 libqt5svg5 python3-requests python3-setproctitle python3-setuptools python3-psutil youtube-dl ffmpeg python3-pyqt5.qtsvg adwaita-qt