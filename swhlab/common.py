# start out this way so tests will import the local swhlab module
import sys
import os
sys.path.insert(0,os.path.abspath('../'))
import swhlab
import time
# now import things regularly
import numpy as np
import time
import datetime
import tempfile

### numpy

def where_cross(data,threshold):
    """return a list of Is where the data first crosses above threshold."""
    Is=np.where(data>threshold)[0]
    Is=np.concatenate(([0],Is))
    Ds=Is[:-1]-Is[1:]+1
    return Is[np.where(Ds)[0]+1]

def kernel_gaussian(size=100, sigma=None, forwardOnly=False):
    """
    return a 1d gassuan array of a given size and sigma.
    If sigma isn't given, it will be 1/10 of the size, which is usually good.
    Note that this is fully numpy, and doesn't use scipy.
    """
    if sigma is None:
        sigma=size/10
    size=int(size)
    points=np.exp(-np.power(np.arange(size)-size/2,2)/(2*np.power(sigma,2)))
    if forwardOnly:
        points[:int(len(points)/2)]=0
    return points/sum(points)

def lowpass(data,filterSize=None):
    """
    minimal complexity low-pass filtering.
    Filter size is how "wide" the filter will be.
    Sigma will be 1/10 of this filter width.
    If filter size isn't given, it will be 1/10 of the data size.
    """
    if filterSize is None:
        filterSize=len(data)/10
    kernel=kernel_gaussian(size=filterSize)
    data=convolve(data,kernel) # do the convolution with padded edges
    return data

def convolve(signal,kernel):
    """
    This applies a kernel to a signal through convolution and returns the result.

    Some magic is done at the edges so the result doesn't apprach zero:
        1. extend the signal's edges with len(kernel)/2 duplicated values
        2. perform the convolution ('same' mode)
        3. slice-off the ends we added
        4. return the same number of points as the original
    """
    pad=np.ones(len(kernel)/2)
    signal=np.concatenate((pad*signal[0],signal,pad*signal[-1]))
    signal=np.convolve(signal,kernel,mode='same')
    signal=signal[len(pad):-len(pad)]
    return signal

### system operations

def waitFor(sec=5):
    """wait a given number of seconds until returning."""
    while sec:
        print("waiting for",sec,"...")
        sec-=1
        time.sleep(1)

def pause():
    """halt everything until user input. Use this sparingly."""
    input("\npress ENTER to continue ...")

def exceptionToString(e):
    """when you "except Exception as e", give me the e and I'll give you a string."""
    exc_type, exc_obj, exc_tb = sys.exc_info()
    s="EXCEPTION THROWN UNEXPECTEDLY"
    s+="  FILE: %s\n"%os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    s+="  LINE: %s\n"%exc_tb.tb_lineno
    s+="  TYPE: %s\n"%exc_type
    return s

def isIpython():
    """returns True if running in an Ipython interpreter."""
    try:
        #print("testing Ipython [%s]"%str(__IPYTHON__))
        if str(__IPYTHON__):
            return True
    except:
        return False


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

def list_move_to_front(l,value='other'):
    """if the value is in the list, move it to the front and return it."""
    l=list(l)
    if value in l:
        l.remove(value)
        l.insert(0,value)
    return l

def list_move_to_back(l,value='other'):
    """if the value is in the list, move it to the back and return it."""
    l=list(l)
    if value in l:
        l.remove(value)
        l.append(value)
    return l

def list_order_by(l,firstItems):
    """given a list and a list of items to be first, return the list in the
    same order except that it begins with each of the first items."""
    l=list(l)
    for item in firstItems[::-1]: #backwards
        if item in l:
            l.remove(item)
            l.insert(0,item)
    return l

def list_to_lowercase(l):
    """given a list of strings, make them all lowercase."""
    return [x.lower() for x in l if type(x) is str]

### abf organization

def ext(fname):
    """return the extension of a filename."""
    if "." in fname:
        return os.path.splitext(fname)[1]
    return fname

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

def abfGroups(abfFolder):
    """
    Given a folder path or list of files, return groups (dict) by cell.

    Rules which define parents (cells):
        * assume each cell has one or several ABFs
        * that cell can be labeled by its "ID" or "parent" ABF (first abf)
        * the ID is just the filename of the first abf without .abf
        * if any file starts with an "ID", that ID becomes a parent.
        * examples could be 16o14044.TIF or 16o14044-cell1-stuff.jpg
        * usually this is done by saving a pic of the cell with same filename

    Returns a dict of "parent IDs" representing the "children"
        groups["16o14041"] = ["16o14041","16o14042","16o14043"]

    From there, getting children files is trivial. Just find all files in
    the same folder whose filenames begin with one of the children.
    """

    # prepare the list of files, filenames, and IDs
    files=False
    if type(abfFolder) is str and os.path.isdir(abfFolder):
        files=abfSort(os.listdir(abfFolder))
    elif type(abfFolder) is list:
        files=abfSort(abfFolder)
    assert type(files) is list
    files=list_to_lowercase(files)

    # group every filename in a different list, and determine parents
    abfs, IDs, others, parents, days = [],[],[],[],[]
    for fname in files:
        if fname.endswith(".abf"):
            abfs.append(fname)
            IDs.append(fname[:-4])
            days.append(fname[:5])
        else:
            others.append(fname)
    for ID in IDs:
        for fname in others:
            if fname.startswith(ID):
                parents.append(ID)
    parents=abfSort(set(parents)) # allow only one copy each
    days=abfSort(set(days)) # allow only one copy each

    # match up children with parents, respecting daily orphans.
    groups={}
    for day in days:
        parent=None
        for fname in [x for x in abfs if x.startswith(day)]:
            ID=fname[:-4]
            if ID in parents:
                parent=ID
            if not parent in groups.keys():
                groups[parent]=[]
            groups[parent].extend([ID])
    return groups

def abfGroupFiles(groups,folder):
    """
    when given a dictionary where every key contains a list of IDs, replace
    the keys with the list of files matching those IDs. This is how you get a
    list of files belonging to each child for each parent.
    """
    assert os.path.exists(folder)
    files=os.listdir(folder)
    group2={}
    for parent in groups.keys():
        if not parent in group2.keys():
            group2[parent]=[]
        for ID in groups[parent]:
            for fname in [x.lower() for x in files if ID in x.lower()]:
                group2[parent].extend([fname])
    return group2

def parent(groups,ID):
    """given a groups dictionary and an ID, return its actual parent ID."""
    if ID in groups.keys():
        return ID # already a parent
    if not ID in groups.keys():
        for actualParent in groups.keys():
            if ID in groups[actualParent]:
                return actualParent # found the actual parent
    return None # doesn't have a parent in this group!

def filesByType(fileList):
    """
    given a list of files, return them as a dict sorted by type:
        * plot, tif, data, other
    """
    features=["plot","tif","data","other","experiment"]
    files={}
    for feature in features:
        files[feature]=[]
    for fname in fileList:
        other=True
        for feature in features:
            if "_"+feature+"_" in fname:
                files[feature].extend([fname])
                other=False
        if other:
            files['other'].extend([fname])
    return files

### temp files

def userFolder():
    """return the semi-temporary user folder"""
    #path=os.path.abspath(tempfile.gettempdir()+"/swhlab/")
    #don't use tempdir! it will get deleted easily.
    path=os.path.expanduser("~")+"/.swhlab/" # works on windows or linux
    # for me, path=r"C:\Users\swharden\.swhlab"
    if not os.path.exists(path):
        print("creating",path)
        os.mkdir(path)
    return os.path.abspath(path)

def abfFname_Load():
    """return the path of the last loaded ABF."""
    fname=userFolder()+"/abfFname.ini"
    if os.path.exists(fname):
        abfFname=open(fname).read().strip()
        if os.path.exists(abfFname) or abfFname.endswith("_._"):
            return abfFname
    return os.path.abspath(os.sep)


def abfFname_Save(abfFname):
    """return the path of the last loaded ABF."""
    fname=userFolder()+"/abfFname.ini"
    with open(fname,'w') as f:
        f.write(os.path.abspath(abfFname))
    return

### GUI

def gui_getFile():
    """
    Launch an ABF file selection file dialog.
    This is smart, and remembers (through reboots) where you last were.
    """
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk() # this is natively supported by python
    root.withdraw() # hide main window
    root.wm_attributes('-topmost', 1) # always on top
    fname = filedialog.askopenfilename(title = "select ABF file",
                                       filetypes=[('ABF Files', '.abf')],
                                       initialdir=os.path.dirname(abfFname_Load()))
    if fname.endswith(".abf"):
        abfFname_Save(fname)
        return fname
    else:
        print("didn't select an ABF!")
        return None

def gui_getFolder():
    """
    Launch a folder selection dialog.
    This is smart, and remembers (through reboots) where you last were.
    """
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk() # this is natively supported by python
    root.withdraw() # hide main window
    root.wm_attributes('-topmost', 1) # always on top
    fname = filedialog.askdirectory(title = "select folder of ABFs",
                                       initialdir=os.path.dirname(abfFname_Load()))
    if len(fname)>3:
        abfFname_Save(fname+"/_._")
        return fname
    else:
        print("didn't select an ABF!")
        return None

if __name__=="__main__":
    gui_getFile()
    print("DONE")
    #print("DONT RUN THIS DIRECTLY")
    #abfFolder=r'C:\Users\scott\Documents\important\abfs'
#    group=abfGroups(abfFolder)
#    group2=abfGroupFiles(group,abfFolder+"/swhlab/")
#    for key in group2:
#        print()
#        print(key)
#        print("\n".join(group2[key]))