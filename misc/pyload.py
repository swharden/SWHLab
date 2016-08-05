"""
This script loads everything we need to run custom modules in origin.
    * reads path variables from ~/Documents/OriginLab/pythonModules.txt
        * should add a full version-matched winpython
        * should add a path for custom modules

This is designed to be called once when origin loads.
If you call it a second time, the swhlab modile is reloaded.
    * this is required to incorporate new changes to the .py files
    * note that an origin restart is NEVER required
"""

import time
import os
import webbrowser
import platform
import sys
import traceback
import imp

if 'swhlab' in globals().keys():
    print(" -- RELOADING SWHLab...")
    imp.reload(swhlab)

pyModulesFile=os.environ['USERPROFILE']+"/Documents/OriginLab/pythonModules.txt"
pyModulesFile=os.path.abspath(pyModulesFile) #backslash / forwardslash conversion
blankFile=r"""###### STEP 1 #####
# give me the path to the "site-packages" folder of a WinPython distro (must be version %s!)
C:\Users\swharden\Documents\important\WinPython-64bit-3.3.5.0\python-3.3.5.amd64\Lib\site-packages

###### STEP 2 #####
# Copy the following folder somewhere locally (outside a python distro)
# X:\Software\OriginC\On-line\python\pythonModules <-- don't uncomment this line!

###### STEP 3 #####
# tell us where you put that folder. (these custom modules will always be imported)
C:\Users\swharden\Documents\important\pythonModules

# Make a mistake? Get a fresh start by deleting this file.
"""%platform.python_version()

def pathMagic():
    """read pythonModules.txt (in origin user documents) and set paths."""
    with open(pyModulesFile) as f:
        raw=f.readlines()
    for line in raw:
        line=line.strip()
        if line.startswith("#"):
            continue
        if len(line)<3:
            continue
        if os.path.exists(line):
            print(" -- adding system path to: .../%s/"%os.path.basename(line))
            sys.path.append(line)

if not os.path.exists(pyModulesFile):
    with open(pyModulesFile,'w') as f:
        f.write(blankFile)
    webbrowser.open(pyModulesFile)
pathMagic() #now we assume the file is set up, so use it to do imports

t=time.time()
try:
    import numpy
    msg=" -- module import paths look good"
except:
    msg="""
    I don't know where to import custom modules from.
    Follow the instructions in the file below and try again!
    %s
    """%pyModulesFile
print(msg)

### ADD OTHER MODULES HERE ###
# I recommend NOT doing this. If a script you wrote needs a module,
# write the appropriate import statement at the top of tha script.
# if you have a set of modules you use a lot, make your own "init.py" script.
# don't make every orign user load modules into memory they won't use.

#from neo import io
#import numpy as np
#import pyqtgraph as pg
#from PySide import QtGui, QtCore
#import matplotlib.pyplot as mp

### try SWHLab last because it crashes a lot :( ###
try:
    print(" -- importing SWHlab and all dependencies...")
    import swhlab
    print(" -- all imports took %.02f ms"%((time.time()-t)*1000))
    print(" -- SWHLab loaded and ready to use!")
    print("      type 'sc help' to get started...")
except:
    print(" -- SWHLlab crashed on import.\n\n")
    print(print(traceback.format_exc()))