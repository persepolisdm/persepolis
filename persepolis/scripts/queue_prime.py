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

from time import sleep
from persepolis.scripts import logger
from persepolis.scripts.bubble import notifySend
from persepolis.scripts import persepolis_lib_prime
from persepolis.scripts.video_finder import VideoFinder
from persepolis.scripts.download_link import DownloadLink

try:
    from PySide6.QtCore import QThread, Signal, QCoreApplication
except:
    from PyQt5.QtCore import QThread, QCoreApplication
    from PyQt5.QtCore import pyqtSignal as Signal
try:
    from persepolis.scripts import ytdlp_downloader
except ModuleNotFoundError:
    # if youtube_dl module is not installed:
    logger.sendToLog(
        "yt-dlp is not installed.", "ERROR")


class Queue():
    def __init__(self, queue_dict, main_window):
        self.queue_name = queue_dict['category']
        self.start_time_enable = queue_dict['start_time_enable']
        self.start_time = queue_dict['start_time']
        self.end_time_enable = queue_dict['end_time_enable']
        self.end_time = queue_dict['end_time']
        self.reverse = queue_dict['reverse']
        self.limit_enable = queue_dict['limit_enable']
        self.limit_value = queue_dict['limit_value']
        self.after_download = queue_dict['after_download']
        self.gid_list = queue['gid_list']
        self.main_window = main_window

    def start(self):

