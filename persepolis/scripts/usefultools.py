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


# converting file_size to KiB or MiB or GiB
def hr_size(size):# human readable size 
    labels = ['KiB', 'MiB', 'Gib', 'TiB']
    i = -1
    if size < 1024:
        return str(size) + ' B'

    while size >= 1024:
        i += 1
        size = size / 1024

    p = 2 if i == 2 else None
    return str(round(size, p)) +' '+ labels[i]
   

