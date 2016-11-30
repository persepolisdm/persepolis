#!/usr/bin/env python3
	
import sys, os, os.path, stat
pythonpath,top = os.path.split(os.path.realpath(sys.executable))
while top:
    if 'Resources' in pythonpath:
        pass
    elif os.path.exists(os.path.join(pythonpath,'Resources')):
        break
    pythonpath,top = os.path.split(pythonpath)
else:
    print("\nSorry, failed to find a Resources directory associated with "+str(sys.executable))
    sys.exit()
pythonapp = os.path.join(pythonpath,'Resources','Python.app','Contents','MacOS','Python')
if not os.path.exists(pythonapp): 
    print("\nSorry, failed to find a Python app in "+str(pythonapp))
    sys.exit()

print(pythonapp)
