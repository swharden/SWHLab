# -*- coding: utf-8 -*-

import numpy as np
import time
import datetime
import os

### numpy

def where_cross(data,threshold):
    """return a list of Is where the data first crosses above threshold."""
    Is=np.where(data>threshold)[0]
    Is=np.concatenate(([0],Is))
    Ds=Is[:-1]-Is[1:]+1
    return Is[np.where(Ds)[0]+1]

### system operations

def timeit(timer=None):
    """simple timer. returns a time object, or a string."""
    if timer is None:
        return time.time()
    else:
        took=time.time()-timer
        if took<1:
            return "%.02f ms"%(took*1000.0)
        elif took<60:
            return "%.02f s"%(took)
        else:
            return "%.02f min"%(took/60.0)
            
### dates and times

def epochToDatetime(epoch=time.time()):
    return datetime.datetime.fromtimestamp(epoch)

def datetimeToString(dt=None):
    if not dt:
        dt=datetime.datetime.now()
    return dt.strftime('%Y-%m-%d %H:%M:%S') #standard for all SWHLAB

def epochToString(epoch):
    return datetimeToString(epochToDatetime())

### list manipulations

def list_to_lowercase(l):
    """given a list of strings, make them all lowercase."""
    return [x.lower() for x in l if type(x) is str]
    
### abf organization

def ext(fname):
    """return the extension of a filename."""
    if "." in fname:
        return os.path.splitext(fname)[1]
    return fname

#def abf2ID(s):
#    """given a string (filename, path, whatever) return the ABF ID."""
#    s=s.replace("\\","/")
#    if "/" in s:
#        s=os.path.basename(s)
#    if "." in s:
#        s=s.split(".")[0]
#    return s

def abfSort(IDs):
    """
    given a list of goofy ABF names, return it sorted intelligently.
    This places things like 16o01001 after 16901001.
    """
    IDs=list(IDs)
    monO=[]
    monN=[]
    monD=[]
    good=[]
    for ID in IDs:
        if ID is None:
            continue
        if 'o' in ID:
            monO.append(ID)
        elif 'n' in ID:
            monN.append(ID)
        elif 'd' in ID:
            monD.append(ID)
        else:
            good.append(ID)
    return sorted(good)+sorted(monO)+sorted(monN)+sorted(monD)