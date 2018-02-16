#!/bin/bash
# finding parent directory
dir=`pwd`
parent_dir=`dirname $dir`

# this line generates ui.ts file 
pylupdate5 -translate-function ui_tr "$dir/translation_files.pro"
echo "$dir/locales/ui.ts is generated!"

# this line generates icons_resource.py file
pyrcc5 resources.qrc -o "$parent_dir/persepolis/gui/resources.py"

echo  "$parent_dir/persepolis/gui/resource.py is generated!"

