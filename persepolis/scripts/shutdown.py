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
from persepolis.constants import OS
from time import sleep
import subprocess
import platform

os_type = platform.system()


def shutDown(parent, gid=None, category=None, password=None):
    # for queue >> gid = None
    # for single downloads >> category = None
    # change value of shutdown in data base
    if category is not None:
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
        if category is not None:
            dict = parent.temp_db.returnCategory(category)
        else:
            dict = parent.temp_db.returnGid(gid)

        shutdown_status = dict['shutdown']

    if shutdown_status == "shutdown":

        logger.sendToLog("Shutting down in a minute", "INFO")
        # Make sure all download progresses are stopped.
        parent.stopAllDownloads()

        sleep(20)

        # Make sure all sessions have ended.
        while parent.download_sessions_list:
            sleep(0.5)

        # shutdown_notification = 0 >> persepolis running , 1 >> persepolis is
        # ready for close(closeEvent called) , 2 >> OK, let's close application!
        parent.changeShutdownValue(1)
        while parent.returnShutDownValue() != 2:
            sleep(0.1)

        # close data bases connections
        for db in parent.persepolis_db, parent.plugins_db, parent.temp_db:
            db.closeConnections()

        for i in parent.threadPool:
            i.quit()
            i.wait()

        parent.cleanTempFolder()

        if os_type == OS.LINUX:

            pipe = subprocess.Popen(['sudo', '-S', 'poweroff'],
                                    stdout=subprocess.DEVNULL,
                                    stdin=subprocess.PIPE,
                                    stderr=subprocess.DEVNULL,
                                    shell=False)

            pipe.communicate(password.encode())

        elif os_type == OS.DARWIN:

            pipe = subprocess.Popen(['sudo', '-S', 'shutdown', '-h', 'now'],
                                    stdout=subprocess.DEVNULL,
                                    stdin=subprocess.PIPE,
                                    stderr=subprocess.DEVNULL,
                                    shell=False)

            pipe.communicate(password.encode())

        elif os_type == OS.WINDOWS:

            CREATE_NO_WINDOW = 0x08000000
            subprocess.Popen(['shutdown', '-S'],
                             stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stdin=subprocess.PIPE,
                             shell=False,
                             creationflags=CREATE_NO_WINDOW)

        elif os_type in OS.BSD_FAMILY:

            pipe = subprocess.Popen(['sudo', '-S', 'shutdown', '-p', 'now'],
                                    stdout=subprocess.DEVNULL,
                                    stdin=subprocess.PIPE,
                                    stderr=subprocess.DEVNULL,
                                    shell=False)

            pipe.communicate(password.encode())
