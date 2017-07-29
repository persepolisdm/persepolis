#!/bin/bash
#finding parent directory
dir=`pwd`
parent_dir=`dirname $dir`

#this line is generating icons_resource.py file
pyrcc5 locale_resources.qrc -o "$parent_dir/persepolis/gui/locale_resources.py"

echo  "$parent_dir/persepolis/gui/locale_resources.py is generated!"

