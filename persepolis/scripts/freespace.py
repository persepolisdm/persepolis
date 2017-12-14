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


from persepolis.scripts import logger


def freeSpace(dir):
    try:
        import psutil
    except:
        logger.sendToLog("psutil in not installed!", "ERROR")

        return None

    try:
        dir_space = psutil.disk_usage(dir)
        free_space = dir_space.free
        return int(free_space)

    except Exception as e:
        # log in to the log file
        logger.sendToLog("persepolis couldn't find free space value:\n" + str(e), "ERROR")

        return None


