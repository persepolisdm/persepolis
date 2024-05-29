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
#

# aria2c wouldn't support socks5. so persepolis use gost for solving this issue.
# gost act as intermediary between socks5 and http.
# SocksToHttpConvertor is a class that manage gost in persepolis.

from persepolis.scripts.useful_tools import runApplication, findExternalAppPath
from persepolis.scripts import logger
from socket import socket


class Socks5ToHttpConvertor():
    def __init__(self, socks5_host, socks5_port, socks5_username, socks5_password, main_window, parent):
        self.socks5_host = socks5_host
        self.socks5_port = socks5_port
        self.socks5_username = socks5_username
        self.socks5_password = socks5_password
        self.main_window = main_window
        self.parent = parent

        # get random free port on localhost
        self.http_host = '127.0.0.1'
        sock = socket()
        sock.bind(('', 0))
        self.http_port = sock.getsockname()[1]
        self.process = None

        logger.sendToLog("{} runs http server:\n\t\thttp://127.0.0.1:{}".format(str(self.main_window.type_of_convertor), str(self.http_port)))

        self.pipe_is_running = False

    def isRunning(self):
        # check process is running or not
        if self.process:
            if self.process.poll() is None:
                self.pipe_is_running = True
            else:
                self.pipe_is_running = False
        else:
            self.pipe_is_running = False

        #     if self.process.ProcessState != QProcess.NotRunning:
        #         self.pipe_is_running = True
        #     else:
        #         self.pipe_is_running = False
        # else:
        #     self.pipe_is_running = False

        return self.pipe_is_running

    def stop(self):
        # kill process
        try:
            self.process.kill()
            self.process.communicate()
            self.pipe_is_running = False
        except:
            self.pipe_is_running = False

    def run(self):
        if not (self.pipe_is_running):
            # find type of convertor
            if self.main_window.type_of_convertor:

                # find convertor path
                convertor_app_path, log_list = findExternalAppPath(self.main_window.type_of_convertor)

                # run convertor
                http_argument = 'http://' + str(self.http_host) + ':' + str(self.http_port)

                if self.socks5_username:

                    socks5_argument = 'socks5://' + str(self.socks5_username) + ':' + str(self.socks5_password) + '@' + str(self.socks5_host) + ':' + str(self.socks5_port)

                else:

                    socks5_argument = 'socks5://' + str(self.socks5_host) + ':' + str(self.socks5_port)

                # gost
                if self.main_window.type_of_convertor == 'gost':

                    command_argument = [convertor_app_path, '-L', http_argument,
                                        '-F', socks5_argument]
                # pproxy
                elif self.main_window.type_of_convertor == 'pproxy':

                    command_argument = [convertor_app_path, '-l', http_argument,
                                        '-r', socks5_argument]
                # sthp
                else:

                    if self.socks5_username:
                        command_argument = [convertor_app_path, '--listen-ip', str(self.http_host),
                                            '--port', str(self.http_port),
                                            '--socks-address', '{}:{}'.format(self.socks5_host, self.socks5_port),
                                            '--username', self.socks5_username,
                                            '--password', self.socks5_password]

                    else:
                        command_argument = [convertor_app_path, '--listen-ip', str(self.http_host),
                                            '--port', str(self.http_port),
                                            '--socks-address', '{}:{}'.format(self.socks5_host, self.socks5_port)]

                self.pipe_is_running = True
                self.process = runApplication(command_argument)
                # self.process = QProcess()
                # self.process.start(convertor_app_path, command_argument)
