# -*- coding: utf-8 -*-
"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import json
import re
from random import random
from time import time, sleep

import subprocess

import os
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QPushButton, QTextEdit, QFrame, QLabel, QComboBox, QHBoxLayout, QApplication
from copy import deepcopy

from persepolis.scripts import logger, osCommands
from persepolis.scripts.spider import spider

from persepolis.scripts.addlink import AddLinkWindow


class YoutubeAddLink(AddLinkWindow):
    formats_showing = []
    media_title = ''
    running_thread = None
    threadPool = {}

    def __init__(self, parent, receiver_slot, settings, video_dict={}):
        super().__init__(parent, receiver_slot, settings, video_dict)
        self.setWindowTitle('Youtube Video Downloader')
        self.size_label.hide()

        # Fetch Button
        self.url_submit_button = QPushButton(self.link_frame)
        self.link_horizontalLayout.addWidget(self.url_submit_button)

        # Status Box
        self.status_box = QTextEdit(self.link_frame)
        self.status_box.setMaximumHeight(150)
        self.link_verticalLayout.addWidget(self.status_box)

        # Select format horizontal layout
        select_format_hl = QHBoxLayout()
        # Selection Label
        select_format_label = QLabel(self.link_frame)
        select_format_hl.addWidget(select_format_label)
        # Selection combobox
        self.media_combo = QComboBox(self.link_frame)
        self.media_combo.setMinimumWidth(200)
        select_format_hl.addWidget(self.media_combo)
        # Duration label
        self.duration_label = QLabel(self.link_frame)
        select_format_hl.addWidget(self.duration_label)

        self.selection_line = QFrame(self)
        self.selection_line.setLayout(select_format_hl)
        self.link_verticalLayout.addWidget(self.selection_line)

        # Add Slot Connections
        self.url_submit_button.clicked.connect(self.submit_clicked)
        self.media_combo.currentIndexChanged.connect(self.media_selection_changed)
        self.link_lineEdit.textChanged.disconnect(super().linkLineChanged)  # Should be disconnected.
        self.link_lineEdit.textChanged.connect(self.linkLineChangedHere)

        self.url_submit_button.setEnabled(False)
        self.change_name_lineEdit.setEnabled(False)
        self.ok_pushButton.setEnabled(False)
        self.download_later_pushButton.setEnabled(False)

        self.setMinimumSize(500, 400)

        # Set Texts
        self.url_submit_button.setText('Fetch Media List')
        self.ok_pushButton.setText('Download Now')
        select_format_label.setText('Select a format')

        if 'referer' in video_dict.keys() and video_dict['link']:
            self.link_lineEdit.setText(video_dict['link'])
            self.link_lineEdit.setEnabled(False)
            self.submit_clicked()
        else:
            clipboard = QApplication.clipboard()
            text = str(clipboard.text())
            if ' ' not in text and 'youtube.com/watch' in text:
                self.link_lineEdit.setText(text)
                self.url_submit_button.setEnabled(True)
            self.status_box.hide()
            self.selection_line.hide()

    # Define native slots

    def url_changed(self, value):
        if ' ' in value or 'youtube.com/watch?' not in value:
            self.url_submit_button.setEnabled(False)
            self.url_submit_button.setToolTip('Please enter a valid youtube video link')
        else:
            self.url_submit_button.setEnabled(True)
            self.url_submit_button.setToolTip('')

    def submit_clicked(self, button=None):
        # Clear media list
        self.media_combo.clear()
        self.selection_line.hide()
        self.change_name_lineEdit.clear()
        self.threadPool.clear()
        self.change_name_checkBox.setChecked(False)
        self.formats_showing.clear()
        self.url_submit_button.setEnabled(False)
        self.status_box.setText('Fetching Media Info...')
        self.status_box.show()
        self.ok_pushButton.setEnabled(False)
        self.download_later_pushButton.setEnabled(False)

        dictionary_to_send = deepcopy(self.plugin_add_link_dictionary)
        # More options
        more_options = self.collect_more_options()
        for k in more_options.keys():
            dictionary_to_send[k] = more_options[k]
        dictionary_to_send['link'] = self.link_lineEdit.text()
        fetcher_thread = MediaListFetcherThread(self.fetched_result, dictionary_to_send, self.persepolis_setting)
        self.running_thread = fetcher_thread
        fetcher_thread.start()

    def filename_changed(self, value):
        if value.strip() == '':
            self.ok_pushButton.setEnabled(False)

    def media_selection_changed(self):
        try:
            self.change_name_lineEdit.setText(self.media_title + '.' +
                                              self.formats_showing[self.media_combo.currentIndex()]['ext'])
        except:
            print(self.formats_showing.__len__(), self.media_combo.currentIndex())

    def okButtonPressed(self, button, download_later):
        index = self.media_combo.currentIndex()
        self.plugin_add_link_dictionary['link'] = self.formats_showing[index]['url']
        self.plugin_add_link_dictionary['out'] = self.change_name_lineEdit.text()
        super().okButtonPressed(button, download_later)

    def fetched_result(self, media_dict):
        self.url_submit_button.setEnabled(True)
        if 'error' in media_dict.keys():
            self.status_box.setText('<font color="#f11">' + str(media_dict['error']) + '</font>')
            self.status_box.show()
        else:  # Show the media list
            self.media_title = media_dict['fulltitle']
            i = 0
            for f in media_dict['formats']:
                try:
                    if f['acodec'] == 'none' and f['vcodec'] != 'none' and self.persepolis_setting.value('youtube/hide_no_audio', 'no') == 'yes':
                        continue
                    if f['vcodec'] == 'none' and f['acodec'] != 'none' and self.persepolis_setting.value('youtube/hide_no_video', 'no') == 'yes':
                        continue

                    if f['vcodec'] == 'none':  # No video, show audio bit rate
                        text = 'Only Audio {}kbps'.format(f['abr'])
                    elif f['acodec'] == 'none':
                        text = 'No Audio {}p'.format(f['height'])
                    else:
                        text = '{}p'.format(f['height'])
                    text = '{} .{}'.format(text, f['ext'])
                    if 'filesize' in f.keys() and f['filesize']:
                        # Youtube api does not supply file size for some formats, so check it.
                        text = '{} - {}'.format(text, get_readable_size(f['filesize']))
                    else:  # Start spider to find file size
                        input_dict = deepcopy(self.plugin_add_link_dictionary)
                        # input_dict['out'] = self.media_title + str(f['ext'])
                        input_dict['link'] = f['url']
                        more_options = self.collect_more_options()
                        for key in more_options.keys():
                            input_dict[key] = more_options[key]
                        size_fetcher = FileSizeFetcherThread(input_dict, i, self.file_size_found)
                        self.threadPool[str(i)] = {'thread': size_fetcher, 'item_id': i}
                        size_fetcher.start()

                    # Add current format to combobox
                    self.formats_showing.append(f)
                    self.media_combo.addItem(text)
                    i = i + 1
                except Exception as ex:
                    logger.sendToLog(ex, "ERROR")

            self.status_box.hide()
            self.duration_label.setText('Duration ' + get_readable_duration(media_dict['duration']))
            self.selection_line.show()
            self.ok_pushButton.setEnabled(True)
            self.download_later_pushButton.setEnabled(True)

    def file_size_found(self, result):
        try:
            item_id = self.threadPool[str(result['thread_key'])]['item_id']
            if result['file_size'] and result['file_size'] != '0':
                text = self.media_combo.itemText(item_id)
                self.media_combo.setItemText(item_id, '{} - {}'.format(text, result['file_size']))
            else:  # Retry
                sleep(0.8)
                self.threadPool[str(result['thread_key'])]['thread'].start()
        except Exception as ex:
            print('Error: ' + str(ex))

    def linkLineChangedHere(self, lineEdit):
        if 'youtube.com/watch' not in str(self.link_lineEdit.text()):
            self.url_submit_button.setEnabled(False)
        else:
            self.url_submit_button.setEnabled(True)

            # if 'googlevideo.com/videoplayback' not in str(self.link_lineEdit.text()):
            #     self.ok_pushButton.setEnabled(False)
            #     self.download_later_pushButton.setEnabled(False)
            # else:
            #     self.ok_pushButton.setEnabled(True)
            #     self.download_later_pushButton.setEnabled(True)

    # This method collects additional information like proxy ip, user, password etc.
    def collect_more_options(self):
        options = {'ip': None, 'port': None, 'proxy_user': None, 'proxy_passwd': None, 'download_user': None,
                   'download_passwd': None}
        if self.proxy_checkBox.isChecked():
            options['ip'] = self.ip_lineEdit.text()
            options['port'] = self.port_spinBox.value()
            options['proxy_user'] = self.proxy_user_lineEdit.text()
            options['proxy_passwd'] = self.proxy_pass_lineEdit.text()
        if self.download_checkBox.isChecked():
            options['download_user'] = self.download_user_lineEdit.text()
            options['download_passwd'] = self.download_pass_lineEdit.text()

        # These info (keys) are required for spider to find file size, because spider() does not check if key exists.
        additional_info = ['header', 'load_cookies', 'user_agent', 'referer', 'out']
        for i in additional_info:
            if i not in self.plugin_add_link_dictionary.keys():
                options[i] = None
        return options


class MediaListFetcherThread(QThread):
    RESULT = pyqtSignal(dict)
    cookies = '# HTTP cookie file.\n'  # We shall write it in a file when thread starts.

    def __init__(self, receiver_slot, video_dict, pdm_setting):
        super().__init__()
        self.RESULT.connect(receiver_slot)
        self.video_dict = video_dict
        self.pdm_setting = pdm_setting

        if pdm_setting.value('youtube/youtube_dl_path', ''):
            youtube_dl_path = pdm_setting.value('youtube/youtube_dl_path', 'youtube-dl')  # Ambiguous ?
            self.youtube_dl_command = [youtube_dl_path, '--ignore-config', '--dump-json', '--no-playlist']

            self.cookie_path = os.path.join(self.pdm_setting.value('youtube/cookie_path'),
                                            '.{}{}'.format(time(), random()))
            self.youtube_dl_command.append('--cookies="{}"'.format(self.cookie_path))

            if 'referer' in video_dict.keys() and video_dict['referer']:
                self.youtube_dl_command.append('--referer="{}"'.format(video_dict['referer']))
            if 'user_agent' in video_dict.keys() and video_dict['user_agent']:
                self.youtube_dl_command.append('--user-agent="{}"'.format(video_dict['user_agent']))
            # if 'referer' in video_dict.keys() and video_dict['header']:
            #     self.youtube_dl_command.append('--add-header=' + str(video_dict['header']))
            if 'load_cookies' in video_dict.keys() and video_dict['load_cookies']:
                # We need to convert raw cookies to http cookie file to use with youtube-dl.
                self.cookies = make_http_cookie(video_dict['load_cookies'])

            # Proxy check
            if 'ip' in video_dict.keys() and video_dict['ip']:
                try:
                    ip_port = 'http://{}:{}'.format(video_dict['ip'], video_dict['port'])
                    if 'referer' in video_dict.keys() and video_dict['proxy_user']:
                        ip_port = 'http://{}:{}@{}'.format(video_dict['proxy_user'], video_dict['proxy_passwd'], ip_port)
                    self.youtube_dl_command.append('--proxy="{}"'.format(ip_port))
                except:
                    pass
            if 'download_user' in video_dict.keys() and video_dict['download_user']:
                try:
                    self.youtube_dl_command.append('--username="{}"'.format(video_dict['download_user']))
                    self.youtube_dl_command.append('--password="{}"'.format(video_dict['download_passwd']))
                except:
                    pass

            if 'link' in video_dict.keys() and video_dict['link']:
                self.youtube_dl_command.append(video_dict['link'])

    def run(self):
        if not self.pdm_setting.value('youtube/youtube_dl_path', ''):
            return self.RESULT.emit({'error': "Error! 'youtube-dl' path not specified. \
            Please go to Preferences > Youtube Options > specify 'youtube-dl' executable path \
            or disable this feature."})
        ret_val = {}

        try:  # Create cookie file
            cookie_file = open(self.cookie_path, 'w')
            cookie_file.write(self.cookies)
            cookie_file.close()
            fetch_process = subprocess.Popen(self.youtube_dl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result, error = fetch_process.communicate()
            error = error.splitlines()[0]  # Or comment out this line to show full stderr.
            if result:
                data = json.loads(result.decode())
                ret_val = data
            else:
                ret_val = {'error': str(error.decode())}
        except PermissionError:
            ret_val = {'error': "Oops! cannot execute specified 'youtube-dl', \
            make sure it is executable."}
        except FileNotFoundError:
            ret_val = {'error': "Oops! 'youtube-dl' seems to be not installed. <br/> \
                Please install the package and make sure it is executable."}
        except json.decoder.JSONDecodeError:
            ret_val = {'error': 'Error: Cannot Decode JSON output.<br/>'
                                'Make sure you specified correct "youtube-dl" path in preferences.'}
        except Exception as ex:
            ret_val = {'error': str(ex)}
        finally:  # Delete cookie file
            try:
                osCommands.remove(self.cookie_path)
            except Exception as ex:
                logger.sendToLog(ex, "ERROR")

        self.RESULT.emit(ret_val)


class FileSizeFetcherThread(QThread):
    FOUND = pyqtSignal(dict)
    __MAX_USAGE_ALLOWED = 3  # Prevent the same thread to start indefinitely if file size is not resolved.

    def __init__(self, dictionary, thread_key, receiver_slot):
        super().__init__()
        self.FOUND.connect(receiver_slot)
        self.dictionary = dictionary
        self.key = thread_key

    def run(self):
        if self.__MAX_USAGE_ALLOWED:
            self.__MAX_USAGE_ALLOWED = self.__MAX_USAGE_ALLOWED - 1
            self.FOUND.emit({'thread_key': self.key, 'file_size': spider(self.dictionary)[1]})


def get_readable_size(size):
    try:
        return '{:1.2f} MB'.format(int(size) / 1048576)
    except:
        return str(size)


def get_readable_duration(seconds):
    try:
        seconds = int(seconds)
        hours = seconds // 3600
        seconds = seconds % 3600
        minutes = seconds // 60
        seconds = seconds % 60
        return '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)
    except:
        return str(seconds)


def make_http_cookie(raw_cookie, host_name='.youtube.com'):
    cookies = '# HTTP cookie file.\n'
    if raw_cookie:
        try:
            raw_cookies = re.split(';\s*', str(raw_cookie))
            # Format all cookie values as netscape cookie.
            for c in raw_cookies:
                key, val = c.split('=', 1)
                cookies = cookies + '{}\tTRUE\t/\tFALSE\t{}\t{}\t{}\n'. \
                    format(host_name, int(time()) + 259200, key, val)  # Expires after 3 days.
        except:
            pass

    return cookies
