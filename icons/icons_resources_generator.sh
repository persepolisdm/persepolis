#!/bin/bash
#finding parent directory
dir=`pwd`
parent_dir=`dirname $dir`

#this line is generating icons_resource.py file
pyrcc5 icons_resource.qrc -o "$parent_dir/persepolis/gui/icons_resource.py"

echo  "$parent_dir/persepolis/gui/icons_resource.py is generated!"

