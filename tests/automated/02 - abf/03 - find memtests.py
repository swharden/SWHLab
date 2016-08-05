"""
show the ABF of the most recent memtest of each cell
"""

import swhlab.core.common as cm
import glob
import os

ABFPATH=r'C:\Apps\pythonModules\abfs'
groups=cm.getABFgroups(glob.glob(ABFPATH+"/*.*"))
for i,cellname in enumerate(sorted(groups.keys())):
    memtestFname=None
    for abfID in sorted(groups[cellname]):
        memtestFname=os.path.join(ABFPATH,abfID+".abf")
    print(cellname, memtestFname)