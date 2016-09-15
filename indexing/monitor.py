import sys
import glob
import time
import os

import swhlab
import swhlab.core.common as cm #shorthand
from swhlab.indexing import standard
#import swhlab.indexing.indexing
from swhlab.indexing import indexing

def waitTillCopied(fname):
    """
    sometimes a huge file takes several seconds to copy over.
    This will hang until the file is copied (file size is stable).
    """
    lastSize=0
    while True:
        thisSize=os.path.getsize(fname)
        print("size:",thisSize)
        if lastSize==thisSize:
            print("size: STABLE")
            return
        else:
            lastSize=thisSize
        time.sleep(.1)

def handleNewABF(fname):
    """we see a brand new ABF. now what?"""
    waitTillCopied(fname)
    standard.autoABF(fname)

def lazygo(watchFolder='../abfs/',reAnalyze=False,rebuildSite=False,
           keepGoing=True,matching=False):
    """
    continuously monitor a folder for new abfs and try to analyze them.
    This is intended to watch only one folder, but can run multiple copies.
    """
    abfsKnown=[]

    while True:
        print()
        pagesNeeded=[]
        for fname in glob.glob(watchFolder+"/*.abf"):
            ID=os.path.basename(fname).replace(".abf","")
            if not fname in abfsKnown:
                if os.path.exists(fname.replace(".abf",".rsv")): #TODO: or something like this
                    continue
                if matching and not matching in fname:
                    continue
                abfsKnown.append(fname)
                if os.path.exists(os.path.dirname(fname)+"/swhlab4/"+os.path.basename(fname).replace(".abf","_info.pkl")) and reAnalyze==False:
                    print("already analyzed",os.path.basename(fname))
                    if rebuildSite:
                        pagesNeeded.append(ID)
                else:
                    handleNewABF(fname)
                    pagesNeeded.append(ID)
        if len(pagesNeeded):
            print(" -- rebuilding index page")
            indexing.genIndex(os.path.dirname(fname),forceIDs=pagesNeeded)
        if not keepGoing:
            return
        for i in range(50):
            print('.',end='')
            time.sleep(.2)

if __name__=="__main__":
    print(sys.argv)
    lazygo(r'X:\Data\2P01\2016\non-publish\2016-08-22 PIR PN GABA',rebuildSite=True)
    #lazygo(r'C:\Users\swharden\Desktop\green blue\abfs')
    #lazygo(r'X:\Data\2P01\2016\2016-07-11 PIR TR IHC',keepGoing=False)
    #lazygo(r'X:\Data\2P01\2016\2016-07-11 PIR TR IHC',keepGoing=False,reAnalyze=True,matching="16711054")

    print("DONE")