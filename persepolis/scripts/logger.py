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

from persepolis.scripts.useful_tools import determineConfigFolder
from persepolis.scripts import osCommands
import logging
import os

# config_folder
config_folder =  determineConfigFolder()

# log file address
log_file = os.path.join(str(config_folder), 'persepolisdm.log')
if not(os.path.isfile(log_file)):
    osCommands.touch(log_file)

# define logging object
logObj = logging.getLogger("Persepolis")
logObj.setLevel(logging.INFO)

# create a file handler
handler = logging.FileHandler(log_file)
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logObj.addHandler(handler)



def sendToLog(text="", type="INFO"):
    if type == "INFO":
        logObj.info(text)
    elif type == "ERROR":
        logObj.error(text)
    else:
        logObj.warning(text)
