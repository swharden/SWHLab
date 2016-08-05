"""
generate the labtalk needed to run "memtest" for every cell.
  - cells are defined as image matches
  - if multiple memtests exist, only the most recent one is used
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
    if memtestFname: # won't run if it didn't find one
        cmd='setpath "%s"; memtest; '%(memtestFname)
        cmd+='callit %s;'%abfID
        print(cmd)