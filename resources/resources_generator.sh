#!/bin/bash

while getopts "trqh" arg;do
    case $arg in
        t)
            translate="1";;
        r)
            resources="1";;
        q)
            create_qm_files="1";;
        *)
            echo "-t updates ui.ts file."
            echo "-r updates resources.py file."
            echo "-q create qm files from ts files."
    esac
done

# finding parent directory
dir=`pwd`
parent_dir=`dirname $dir`


if [ "$translate" == "1" ];then

    # generate ui.ts file 
    pylupdate5 -translate-function ui_tr "$dir/translation_files.pro"
    echo "$dir/locales/ui.ts is generated!"
fi

if [ "$resources" == "1" ];then

    # generate resource.py file
    # for pyqt5
#     pyrcc5 resources.qrc -o "$parent_dir/persepolis/gui/resources.py"

    # for pysside2
#     rcc -g python -o "$parent_dir/persepolis/gui/resources.py" resources.qrc

    pyside6-rcc resources.qrc -o "$parent_dir/persepolis/gui/resources.py"

     
    #add some line to file
    sed -i '/PySide6/d' "$parent_dir/persepolis/gui/resources.py"
    sed -i '6i try:' "$parent_dir/persepolis/gui/resources.py"
    sed -i '7i\    from PySide6 import QtCore' "$parent_dir/persepolis/gui/resources.py"
    sed -i '8i except:' "$parent_dir/persepolis/gui/resources.py"
    sed -i '9i\    from PyQt5 import QtCore' "$parent_dir/persepolis/gui/resources.py"
#     sed -i '11i try:' "$parent_dir/persepolis/gui/resources.py"
#     sed -i '12i\    import lzma' "$parent_dir/persepolis/gui/resources.py"
#     sed -i '13i except:' "$parent_dir/persepolis/gui/resources.py"
#     sed -i '14i\    print(\"lzma\ is\ not\ installed!\")' "$parent_dir/persepolis/gui/resources.py"
# 
    echo  "$parent_dir/persepolis/gui/resource.py is generated!"

fi

if [ "$create_qm_files" == "1" ];then

    for file in $dir/locales/* ;do
        # generate qm files from ts files
        lrelease "$file"
    done
fi
