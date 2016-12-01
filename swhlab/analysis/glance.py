"""Methods to generate a SINGLE image to represent any ABF.
There are several categories which are grossly analyzed.

gain function:
    * current clamp recording where command traces differ by sweep.
    * must also have something that looks like an action potential
    * will be analyzed with AP detection information

voltage clamp I/V:
    * voltage clamp recording where command traces differ by sweep.
    * image will simply be an overlay

drug experiment:
    * voltage clamp or current clamp where every command is the same
    * tags will be reported over a chronological graph
"""

import sys
import os
import glob

sys.path.insert(0,'../../')
import swhlab

def processFolder(abfFolder):
    for fname in glob.glob(abfFolder+"/*.abf"):
        print(fname)
    return

def processAbf(abfFname):
    abf=swhlab.ABF(abfFname)

    return

if __name__=="__main__":
    abfFile=r"C:\Users\swharden\Desktop\2016-07-03\16703000.abf"
    abfFolder=os.path.basename(abfFile)
    #processFolder(abfFolder)
    processAbf(abfFile)