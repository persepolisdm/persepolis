#!/usr/bin/env python

import sys
import os

# direct call of __main__.py
import os.path

cwd = os.path.abspath(__file__)
persepolis_path = os.path.dirname(cwd)
# if persepolis run in test folder
scripts_path = os.path.join(persepolis_path, 'scripts')
gui_path = os.path.join(persepolis_path, 'gui')
for path in [persepolis_path, scripts_path, gui_path]:
    sys.path.insert(0, path)


from persepolis.scripts import persepolis

persepolis.main()
