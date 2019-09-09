#!/bin/bash

while getopts "trh" arg;do
    case $arg in
        t)
            translate="1";;
        r)
            resources="1";;
        *)
            echo "-t updates ui.ts file."
            echo "-r updates resources.py file."
    esac
done

# finding parent directory
dir=`pwd`
parent_dir=`dirname $dir`


if [ "$translate" == "1" ];then

    # this line generates ui.ts file 
    pylupdate5 -translate-function ui_tr "$dir/translation_files.pro"
    echo "$dir/locales/ui.ts is generated!"
fi

if [ "$resources" == "1" ];then

    # this line generates resource.py file
    pyrcc5 resources.qrc -o "$parent_dir/persepolis/gui/resources.py"

    echo  "$parent_dir/persepolis/gui/resource.py is generated!"
fi

