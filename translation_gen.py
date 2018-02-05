#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import subprocess
import sys
from shutil import copyfile

HERE = os.path.dirname(os.path.realpath(__file__))
translation_files = os.path.join(HERE, 'translation_files.pro')

def function(locale):
    if not os.path.exists(os.path.join(HERE + '/icons/locales')):
        os.makedirs(os.path.join(HERE + '/icons/locales'))

    subprocess.call(['pylupdate5', '-noobsolete','-tr-function', 'ui_tr', translation_files])
function("locale")
