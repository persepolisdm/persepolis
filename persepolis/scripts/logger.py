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
from persepolis.scripts.osCommands import touch
import logging
import os


def setUpLogger(logger_name, log_file, level):
    # define logging object
    logObj = logging.getLogger(logger_name)
    logObj.setLevel(level)

    # don't show log in console
    logObj.propagate = False

    # create a file handler
    handler = logging.FileHandler(log_file)
    handler.setLevel(logging.INFO)
    # create a logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # add the handlers to the logger
    logObj.addHandler(handler)

    return logObj


# config_folder
config_folder = determineConfigFolder()

# create a directory if it does not exist
if not os.path.exists(config_folder):
    os.makedirs(config_folder)

# log files address
initialization_log_file = os.path.join(str(config_folder), 'initialization_log_file.log')
downloads_log_file = os.path.join(str(config_folder), 'downloads_log_file.log')
errors_log_file = os.path.join(str(config_folder), 'errors_log_file.log')

for file in [initialization_log_file, downloads_log_file, errors_log_file]:
    if not os.path.isfile(file):
        touch(file)

initialization_logger = setUpLogger('initialization', initialization_log_file, logging.INFO)
downloads_logger = setUpLogger('downloads', downloads_log_file, logging.INFO)
errors_logger = setUpLogger('errors', errors_log_file, logging.ERROR)


def sendToLog(text="", type="INFO"):
    if type == "INITIALIZATION":
        initialization_logger.info(text)
    elif type == "ERROR":
        errors_logger.error(text)
    elif type == 'DOWNLOADS':
        downloads_logger.info(text)
    elif type == 'DOWNLOAD ERROR':
        downloads_logger.error(text)
        errors_logger.error(text)
    else:
        initialization_logger.info(text)
