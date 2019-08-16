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

from persepolis.scripts import logger
from time import sleep
import subprocess
import platform

# find os platform
os_type = platform.system()


def shutDown(parent, gid=None, category=None, password=None):
    # for queue >> gid = None
    # for single downloads >> category = None
    # change value of shutdown in data base
    if category != None:
        dict = {'category': category,
                'shutdown': 'wait'}

        # update data base
        parent.temp_db.updateQueueTable(dict)
    else:
        # so we have single download
        dict = {'gid': gid,
                'shutdown': 'wait'}

        # update data base
        parent.temp_db.updateSingleTable(dict)

    shutdown_status = "wait"

    while shutdown_status == "wait":
        sleep(5)

        # get shutdown status from data_base
        if category != None:
            dict = parent.temp_db.returnCategory(category)
        else:
            dict = parent.temp_db.returnGid(gid)

        shutdown_status = dict['shutdown']

    if shutdown_status == "shutdown":

        logger.sendToLog("Shutting down in 20 seconds", "INFO")
        sleep(20)

        if os_type == 'Linux':

            pipe = subprocess.Popen(['sudo', '-S', 'poweroff'],
                                    stdout=subprocess.DEVNULL,
                                    stdin=subprocess.PIPE,
                                    stderr=subprocess.DEVNULL,
                                    shell=False)

            pipe.communicate(password.encode())

        elif os_type == 'Darwin':

            pipe = subprocess.Popen(['sudo', '-S', 'shutdown', '-h', 'now'],
                                    stdout=subprocess.DEVNULL,
                                    stdin=subprocess.PIPE,
                                    stderr=subprocess.DEVNULL,
                                    shell=False)

            pipe.communicate(password.encode())

        elif os_type == 'Windows':

            CREATE_NO_WINDOW = 0x08000000
            subprocess.Popen(['shutdown', '-S'],
                             stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stdin=subprocess.PIPE,
                             shell=False,
                             creationflags=CREATE_NO_WINDOW)

        elif os_type == 'FreeBSD' or os_type == 'OpenBSD':

            pipe = subprocess.Popen(['sudo', '-S', 'shutdown', '-p', 'now'],
                                    stdout=subprocess.DEVNULL,
                                    stdin=subprocess.PIPE,
                                    stderr=subprocess.DEVNULL,
                                    shell=False)

            pipe.communicate(password.encode())
