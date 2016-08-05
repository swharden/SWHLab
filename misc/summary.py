"""operations related to comparing data from one cell to another.

A collection of ABFs is defined as belingong to a single cell if an ABF
in the folder matches the file name (EXACTLY) as a .TIF file in the same
folder. That ABF and every ABF after that point is considered to belong
to the same cell. If a new ABF/TIF pair is found, it starts a new cell.
"""

import os
import glob
import swhlab.core.common as cm
import pylab

ABF_FOLDER=r"C:\Users\swharden\Desktop\green blue\abfs"
ABF_FILES,SWH_FILES,ABF_GROUPS=cm.scanABFfolder(ABF_FOLDER)

def findFirst(abfParent,matching,firstOne=False):
    """Given an ABF ID, scan its children and returns the first protocol
    whose description matches.  If firstOne is False, return the last."""
    children=ABF_GROUPS[abfParent]
    matchFile = None
    for ID in children:
        info=os.path.join("%s/swhlab4/%s_info.pkl"%(ABF_FOLDER,ID))
        protocol = cm.pickle_load(info)["protoComment"]
        if matching in protocol:
            matchFile=os.path.abspath("%s/%s.abf"%(ABF_FOLDER,ID))
            if firstOne:
                return matchFile
    return matchFile

def getGainPoints(fname,startWithDict={}):
    print()
    if fname is None:
        return startWithDict
    baseName,fname=os.path.split(fname)
    fname=baseName+"/swhlab4/"+fname.replace(".abf","_SAP.pkl")
    thing=cm.pickle_load(fname)
    Xs=cm.matrixValues(thing,"commandI")
    Ys=cm.matrixValues(thing,"freqSteady25")
    #Ys=cm.matrixValues(thing,"freqAvg")
    for i,X in enumerate(Xs):
        startWithDict[X]=Ys[i]
    return startWithDict

def plotGainDict(d,color='b',label=None):
    Xs,Ys=[],[]
    for i,X in enumerate(sorted(d.keys())):
        if X>0 and d[X]==0:
            continue # skip AP block
        Xs.append(X)
        Ys.append(d[X])
    pylab.plot(Xs,Ys,'.-',color=color,alpha=.5,label=label,ms=2)

if __name__=="__main__":
    print("DONT RUN THIS DIRECTLY.")

    #print(getGainPoints(r'C:\Users\swharden\Desktop\green blue\abfs\16718037.abf'))

    groups=cm.groupsFromKey(r"C:\Users\swharden\Desktop\green blue\key.txt")
    colors=['g','b','r','y'] #more than we need
    for i,groupName in enumerate(sorted(groups.keys())):
        color=colors[i]
        label=groupName
        for abfID in groups[groupName]:
            d={}
            d=getGainPoints(findFirst(abfID,"steps100"),startWithDict=d)
            d=getGainPoints(findFirst(abfID,"steps025"),startWithDict=d)
            plotGainDict(d,color,label)
            label=None
    pylab.legend(loc='upper left')
    pylab.grid(alpha=.5)
    pylab.xlabel("current applied (pA)")
    pylab.ylabel("average frequency (Hz)")
    pylab.savefig(r"C:\Users\swharden\Documents\temp\test3.png",dpi=300)




