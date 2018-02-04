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

    copyfile('./translation_files.pro.orig', './translation_files.pro')

    with open('./translation_files.pro.orig', 'rt') as src:
        with open('./translation_files.pro', 'wt') as copy:
            for line in src:
                copy.write(line.replace('LOCALE', locale))

    subprocess.call(['pylupdate5', '-noobsolete','-tr-function', 'ui_tr', translation_files])
function(sys.argv[1])
