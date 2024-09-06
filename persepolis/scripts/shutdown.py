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

from __future__ import annotations

import platform
import subprocess
from time import sleep
from typing import TYPE_CHECKING

from persepolis.constants import Os
from persepolis.scripts import logger

if TYPE_CHECKING:
    try:
        from PySide6.QtWidgets import QWidget
    except ImportError:
        from PyQt5.QtWidgets import QWidget

os_type = platform.system()


def shutDown(parent: QWidget, gid: str | None = None, category: str | None = None, password: str | None = None) -> None:
    # for queue >> gid = None
    # for single downloads >> category = None
    # change value of shutdown in data base
    if category is not None:
        shutdown_dict = {'category': category, 'shutdown': 'wait'}

        # update data base
        parent.temp_db.updateQueueTable(shutdown_dict)
    else:
        # so we have single download
        shutdown_dict = {'gid': gid, 'shutdown': 'wait'}

        # update data base
        parent.temp_db.updateSingleTable(shutdown_dict)

    shutdown_status = 'wait'

    while shutdown_status == 'wait':
        sleep(5)

        # get shutdown status from data_base
        if category is not None:
            shutdown_dict = parent.temp_db.returnCategory(category)
        else:
            shutdown_dict = parent.temp_db.returnGid(gid)

        shutdown_status = shutdown_dict['shutdown']

    if shutdown_status == 'shutdown':
        logger.sendToLog('Shutting down in 20 seconds', 'INFO')
        sleep(20)

        if os_type == Os.LINUX:
            pipe = subprocess.Popen(
                ['sudo', '-S', 'poweroff'],
                stdout=subprocess.DEVNULL,
                stdin=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                shell=False,
            )

            pipe.communicate(password.encode())

        elif os_type == Os.DARWIN:
            pipe = subprocess.Popen(
                ['sudo', '-S', 'shutdown', '-h', 'now'],
                stdout=subprocess.DEVNULL,
                stdin=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                shell=False,
            )

            pipe.communicate(password.encode())

        elif os_type == Os.WINDOWS:
            CREATE_NO_WINDOW = 0x08000000
            subprocess.Popen(
                ['shutdown', '-S'],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=False,
                creationflags=CREATE_NO_WINDOW,
            )

        elif os_type in Os.BSD_FAMILY:
            pipe = subprocess.Popen(
                ['sudo', '-S', 'shutdown', '-p', 'now'],
                stdout=subprocess.DEVNULL,
                stdin=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                shell=False,
            )

            pipe.communicate(password.encode())
