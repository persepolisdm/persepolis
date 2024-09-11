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
try:
    from PySide6.QtWidgets import QCheckBox, QPushButton, QTextEdit, QFrame, QLabel, QComboBox, QHBoxLayout, QApplication
    from PySide6.QtCore import QThread, Signal, QCoreApplication, QTranslator, QLocale
except:
    from PyQt5.QtWidgets import QCheckBox, QPushButton, QTextEdit, QFrame, QLabel, QComboBox, QHBoxLayout, QApplication
    from PyQt5.QtCore import QThread, QCoreApplication, QTranslator, QLocale
    from PyQt5.QtCore import pyqtSignal as Signal

from persepolis.scripts.useful_tools import determineConfigFolder, dictToHeader
from persepolis.scripts.addlink import AddLinkWindow
from persepolis.scripts import logger, osCommands
from persepolis.scripts.spider import spider
from persepolis.constants import VERSION
from time import time
from functools import partial
from random import random
from copy import deepcopy
import yt_dlp as youtube_dl
import re
import os

# write youtube_dl version in log
logger.sendToLog('yt-dlp version: '
                 + str(youtube_dl.version.__version__),
                 'INFO')

# download manager config folder .
config_folder = determineConfigFolder()

# persepolis tmp folder path
persepolis_tmp = os.path.join(config_folder, 'persepolis_tmp')


class MediaListFetcherThread(QThread):
    RESULT = Signal(dict)
    cookies = '# HTTP cookie file.\n'  # We shall write it in a file when thread starts.
    LOADCOOKIEFILESIGNAL = Signal(str)

    def __init__(self, receiver_slot, video_dict, main_window):
        super().__init__()
        self.RESULT.connect(receiver_slot)
        self.video_dict = video_dict

        self.cookie_path = os.path.join(persepolis_tmp, '.{}{}'.format(time(), random()))

        # check certificate
        if str(main_window.persepolis_setting.value('settings/dont-check-certificate')) == 'yes':
            self.dont_check_certificate = True
        else:
            self.dont_check_certificate = False

        # youtube options must be added to youtube_dl_options_dict in dictionary format
        self.youtube_dl_options_dict = {'dump_single_json': True,
                                        'quiet': True,
                                        'noplaylist': True,
                                        'no_warnings': True,
                                        'no-check-certificates': self.dont_check_certificate
                                        }

        # cookies
        self.youtube_dl_options_dict['cookies'] = str(self.cookie_path)

        # referer
        if 'referer' in video_dict.keys() and video_dict['referer']:
            self.youtube_dl_options_dict['referer'] = str(video_dict['referer'])

        # user_agent
        if 'user_agent' in video_dict.keys() and video_dict['user_agent']:
            self.youtube_dl_options_dict['user-agent'] = str(video_dict['user_agent'])
        else:
            # set PersepolisDM user agent
            video_dict['user_agent'] = 'PersepolisDM/' + str(VERSION.version_str)
            self.youtube_dl_options_dict['user-agent'] = 'PersepolisDM/' + str(VERSION.version_str)

        # load_cookies
        if 'load_cookies' in video_dict.keys() and video_dict['load_cookies']:
            # We need to convert raw cookies to http cookie file to use with youtube-dl.
            self.cookies = self.makeHttpCookie(video_dict['load_cookies'])

        # Proxy
        if video_dict['ip']:

            # ip + port
            ip_port = '{}:{}'.format(video_dict['ip'], str(video_dict['port']))

            if video_dict['proxy_user']:
                proxy_argument = '{}://{}:{}@{}'.format(video_dict['proxy_type'], video_dict['proxy_user'], video_dict['proxy_passwd'], ip_port)

            else:
                proxy_argument = '{}://{}'.format(video_dict['proxy_type'], ip_port)

            self.youtube_dl_options_dict['proxy'] = str(proxy_argument)

        if video_dict['download_user']:

            self.youtube_dl_options_dict['username'] = str(video_dict['download_user'])
            self.youtube_dl_options_dict['password'] = str(video_dict['download_passwd'])

        if video_dict['link']:
            self.youtube_link = str(video_dict['link'])

    def run(self):
        ret_val = {}

        try:  # Create cookie file
            cookie_file = open(self.cookie_path, 'w')
            cookie_file.write(self.cookies)
            cookie_file.close()

            ydl = youtube_dl.YoutubeDL(self.youtube_dl_options_dict)
            with ydl:
                result = ydl.extract_info(
                    self.youtube_link,
                    download=False
                )
            # write new cookies to cookie file
            ydl.cookiejar.save(filename=self.cookie_path)
            error = "error"  # Or comment out this line to show full stderr.
            if result:
                ret_val = result
            else:
                ret_val = {'error': str(error)}
                try:
                    osCommands.remove(self.cookie_path)

                except Exception as ex:
                    logger.sendToLog(ex, "ERROR")

        except Exception as ex:
            ret_val = {'error': str(ex)}
            try:
                osCommands.remove(self.cookie_path)

            except Exception as ex:
                logger.sendToLog(ex, "ERROR")

        self.LOADCOOKIEFILESIGNAL.emit(self.cookie_path)
        self.RESULT.emit(ret_val)

    def makeHttpCookie(self, raw_cookie, host_name='.youtube.com'):
        cookies = '# HTTP cookie file.\n'
        if raw_cookie:
            try:
                raw_cookies = re.split(';\\s*', str(raw_cookie))
                # Format all cookie values as netscape cookie.
                for c in raw_cookies:
                    key, val = c.split('=', 1)
                    cookies = cookies + '{}\tTRUE\t/\tFALSE\t{}\t{}\t{}\n'. \
                        format(host_name, int(time()) + 259200, key, val)  # Expires after 3 days.
            except:
                pass

        return cookies


class FileSizeFetcherThread(QThread):
    FOUND = Signal(dict)

    def __init__(self, dictionary, text, combobox_type, index):
        super().__init__()
        self.dictionary = dictionary
        self.text = text
        self.combobox_type = combobox_type
        self.index = index

    def run(self):
        spider_file_size = spider(self.dictionary)[1]
        self.FOUND.emit({'text': self.text,
                         'file_size': spider_file_size,
                         'combobox_type': self.combobox_type,
                         'index': self.index})


class VideoFinderAddLink(AddLinkWindow):
    running_thread = None
    threadPool = {}

    def __init__(self, parent, receiver_slot, settings, video_dict={}):
        super().__init__(parent, receiver_slot, settings, video_dict)
        self.setWindowTitle(QCoreApplication.translate("ytaddlink_src_ui_tr", 'Video Finder'))
        self.size_label.hide()

        # empty lists for no_audio and no_video and video_audio files
        self.no_audio_list = []
        self.no_video_list = []
        self.video_audio_list = []
        self.cookie_path = None

        self.media_title = ''

        # add support for other languages
        locale = str(self.persepolis_setting.value('settings/locale'))
        QLocale.setDefault(QLocale(locale))
        self.translator = QTranslator()
        if self.translator.load(':/translations/locales/ui_' + locale, 'ts'):
            QCoreApplication.installTranslator(self.translator)

        # extension_label
        self.extension_label = QLabel(self.link_frame)
        self.change_name_horizontalLayout.addWidget(self.extension_label)

        # Fetch Button
        self.url_submit_pushButtontton = QPushButton(self.link_frame)
        self.link_horizontalLayout.addWidget(self.url_submit_pushButtontton)

        # Status Box
        self.status_box_textEdit = QTextEdit(self.link_frame)
        self.status_box_textEdit.setMaximumHeight(150)
        self.link_verticalLayout.addWidget(self.status_box_textEdit)

        # Select format horizontal layout
        select_format_horizontalLayout = QHBoxLayout()

        # Selection Label
        self.select_format_label = QLabel(self.link_frame)
        select_format_horizontalLayout.addWidget(self.select_format_label)

        # Selection combobox
        self.media_comboBox = QComboBox(self.link_frame)
        self.media_comboBox.setMinimumWidth(200)
        select_format_horizontalLayout.addWidget(self.media_comboBox)

        # Duration label
        self.duration_label = QLabel(self.link_frame)
        select_format_horizontalLayout.addWidget(self.duration_label)

        self.format_selection_frame = QFrame(self)
        self.format_selection_frame.setLayout(select_format_horizontalLayout)
        self.link_verticalLayout.addWidget(self.format_selection_frame)

        # advanced_format_selection_checkBox
        self.advanced_format_selection_checkBox = QCheckBox(self)
        self.link_verticalLayout.addWidget(self.advanced_format_selection_checkBox)

        # advanced_format_selection_frame
        self.advanced_format_selection_frame = QFrame(self)
        self.link_verticalLayout.addWidget(self.advanced_format_selection_frame)

        advanced_format_selection_horizontalLayout = QHBoxLayout(self.advanced_format_selection_frame)

        # video_format_selection
        self.video_format_selection_label = QLabel(self.advanced_format_selection_frame)
        self.video_format_selection_comboBox = QComboBox(self.advanced_format_selection_frame)

        # audio_format_selection
        self.audio_format_selection_label = QLabel(self.advanced_format_selection_frame)
        self.audio_format_selection_comboBox = QComboBox(self.advanced_format_selection_frame)

        for widget in [self.video_format_selection_label,
                       self.video_format_selection_comboBox,
                       self.audio_format_selection_label,
                       self.audio_format_selection_comboBox]:
            advanced_format_selection_horizontalLayout.addWidget(widget)

        # Set Texts
        self.url_submit_pushButtontton.setText(QCoreApplication.translate("ytaddlink_src_ui_tr", 'Fetch Media List'))
        self.select_format_label.setText(QCoreApplication.translate("ytaddlink_src_ui_tr", 'Select a format'))

        self.video_format_selection_label.setText(QCoreApplication.translate("ytaddlink_src_ui_tr", 'Video format:'))
        self.audio_format_selection_label.setText(QCoreApplication.translate("ytaddlink_src_ui_tr", 'Audio format:'))

        self.advanced_format_selection_checkBox.setText(
            QCoreApplication.translate("ytaddlink_src_ui_tr", 'Advanced options'))

        # Add Slot Connections
        self.url_submit_pushButtontton.setEnabled(False)
        self.change_name_lineEdit.setEnabled(False)
        self.ok_pushButton.setEnabled(False)
        self.download_later_pushButton.setEnabled(False)

        self.format_selection_frame.setEnabled(True)
        self.advanced_format_selection_frame.setEnabled(False)
        self.advanced_format_selection_checkBox.toggled.connect(self.advancedFormatFrame)

        self.url_submit_pushButtontton.clicked.connect(self.submitClicked)

        self.media_comboBox.activated.connect(
            partial(self.mediaSelectionChanged, 'video_audio'))

        self.video_format_selection_comboBox.activated.connect(
            partial(self.mediaSelectionChanged, 'video'))

        self.audio_format_selection_comboBox.activated.connect(
            partial(self.mediaSelectionChanged, 'audio'))

        self.link_lineEdit.textChanged.disconnect(super().linkLineChanged)  # Should be disconnected.
        self.link_lineEdit.textChanged.connect(self.linkLineChangedHere)

        self.setMinimumSize(650, 480)

        self.status_box_textEdit.hide()
        self.format_selection_frame.hide()
        self.advanced_format_selection_frame.hide()
        self.advanced_format_selection_checkBox.hide()

        if 'link' in video_dict.keys() and video_dict['link']:
            self.link_lineEdit.setText(video_dict['link'])
            self.url_submit_pushButtontton.setEnabled(True)
        else:
            # check clipboard
            clipboard = QApplication.clipboard()
            text = clipboard.text()
            if (("tp:/" in text[2:6]) or ("tps:/" in text[2:7])):
                self.link_lineEdit.setText(str(text))

            self.url_submit_pushButtontton.setEnabled(True)

    def advancedFormatFrame(self, button):
        if self.advanced_format_selection_checkBox.isChecked():

            self.advanced_format_selection_frame.setEnabled(True)
            self.format_selection_frame.setEnabled(False)
            self.mediaSelectionChanged('video', int(self.video_format_selection_comboBox.currentIndex()))

        else:
            self.advanced_format_selection_frame.setEnabled(False)
            self.format_selection_frame.setEnabled(True)
            self.mediaSelectionChanged('video_audio', int(self.media_comboBox.currentIndex()))

    def getReadableSize(self, size):
        try:
            return '{:1.2f} MB'.format(int(size) / 1048576)
        except:
            return str(size)

    def getReadableDuration(self, seconds):
        try:
            seconds = int(seconds)
            hours = seconds // 3600
            seconds = seconds % 3600
            minutes = seconds // 60
            seconds = seconds % 60
            return '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)
        except:
            return str(seconds)

    # Define native slots

    def urlChanged(self, value):
        if ' ' in value or value == '':
            self.url_submit_pushButtontton.setEnabled(False)
            self.url_submit_pushButtontton.setToolTip(QCoreApplication.translate(
                "ytaddlink_src_ui_tr", 'Please enter a valid video link'))
        else:
            self.url_submit_pushButtontton.setEnabled(True)
            self.url_submit_pushButtontton.setToolTip('')

    def submitClicked(self, button=None):
        # Clear media list
        self.media_comboBox.clear()
        self.format_selection_frame.hide()
        self.advanced_format_selection_checkBox.hide()
        self.advanced_format_selection_frame.hide()
        self.video_format_selection_comboBox.clear()
        self.audio_format_selection_comboBox.clear()
        self.change_name_lineEdit.clear()
        self.threadPool.clear()
        self.change_name_checkBox.setChecked(False)
        self.video_audio_list.clear()
        self.no_video_list.clear()
        self.no_audio_list.clear()
        self.url_submit_pushButtontton.setEnabled(False)
        self.status_box_textEdit.setText(QCoreApplication.translate("ytaddlink_src_ui_tr", 'Fetching Media Info...'))
        self.status_box_textEdit.show()
        self.ok_pushButton.setEnabled(False)
        self.download_later_pushButton.setEnabled(False)

        dictionary_to_send = deepcopy(self.plugin_add_link_dictionary)
        # More options
        more_options = self.collectMoreOptions()

        for k in more_options.keys():
            dictionary_to_send[k] = more_options[k]

        dictionary_to_send['link'] = self.link_lineEdit.text()
        dictionary_to_send['socket-timeout'] = '5'

        fetcher_thread = MediaListFetcherThread(self.fetchedResult, dictionary_to_send, self.parent)
        self.parent.threadPool.append(fetcher_thread)
        self.parent.threadPool[-1].start()
        self.parent.threadPool[-1].LOADCOOKIEFILESIGNAL.connect(self.setLoadCookie)

    def setLoadCookie(self, str):
        if os.path.isfile(str):
            self.cookie_path = str
            self.load_cookies_lineEdit.setText(str)

    def fileNameChanged(self, value):
        if value.strip() == '':
            self.ok_pushButton.setEnabled(False)

    def mediaSelectionChanged(self, combobox, index):
        try:
            if combobox == 'video_audio':
                if self.media_comboBox.currentText() == 'Best quality':
                    self.change_name_lineEdit.setText(self.media_title)
                    self.extension_label.setText('.' + self.no_audio_list[-1]['ext'])

                else:
                    self.change_name_lineEdit.setText(self.media_title)
                    self.extension_label.setText('.' + self.video_audio_list[index]['ext'])

                self.change_name_checkBox.setChecked(True)

            elif combobox == 'video':
                if self.video_format_selection_comboBox.currentText() != 'No video':
                    self.change_name_lineEdit.setText(self.media_title)
                    self.extension_label.setText('.' + self.no_audio_list[index - 1]['ext'])
                    self.change_name_checkBox.setChecked(True)

                else:

                    if self.audio_format_selection_comboBox.currentText() != 'No audio':
                        self.change_name_lineEdit.setText(self.media_title)
                        self.extension_label.setText('.'
                                                     + self.no_video_list[int(self.audio_format_selection_comboBox.currentIndex()) - 1]['ext'])

                        self.change_name_checkBox.setChecked(True)
                    else:
                        self.change_name_lineEdit.setChecked(False)

            elif combobox == 'audio':
                if self.audio_format_selection_comboBox.currentText() != 'No audio' and self.video_format_selection_comboBox.currentText() == 'No video':
                    self.change_name_lineEdit.setText(self.media_title)
                    self.extension_label.setText('.'
                                                 + self.no_video_list[index - 1]['ext'])

                    self.change_name_checkBox.setChecked(True)

                elif (self.audio_format_selection_comboBox.currentText() == 'No audio' and self.video_format_selection_comboBox.currentText() != 'No video') or (self.audio_format_selection_comboBox.currentText() != 'No audio' and self.video_format_selection_comboBox.currentText() != 'No video'):
                    self.change_name_lineEdit.setText(self.media_title)
                    self.extension_label.setText('.'
                                                 + self.no_audio_list[int(self.video_format_selection_comboBox.currentIndex()) - 1]['ext'])

                    self.change_name_checkBox.setChecked(True)

                elif self.audio_format_selection_comboBox.currentText() == 'No audio' and self.video_format_selection_comboBox.currentText() == 'No video':
                    self.change_name_checkBox.setChecked(False)

        except Exception as ex:
            logger.sendToLog(ex, "ERROR")

    def fetchedResult(self, media_dict): # noqa

        self.url_submit_pushButtontton.setEnabled(True)
        if 'error' in media_dict.keys():

            self.status_box_textEdit.setText('<font color="#f11">' + str(media_dict['error']) + '</font>')
            self.status_box_textEdit.show()
        else:  # Show the media list

            # add no audio and no video options to the comboboxes
            self.video_format_selection_comboBox.addItem('No video')
            self.audio_format_selection_comboBox.addItem('No audio')

            self.media_title = media_dict['title']
            if 'formats' not in media_dict.keys() and 'entries' in media_dict.keys():
                formats = media_dict['entries']
                formats = formats[0]
                media_dict['formats'] = formats['formats']
            elif 'formats' not in media_dict.keys() and 'format' in media_dict.keys():
                media_dict['formats'] = [media_dict.copy()]

            try:
                i = 0
                for f in media_dict['formats']:
                    no_audio = False
                    no_video = False
                    text = ''

                    # set http_headers
                    if 'http_headers' in f.keys():
                        header_dict = f['http_headers']

                        if 'User-Agent' in header_dict.keys():
                            self.user_agent_lineEdit.setText(header_dict['User-Agent'])
                            self.plugin_add_link_dictionary['user-agent'] = header_dict['User-Agent']
                            header_dict.pop('User-Agent')

                        if 'Referer' in header_dict.keys():
                            self.referer_lineEdit.setText(header_dict['Referer'])
                            self.plugin_add_link_dictionary['referer'] = header_dict['Referer']
                            header_dict.pop('Referer')

                        self.plugin_add_link_dictionary['header'] = dictToHeader(header_dict)
                        self.header_lineEdit.setText(self.plugin_add_link_dictionary['header'])

                    if 'acodec' in f.keys():
                        # only video, no audio
                        if f['acodec'] == 'none':
                            no_audio = True

                        # resolution
                        if 'height' in f.keys():
                            text = text + ' ' + '{}p'.format(f['height'])

                    if 'vcodec' in f.keys():
                        #                         if f['vcodec'] == 'none' and f['acodec'] != 'none':
                        #                             continue

                        # No video, show audio bit rate
                        if f['vcodec'] == 'none':
                            text = text + '{}kbps'.format(f['abr'])
                            no_video = True

                    if 'ext' in f.keys():
                        text = text + ' ' + '.{}'.format(f['ext'])

                    if 'filesize' in f.keys() and f['filesize']:
                        # Youtube api does not supply file size for some formats, so check it.
                        text = text + ' ' + '{}'.format(self.getReadableSize(f['filesize']))
                        size_available = True
                    else:  # Start spider to find file size
                        size_available = False
                        input_dict = deepcopy(self.plugin_add_link_dictionary)

                        input_dict['link'] = f['url']
                        more_options = self.collectMoreOptions()

                        for key in more_options.keys():
                            input_dict[key] = more_options[key]

                    # Add current format to the related comboboxes
                    if no_audio:
                        combobox_type = 'video'
                        self.no_audio_list.append(f)
                        self.video_format_selection_comboBox.addItem(text)
                        index = self.video_format_selection_comboBox.count() - 1

                    elif no_video:
                        combobox_type = 'audio'
                        self.no_video_list.append(f)
                        self.audio_format_selection_comboBox.addItem(text)
                        index = self.audio_format_selection_comboBox.count() - 1

                    else:
                        combobox_type = 'media'
                        self.video_audio_list.append(f)
                        self.media_comboBox.addItem(text)
                        index = self.media_comboBox.count() - 1

                    if not (size_available):
                        size_fetcher = FileSizeFetcherThread(input_dict, text, combobox_type, index)
                        self.threadPool[str(i)] = {'thread': size_fetcher, 'item_id': i}
                        self.parent.threadPool.append(size_fetcher)
                        self.parent.threadPool[-1].start()
                        self.parent.threadPool[-1].FOUND.connect(self.findFileSize)

                    i = i + 1

                self.status_box_textEdit.hide()

                if 'duration' in media_dict.keys():
                    self.duration_label.setText('Duration ' + self.getReadableDuration(media_dict['duration']))

                self.format_selection_frame.show()
                self.advanced_format_selection_checkBox.show()
                self.advanced_format_selection_frame.show()
                self.ok_pushButton.setEnabled(True)
                self.download_later_pushButton.setEnabled(True)

                # if we have no options for separate audio and video, then hide advanced_format_selection...
                if len(self.no_audio_list) == 0 and len(self.no_video_list) == 0:
                    self.advanced_format_selection_checkBox.hide()
                    self.advanced_format_selection_frame.hide()

                # set index of comboboxes on best available quality.
                # we have both audio and video
                if len(self.no_audio_list) != 0 and len(self.no_video_list) != 0:
                    self.media_comboBox.addItem('Best quality')
                    self.media_comboBox.setCurrentIndex(len(self.video_audio_list))
                    self.change_name_lineEdit.setText(self.media_title)
                    self.extension_label.setText('.' + self.no_audio_list[-1]['ext'])
                    self.change_name_checkBox.setChecked(True)

                # video and audio are not separate
                elif len(self.video_audio_list) != 0:
                    self.media_comboBox.setCurrentIndex(len(self.video_audio_list) - 1)

                if len(self.no_audio_list) != 0:
                    self.video_format_selection_comboBox.setCurrentIndex(len(self.no_audio_list))

                if len(self.no_video_list) != 0:
                    self.audio_format_selection_comboBox.setCurrentIndex(len(self.no_video_list))

                # if we have only audio or we have only video then hide media_comboBox
                if len(self.video_audio_list) == 0:
                    self.media_comboBox.hide()
                    self.select_format_label.hide()

                    # only video
                    if len(self.no_video_list) != 0 and len(self.no_audio_list) == 0:
                        self.mediaSelectionChanged('video', int(self.video_format_selection_comboBox.currentIndex()))
                        self.advanced_format_selection_checkBox.setChecked(True)
                        self.advanced_format_selection_checkBox.hide()

                    # only audio
                    elif len(self.no_video_list) == 0 and len(self.no_audio_list) != 0:
                        self.mediaSelectionChanged('audio', int(self.audio_format_selection_comboBox.currentIndex()))
                        self.advanced_format_selection_checkBox.setChecked(True)
                        self.advanced_format_selection_checkBox.hide()

                    # audio and video
                    else:
                        self.mediaSelectionChanged('video_audio', int(self.media_comboBox.currentIndex()))

            except Exception as ex:
                logger.sendToLog(ex, "ERROR")

    def findFileSize(self, result):
        try:
            index = result['index']
            text = result['text']
            if result['file_size'] and result['file_size'] != '0':
                if result['combobox_type'] == 'audio':
                    self.audio_format_selection_comboBox.setItemText(index, '{} - {}'.format(text, result['file_size']))
                elif result['combobox_type'] == 'video':
                    self.video_format_selection_comboBox.setItemText(index, '{} - {}'.format(text, result['file_size']))
                else:
                    self.media_comboBox.setItemText(index, '{} - {}'.format(text, result['file_size']))

        except Exception as ex:
            logger.sendToLog(ex, "ERROR")

    def linkLineChangedHere(self, lineEdit):
        if str(lineEdit) == '':
            self.url_submit_pushButtontton.setEnabled(False)
        else:
            self.url_submit_pushButtontton.setEnabled(True)

    # This method collects additional information like proxy ip, user, password etc.
    def collectMoreOptions(self):
        options = {'ip': None, 'port': None, 'proxy_user': None, 'proxy_passwd': None, 'download_user': None,
                   'download_passwd': None, 'proxy_type': None, 'load_cookies': None}

        if self.proxy_checkBox.isChecked():

            options['ip'] = self.ip_lineEdit.text()
            options['port'] = self.port_spinBox.value()
            options['proxy_user'] = self.proxy_user_lineEdit.text()
            options['proxy_passwd'] = self.proxy_pass_lineEdit.text()

            # http, https or socks5 proxy
            if self.http_radioButton.isChecked() is True:

                options['proxy_type'] = 'http'

            elif self.https_radioButton.isChecked() is True:

                options['proxy_type'] = 'https'

            else:

                options['proxy_type'] = 'socks5'

        if self.download_checkBox.isChecked():

            options['download_user'] = self.download_user_lineEdit.text()
            options['download_passwd'] = self.download_pass_lineEdit.text()

        if self.load_cookies_lineEdit.text() != '':
            options['load_cookies'] = self.load_cookies_lineEdit.text()

        # These info (keys) are required for spider to find file size, because spider() does not check if key exists.
        additional_info = ['header', 'user_agent', 'referer', 'out']
        for i in additional_info:

            if i not in self.plugin_add_link_dictionary.keys():
                options[i] = None

        return options

    # user submitted information by pressing ok_pushButton, so get information
    # from VideoFinderAddLink window and return them to the mainwindow with callback!
    def okButtonPressed(self, download_later, button=None): # noqa

        link_list = []
        # separate audio format and video format is selected.
        if self.advanced_format_selection_checkBox.isChecked():

            if self.video_format_selection_comboBox.currentText() == 'No video' and self.audio_format_selection_comboBox.currentText() != 'No audio':

                # only audio link must be added to the link_list
                audio_link = self.no_video_list[self.audio_format_selection_comboBox.currentIndex() - 1]['url']
                link_list.append(audio_link)

            elif self.video_format_selection_comboBox.currentText() != 'No video' and self.audio_format_selection_comboBox.currentText() == 'No audio':

                # only video link must be added to the link_list
                video_link = self.no_audio_list[self.video_format_selection_comboBox.currentIndex() - 1]['url']
                link_list.append(video_link)

            elif self.video_format_selection_comboBox.currentText() != 'No video' and self.audio_format_selection_comboBox.currentText() != 'No audio':

                # video and audio links must be added to the link_list
                audio_link = self.no_video_list[self.audio_format_selection_comboBox.currentIndex() - 1]['url']
                video_link = self.no_audio_list[self.video_format_selection_comboBox.currentIndex() - 1]['url']
                link_list = [video_link, audio_link]

            elif self.video_format_selection_comboBox.currentText() == 'No video' and self.audio_format_selection_comboBox.currentText() == 'No audio':

                # no video and audio is selected! REALLY?!. user is DRUNK! close the window! :))
                self.close()
        else:
            if self.media_comboBox.currentText() == 'Best quality':

                # the last item in no_video_list and no_audio_list are the best.
                video_link = self.no_audio_list[-1]['url']
                audio_link = self.no_video_list[-1]['url']

                link_list = [video_link, audio_link]

            else:
                audio_and_video_link = self.video_audio_list[self.media_comboBox.currentIndex()]['url']
                link_list.append(audio_and_video_link)

        # write user's new inputs in persepolis_setting for next time :)
        self.persepolis_setting.setValue(
            'add_link_initialization/ip', self.ip_lineEdit.text())
        self.persepolis_setting.setValue(
            'add_link_initialization/port', self.port_spinBox.value())
        self.persepolis_setting.setValue(
            'add_link_initialization/proxy_user', self.proxy_user_lineEdit.text())
        self.persepolis_setting.setValue(
            'add_link_initialization/download_user', self.download_user_lineEdit.text())

        # http, https or socks5 proxy
        if self.http_radioButton.isChecked() is True:

            proxy_type = 'http'
            self.persepolis_setting.setValue(
                'add_link_initialization/proxy_type', 'http')

        elif self.https_radioButton.isChecked() is True:

            proxy_type = 'https'
            self.persepolis_setting.setValue(
                'add_link_initialization/proxy_type', 'https')

        else:

            proxy_type = 'socks5'
            self.persepolis_setting.setValue(
                'add_link_initialization/proxy_type', 'socks5')

        # get proxy information
        if not (self.proxy_checkBox.isChecked()):
            ip = None
            port = None
            proxy_user = None
            proxy_passwd = None
            proxy_type = None
        else:
            ip = self.ip_lineEdit.text()
            if not (ip):
                ip = None
            port = self.port_spinBox.value()
            if not (port):
                port = None
            proxy_user = self.proxy_user_lineEdit.text()
            if not (proxy_user):
                proxy_user = None
            proxy_passwd = self.proxy_pass_lineEdit.text()
            if not (proxy_passwd):
                proxy_passwd = None

        # get download username and password information
        if not (self.download_checkBox.isChecked()):
            download_user = None
            download_passwd = None
        else:
            download_user = self.download_user_lineEdit.text()
            if not (download_user):
                download_user = None
            download_passwd = self.download_pass_lineEdit.text()
            if not (download_passwd):
                download_passwd = None

        # get start time for download if user set that.
        if not (self.start_checkBox.isChecked()):
            start_time = None
        else:
            start_time = self.start_time_qDataTimeEdit.text()

        # get end time for download if user set that.
        if not (self.end_checkBox.isChecked()):
            end_time = None
        else:
            end_time = self.end_time_qDateTimeEdit.text()

        # set name for file(s)
        if self.change_name_checkBox.isChecked():
            name = str(self.change_name_lineEdit.text())
            if name == '':
                name = 'video_finder_file'
        else:
            name = 'video_finder_file'

        # video finder always finds extension
        # but if it can't find file extension
        # use mp4 for extension.
        if str(self.extension_label.text()) == '':
            extension = '.mp4'
        else:
            extension = str(self.extension_label.text())

        # did user select separate audio and video?
        if len(link_list) == 2:
            video_name = name + "_video" + extension
            audio_name = name + "_audio" + '.' + \
                str(self.no_video_list[self.audio_format_selection_comboBox.currentIndex() - 1]['ext'])

            name_list = [video_name, audio_name]

        else:
            name_list = [name + extension]

        # get number of connections
        connections = self.connections_spinBox.value()

        # get download_path
        download_path = self.download_folder_lineEdit.text()

        # referer
        if self.referer_lineEdit.text() != '':
            referer = self.referer_lineEdit.text()
        else:
            referer = None

        # header
        if self.header_lineEdit.text() != '':
            header = self.header_lineEdit.text()
        else:
            header = None

        # user_agent
        if self.user_agent_lineEdit.text() != '':
            user_agent = self.user_agent_lineEdit.text()
        else:
            user_agent = None

        # load_cookies
        if self.load_cookies_lineEdit.text() != '':
            load_cookies = self.load_cookies_lineEdit.text()
        else:
            load_cookies = None

        add_link_dictionary_list = []
        if len(link_list) == 1:
            # save information in a dictionary(add_link_dictionary).
            add_link_dictionary = {'referer': referer, 'header': header, 'user_agent': user_agent, 'load_cookies': load_cookies,
                                   'out': name_list[0], 'start_time': start_time, 'end_time': end_time, 'link': link_list[0], 'ip': ip,
                                   'port': port, 'proxy_user': proxy_user, 'proxy_passwd': proxy_passwd, 'proxy_type': proxy_type,
                                   'download_user': download_user, 'download_passwd': download_passwd,
                                   'connections': connections, 'limit_value': 10, 'download_path': download_path}

            add_link_dictionary_list.append(add_link_dictionary)

        else:
            video_add_link_dictionary = {'referer': referer, 'header': header, 'user_agent': user_agent, 'load_cookies': load_cookies,
                                         'out': name_list[0], 'start_time': start_time, 'end_time': end_time, 'link': link_list[0], 'ip': ip,
                                         'port': port, 'proxy_user': proxy_user, 'proxy_passwd': proxy_passwd, 'proxy_type': proxy_type,
                                         'download_user': download_user, 'download_passwd': download_passwd,
                                         'connections': connections, 'limit_value': 10, 'download_path': download_path}

            audio_add_link_dictionary = {'referer': referer, 'header': header, 'user_agent': user_agent, 'load_cookies': load_cookies,
                                         'out': name_list[1], 'start_time': None, 'end_time': end_time, 'link': link_list[1], 'ip': ip,
                                         'port': port, 'proxy_user': proxy_user, 'proxy_passwd': proxy_passwd, 'proxy_type': proxy_type,
                                         'download_user': download_user, 'download_passwd': download_passwd,
                                         'connections': connections, 'limit_value': 10, 'download_path': download_path}

            add_link_dictionary_list = [video_add_link_dictionary, audio_add_link_dictionary]

        # get category of download
        category = str(self.add_queue_comboBox.currentText())

        del self.plugin_add_link_dictionary

        # return information to mainwindow
        self.callback(add_link_dictionary_list, download_later, category)

        # close window
        self.close()
