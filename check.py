#!/usr/bin/env python3
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
import sys
import importlib
import subprocess
class Check:

    def check_PyQt(self):
        """ Check if PyQt5 is installed """
        try:
            import PyQt5
            return True

        except:
            return False

    def check_requests(self):
        """ checks if requests is installed """

        try:
            import requests
            return True

        except ImportError:
            return False
