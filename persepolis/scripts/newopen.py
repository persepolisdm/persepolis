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

from persepolis.scripts import osCommands
import shutil
import ast


# This function is writting a list in file_path in dictionary format
def writeList(file_path, list):
    dictionary = {'list': list}
    f = open(file_path, 'w')
    f.writelines(str(dictionary))
    f.close()

# This function is reading file_path and return content of file in list format


def readList(file_path, mode='dictionary'):
    f = open(file_path, 'r')
    f_string = f.readline()
    f.close()
    dictionary = ast.literal_eval(f_string.strip())
    list = dictionary['list']

    if mode == 'string':
        list[9] = str(list[9])

    return list

# this function is reading a file that contains dictionary , and extracts
# dictionary from it.


def readDict(file_path):
    f = open(file_path)
    f_lines = f.readlines()
    f.close()
    dict_str = str(f_lines[0].strip())
    return_dict = ast.literal_eval(dict_str)
    return return_dict
