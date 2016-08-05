"""
Show how to organize a folder of ABFs into ABFs per cell.
ABFs belonging to a cell are defined as those coming after a perfectly
matching image file name (.TIF) and ABF file.
"""
import swhlab
import swhlab.core.common as cm
import glob
import os

ABFPATH=r'C:\Apps\pythonModules\abfs'
files=glob.glob(ABFPATH+"/*.*")
print("found %d files (ABFs, TIFs, etc)"%len(files))
groups=cm.getABFgroups(files)
print("found %d groups (cells)"%len(groups))
#for cellname in sorted(groups.keys()):
for i,cellname in enumerate(sorted(groups.keys())):
    print("\ncell %s has %d ABFs:"%(cellname,len(groups[cellname])))
    for abfID in groups[cellname]:
        fname=os.path.join(ABFPATH,abfID+".abf")
        print("  %s.abf (protocol %s)"%(abfID,cm.determineProtocol(fname)))
    if i>10:
        break #just do this a few times