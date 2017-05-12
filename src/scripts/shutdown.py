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
import os
from newopen import Open
from time import sleep
import osCommands
import logger
import platform
import subprocess

home_address = os.path.expanduser("~")

# finding os platform
os_type = platform.system()


# persepolis tmp folder in /tmp
if os_type != 'Windows':
    user_name_split = home_address.split('/')
    user_name = user_name_split[2]
    persepolis_tmp = '/tmp/persepolis_' + user_name
else:
    persepolis_tmp = os.path.join(
        str(home_address), 'AppData', 'Local', 'persepolis_tmp')


def shutDown(gid, password=None):
    shutdown_notification_file = os.path.join(persepolis_tmp, 'shutdown', gid)
    f = Open(shutdown_notification_file, 'w')
    f.writelines('wait')
    f.close()

    shutdown_notification = "wait"

    while shutdown_notification == "wait":
        sleep(1)

        f = Open(shutdown_notification_file, 'r')
        shutdown_notification_file_lines = f.readlines()
        f.close()

        shutdown_notification = str(
            shutdown_notification_file_lines[0].strip())

    osCommands.remove(shutdown_notification_file)

    if shutdown_notification == "shutdown":

        print("shutdown in 20 seconds")
        logger.sendToLog("Shutting down in 20 seconds", "INFO")
        sleep(20)
        if os_type == 'Linux':
            os.system('echo "' + password + '" |sudo -S poweroff')

        elif os_type == 'Darwin':
            os.system('echo "' + password + '" |sudo -S shutdown -h now ')

        elif os_type == 'Windows':
            CREATE_NO_WINDOW = 0x08000000
            subprocess.Popen(['shutdown', '-S'], shell=False,
                             creationflags=CREATE_NO_WINDOW)

        elif os_type == 'FreeBSD' or os_type == 'OpenBSD':
            os.system('echo "' + password + '" |sudo -S shutdown -p now ')
