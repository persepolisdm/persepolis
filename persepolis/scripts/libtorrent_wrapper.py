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
import libtorrent
from persepolis.scripts.useful_tools import readCookieJar
from persepolis.scripts.osCommands import makeDirs


class Torrent_Download():
    def __init__(self, add_link_dictionary, main_window, gid):
        self.add_link_dictionary = add_link_dictionary
        self.main_window = main_window
        self.gid = gid
        self.link = add_link_dictionary['link']
        self.name = add_link_dictionary['out']
        self.download_path = add_link_dictionary['download_path']
        self.ip = add_link_dictionary['ip']
        self.port = add_link_dictionary['port']
        self.proxy_user = add_link_dictionary['proxy_user']
        self.proxy_passwd = add_link_dictionary['proxy_passwd']
        self.proxy_type = add_link_dictionary['proxy_type']
        self.download_user = add_link_dictionary['download_user']
        self.download_passwd = add_link_dictionary['download_passwd']
        self.header = add_link_dictionary['header']
        self.user_agent = add_link_dictionary['user_agent']
        self.load_cookies = add_link_dictionary['load_cookies']
        self.referer = add_link_dictionary['referer']
        self.start_time = add_link_dictionary['start_time']
        self.end_time = add_link_dictionary['end_time']

    def createSession(self):
        self.libtorrent_session = libtorrent.session()
        self.libtorrent_session.listen_on(6881, 6891)
        self.libtorrent_session_parameters = {}

        # check if user set proxy
        if self.ip:

            if self.proxy_type == 'socks5':
                proxy_type = libtorrent.proxy_type_t.socks5
            elif self.proxy_type == 'http':
                proxy_type = libtorrent.proxy_type_t.http

            # set proxy to the session
            self.libtorrent_session.set_proxy(proxy_type, self.ip, self.port, self.proxy_user, self.proxy_passwd)

        # set user_agent
        if self.user_agent:
            # setting user_agent to the session
            self.libtorrent_session_parameters['user_agent'] = self.user_agent

        # set cookies
        if self.load_cookies:
            jar = readCookieJar(self.load_cookies)
            if jar:
                self.libtorrent_session_parameters['cookies'] = jar

        # Create download_path if not existed
        makeDirs(self.download_path)

        self.libtorrent_session_parameters['save_path'] = self.download_path

        # set storage mode
        self.libtorrent_session_parameters['storage_mode'] = libtorrent.storage_mode_full
