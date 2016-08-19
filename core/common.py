"""Just stuff Scott likes to use a lot."""

import os
import sys

import datetime
import time
import numpy as np
import IPython.display
import pylab
import scipy.optimize
import urllib
import urllib.request
import glob
import ftplib
import pickle

import tkinter
import tkinter.messagebox
import tkinter.simpledialog

import scipy.ndimage

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import tempfile
import webbrowser

import swhlab
exampleABF=None

### UNITS
# we can predict units by common key values
UNITS={}
for key in "commandV,ahp,peak,threshold".split(","):
    UNITS[key]='mV'
for key in "commandI,Ih".split(","):
    UNITS[key]='pA'
for key in "Rm,Ra".split(","):
    UNITS[key]='MOhm'
for key in "expT,sweepT".split(","):
    UNITS[key]='sec'
for key in "halfwidth".split(","):
    UNITS[key]='ms'
for key in "expI,sweepI".split(","):
    UNITS[key]='points'
for key in "nAPs,sweep".split(","):
    UNITS[key]='#'
for key in "accom1Avg,accom1Steady25,accom5Avg,accom5Steady25,centerBinFrac,centerFrac".split(","):
    UNITS[key]='ratio'
for key in "T1,T2,centerBinTime,centerTime".split(","):
    UNITS[key]='sec'
for key in "msToFirst".split(","):
    UNITS[key]='ms'
for key in "rate,freq,freqAvg,freqBin,freqFirst1,freqFirst5,freqLast,freqSteady25,freqCV".split(","):
    UNITS[key]='Hz'

#APS
for key in "AHP,AHPheight,AHPreturn,halfwidthPoint,height".split(","):
    UNITS[key]='mV'
for key in "AHPI,AHPreturnFullI,AHPreturnI,halfwidthI1,halfwidthI2,peakI,thresholdI,upslopeI".split(","):
    UNITS[key]='points'
for key in "AHPrisetime,risetime".split(","):
    UNITS[key]='ms'
for key in "AHPupslope,downslope,downslopeI,upslope".split(","):
    UNITS[key]='mV/ms'

def getUnit(name):
    """given a column name, return the best guess unit."""
    for key in UNITS:
        if name in key:
            return UNITS[key]
    return "" #never found one

### timing things

def timethis(t=0):
    return time.clock()-t

### python datatype manipulation

def dictFlat(l):
    """Given a list of list of dicts, return just the dicts."""
    if type(l) is dict:
        return [l]
    if "numpy" in str(type(l)):
        return l
    dicts=[]
    for item in l:
        if type(item)==dict:
            dicts.append(item)
        elif type(item)==list:
            for item2 in item:
                dicts.append(item2)
    return dicts

def listCount(l):
    """returns len() of each item in a list, as a list."""
    for i in range(len(l)):
        l[i]=len(l[i])
    return l

def dictVals(l,key):
    """Return all 'key' from a list of dicts. (or list of list of dicts)"""
    dicts=dictFlat(l)
    vals=np.empty(len(dicts))*np.nan
    for i in range(len(dicts)):
        if key in dicts[i]:
            vals[i]=dicts[i][key]
    return vals

def dictAvg(listOfDicts,key,stdErr=False):
    """Given a list (l) of dicts (d), return AV and SD."""
    vals=dictVals(listOfDicts,key)
    if len(vals) and np.any(vals):
        av=np.nanmean(vals)
        er=np.nanstd(vals)
        if stdErr:
            er=er/np.sqrt(np.count_nonzero(~np.isnan(er)))
    else:
        av,er=np.nan,np.nan
    return av,er

def dummyListOfDicts(size=100):
    """
    returns a list (of the given size) of dicts with fake data.
    some dictionary keys are missing for some of the items.
    """
    titles="ahp,halfwidth,peak,expT,expI,sweep".split(",")
    ld=[] #list of dicts
    for i in range(size):
        d={}
        for t in titles:
            if int(np.random.random(1)*100)>5: #5% of values are missing
                d[t]=float(np.random.random(1)*100) #random number 0-100
            if t=="sweep" and "sweep" in d.keys():
                d[t]=int(d[t])
        ld.append(d)
    return ld

def matrixValues(matrix,key):
    """given a key, return a list of values from the matrix with that key."""
    assert key in matrix.dtype.names
    col=matrix.dtype.names.index(key)
    values=np.empty(len(matrix))*np.nan
    for i in range(len(matrix)):
        values[i]=matrix[i][col]
    return values

def matrixToDicts(data):
    """given a recarray, return it as a list of dicts."""

    # 1D array
    if "float" in str(type(data[0])):
        d={}
        for x in range(len(data)):
            d[data.dtype.names[x]]=data[x]
        return d

    # 2D array
    l=[]
    for y in range(len(data)):
        d={}
        for x in range(len(data[y])):
            d[data.dtype.names[x]]=data[y][x]
        l.append(d)
    return l

def matrixfromDicts(dicts):
    """
    Give a list of dicts (or list of list of dicts) return a structured array.
    Headings will be sorted in alphabetical order.
    """
    if 'numpy' in str(type(dicts)):
        return dicts #already an array?
    names=set([])
    dicts=dictFlat(dicts)
    for item in dicts:
        names=names.union(list(item.keys()))
    names=sorted(list(names))
    data=np.empty((len(dicts),len(names)),dtype=float)*np.nan
    for y in range(len(dicts)):
        for key in dicts[y].keys():
            for x in range(len(names)):
                if names[x] in dicts[y]:
                    data[y,x]=dicts[y][names[x]]
    if len(dicts):
        data=np.core.records.fromarrays(data.transpose(),names=names)
    return data #now a structured array

def htmlListToTR(l,trClass=None,tdClass=None,td1Class=None):
    """
    turns a list into a <tr><td>something</td></tr>
    call this when generating HTML tables dynamically.
    """
    html="<tr>"
    for item in l:
        if 'array' in str(type(item)):
            item=item[0] #TODO: why is this needed
        html+="<td>%s</td>"%item
    html+="</tr>"
    if trClass:
        html=html.replace("<tr>",'<tr class="%s">'%trClass)
    if td1Class:
        html=html.replace("<td>",'<td class="%s">'%td1Class,1)
    if tdClass:
        html=html.replace("<td>",'<td class="%s">'%tdClass)


    return html

def html_temp_launch(html):
    """given text, make it a temporary HTML file and launch it."""
    fname = tempfile.gettempdir()+"/swhlab/temp.html"
    with open(fname,'w') as f:
        f.write(html)
    webbrowser.open(fname)

### ORIGIN STUFF (but could be matlab stuff too)

def checkOut(thing,html=True):
    """show everything we can about an object's projects and methods."""
    msg=""
    for name in sorted(dir(thing)):
        if not "__" in name:
            msg+="<b>%s</b>\n"%name
            try:
                msg+=" ^-VALUE: %s\n"%getattr(thing,name)()
            except:
                pass
    if html:
        html='<html><body><code>'+msg+'</code></body></html>'
        html=html.replace(" ","&nbsp;").replace("\n","<br>")
        fname = tempfile.gettempdir()+"/swhlab/checkout.html"
        with open(fname,'w') as f:
            f.write(html)
        webbrowser.open(fname)
    print(msg.replace('<b>','').replace('</b>',''))

def matrixToWks(data,names=None,units=None,bookName=None,sheetName=" ",xCol=None):
    """
    Put 2d numpy data into an Origin worksheet.
    If bookname and sheetname are given try to load data into that book/sheet.
    If the book/sheet doesn't exist, create it.
    """
    if type(data) is list:
        data=matrixfromDicts(data)
    if not names:
        names=[""]*len(data[0])
        if data.dtype.names:
            names=list(data.dtype.names)
    if not units:
        units=[""]*len(data[0])
        for i in range(len(units)):
            if names[i] in UNITS.keys():
                units[i]=UNITS[names[i]]
    if 'recarray' in str(type(data)): #make it a regular array
        data=data.view(float).reshape(data.shape + (-1,))
    if xCol and xCol in names:
        xCol=names.index(xCol)
        names.insert(0,names[xCol])
        units.insert(0,units[xCol])
        data=np.insert(data,0,data[:,xCol],1)

    if not bookName:
        bookName="tempBook"
    if not sheetName:
        sheetName="temp-"+str(time.clock())[-5:]

    try:
        import PyOrigin
        PyOrigin.LT_execute("") #try to crash a non-orign environment
    except:
        print(" -- PyOrigin not running, making HTML output.")
        matrixToHTML(data,names,units,bookName,sheetName,xCol)
        return

    nrows,ncols=len(data),len(data[0])
    if 'recarray' in str(type(data)): #convert structured array to regular array
        data=np.array(data.view(),dtype=float).reshape((nrows,ncols))
    data=np.transpose(data) #transpose it

    PyOrigin.LT_execute("activateSheet(%s, %s)"%(bookName,sheetName))
    wks=PyOrigin.ActiveLayer()
    while wks.GetColCount() < ncols:
        wks.InsertCol(wks.GetColCount(),'')
    for i in range(ncols):
        col=wks.Columns(i)
        col.SetLongName(names[i])
        col.SetUnits(units[i])
    wks.SetData(data,0,0)
    PyOrigin.LT_execute("FixNanBug")
    PyOrigin.LT_execute("ABFPathToMetaData")

def matrixToHTML(data,names=None,units=None,bookName=None,sheetName=None,xCol=None):
    """Put 2d numpy data into a temporary HTML file."""
    if not names:
        names=[""]*len(data[0])
        if data.dtype.names:
            names=list(data.dtype.names)
    if not units:
        units=[""]*len(data[0])
        for i in range(len(units)):
            if names[i] in UNITS.keys():
                units[i]=UNITS[names[i]]
    if 'recarray' in str(type(data)): #make it a regular array
        data=data.view(float).reshape(data.shape + (-1,))
    if xCol and xCol in names:
        xCol=names.index(xCol)
        names.insert(0,names[xCol])
        units.insert(0,units[xCol])
        data=np.insert(data,0,data[:,xCol],1)

    htmlFname = tempfile.gettempdir()+"/swhlab/WKS-%s.%s.html"%(bookName,sheetName)
    html="""<body>
    <style>
    body {
          background-color: #ababab;
          padding:20px;
          }
    table {
           font-size:12px;
           border-spacing: 0;
           border-collapse: collapse;
           //border:2px solid #000000;
           }
    .name {background-color:#fafac8;text-align:center;}
    .units {background-color:#fafac8;text-align:center;}
    .data0 {background-color:#FFFFFF;font-family: monospace;text-align:center;}
    .data1 {background-color:#FAFAFA;font-family: monospace;text-align:center;}
    .labelRow {background-color:#e0dfe4; text-align:right;border:1px solid #000000;}
    .labelCol {background-color:#e0dfe4; text-align:center;border:1px solid #000000;}
    td {
        border:1px solid #c0c0c0; padding:5px;
        //font-family: Verdana, Geneva, sans-serif;
        font-family: Arial, Helvetica, sans-serif
        }
    </style>
    <html>"""
    html+="<h1>FauxRigin</h1>"
    if bookName or sheetName:
        html+='<code><b>%s / %s</b></code><br><br>'%(bookName,sheetName)
    html+="<table>"
    #cols=list(range(len(names)))
    colNames=['']
    for i in range(len(units)):
        label="%s (%d)"%(chr(i+ord('A')),i)
        colNames.append(label)
    html+=htmlListToTR(colNames,'labelCol','labelCol')
    html+=htmlListToTR(['Long Name']+list(names),'name',td1Class='labelRow')
    html+=htmlListToTR(['Units']+list(units),'units',td1Class='labelRow')
    cutOff=False
    for y in range(len(data)):
        html+=htmlListToTR([y+1]+list(data[y]),trClass='data%d'%(y%2),td1Class='labelRow')
        if y>=200:
            cutOff=True
            break
    html+="</table>"
    html=html.replace(">nan<",">--<")
    html=html.replace(">None<","><")
    if cutOff:
        html+="<h3>... showing only %d of %d rows ...</h3>"%(y,len(data))
    html+="</body></html>"
    with open(htmlFname,'w') as f:
        f.write(html)
    webbrowser.open(htmlFname)
    return


### XML STUFF

def XMLtoPython(xmlStr=r"C:\Apps\pythonModules\GSTemp.xml"):
    """
    given a string or a path to an XML file, return an XML object.
    """
    #TODO: this absolute file path crazy stuff needs to stop!
    if os.path.exists(xmlStr):
        with open(xmlStr) as f:
            xmlStr=f.read()
    print(xmlStr)
    print("DONE")
    return

def XMLfromPython(xmlObj,saveAs=False):
    """
    given a an XML object, return XML string.
    optionally, save it to disk.
    """
    return

### curve fitting

def algo_exp(x, m, t, b):
    """mono-exponential curve."""
    return m*np.exp(-t*x)+b

def fit_exp(y,graphToo=False):
    """Exponential fit. Returns [multiplier, t, offset, time constant]"""
    x=np.arange(len(y))
    try:
        params, cv = scipy.optimize.curve_fit(algo_exp, x, y, p0=(1,1e-6,1))
    except:
        print(" !! curve fit failed (%.02f points)"%len(x))
        return np.nan,np.nan,np.nan,np.nan #can't fit so little data!
    m,t,b=params
    tau=1/t
    if graphToo:
        pylab.figure(figsize=(6,4))
        pylab.grid()
        pylab.title("FIT ASSESSMENT")
        pylab.plot(x,y,'o',mfc='none',ms=10)
        pylab.plot(x,algo_exp(x,m,t,b),'b-',lw=2)
        pylab.show()
    return m,t,b,tau # multiplier, t, offset, time constant

### numpy array manipulation

def numpyAlignXY(data):
    """
    given a numpy array (XYXYXY columns), return it aligned.
    data returned will be XYYY. NANs may be returned.
    """
    print(data)
    Xs=data.flatten()[::2] # get all X values
    Xs=Xs[~np.isnan(Xs)] # remove nans
    Xs=sorted(list(set(Xs))) # eliminate duplicates then sort it
    aligned=np.empty((len(Xs),int(len(data[0])/2+1)))*np.nan
    aligned[:,0]=Xs
    for col in range(0,len(data[0]),2):
        for row in range(len(data)):
            X=data[row,col]
            Y=data[row,col+1]
            if np.isnan(X) or np.isnan(Y):
                continue
            aligned[Xs.index(X),int(col/2+1)]=Y
    return aligned

def filter_gaussian(Ys,sigma,plotToo=False):
    """simple gaussian convolution. Returns same # of points as gotten."""
    timeA=time.time()
    window=scipy.signal.gaussian(len(Ys),sigma)
    window/=sum(window)
    Ys2=np.convolve(Ys,window,'same')
    print("LEN:",len(Ys2),len(Ys))
    timeB=time.time()
    print("convolution took %.03f ms"%((timeB-timeA)*1000))
    if len(Ys2)!=len(Ys):
        print("?!?!?!? convolution point size mismatch")
    if plotToo:
        pylab.plot(Ys,label='original',alpha=.2)
        pylab.plot(Ys2,'b-',label='smooth')
        pylab.legend()
        pylab.show()
    return Ys2


def where_cross(data,threshold):
    """return a list of Is where the data first crosses above threshold."""
    Is=np.where(data>threshold)[0]
    Is=np.concatenate(([0],Is))
    Ds=Is[:-1]-Is[1:]+1
    return Is[np.where(Ds)[0]+1]

### IPython stuff

def show(closeToo=False):
    """alternative to pylab.show() that updates IPython window."""
    IPython.display.display(pylab.gcf())
    if closeToo:
        pylab.close('all')

### Silly data type and printing


def originFormat_listOfDicts(l):
    """Return [{},{},{}] as a 2d matrix."""
    titles=[]
    for d in l:
        for k in d.keys():
            if not k in titles:
                titles.append(k)
    titles.sort()
    data=np.empty((len(l),len(titles)))*np.nan
    for y in range(len(l)):
        for x in range(len(titles)):
            if titles[x] in l[y].keys():
                data[y][x]=l[y][titles[x]]
    return titles,data

def originFormat(thing):
    """Try to format anything as a 2D matrix with column names."""
    if type(thing) is list and type(thing[0]) is dict:
        return originFormat_listOfDicts(thing)
    if type(thing) is list and type(thing[0]) is list:
        return originFormat_listOfDicts(dictFlat(thing))
    else:
        print(" !! I don't know how to format this object!")
        print(thing)

def pickle_load(fname):
    """return the contents of a pickle file"""
    thing = pickle.load(open(fname,"rb"))
    return thing

def pickle_save(thing,fname):
    """save something to a pickle file"""
    pickle.dump(thing, open(fname,"wb"),pickle.HIGHEST_PROTOCOL)
    return thing

def getPkl(fname): #TODO: remove this
    """return the contents of a pickle file"""
    thing = pickle.load(open(fname,"rb"))
    return thing

def msgDict(d,matching=None,sep1="=",sep2="\n",sort=True,cantEndWith=None):
    """convert a dictionary to a pretty formatted string."""
    msg=""
    if "record" in str(type(d)):
        keys=d.dtype.names
    else:
        keys=d.keys()
    if sort:
        keys=sorted(keys)
    for key in keys:
        if key[0]=="_":
            continue
        if matching:
            if not key in matching:
                continue
        if cantEndWith and key[-len(cantEndWith)]==cantEndWith:
            continue
        if 'float' in str(type(d[key])):
            s="%.02f"%d[key]
        else:
            s=str(d[key])
        if "object" in s:
            s='<object>'
        msg+=key+sep1+s+sep2
    return msg.strip()

def showDict(d,title):
    if title:
        print("### %s ###"%title)
    for key in sorted(d.keys()):
        t=str(type(d[key])).split("'")[1]
        print("%s <%s> %s"%(key,t,d[key]))

### dates and times

def epochToDatetime(epoch=time.time()):
    return datetime.datetime.fromtimestamp(epoch)

def datetimeToString(dt):
    return dt.strftime('%Y-%m-%d %H:%M:%S') #standard for all SWHLAB

def epochToString(epoch):
    return datetimeToString(epochToDatetime())

### Trivial ABF analysis

def groupsFromKey(keyFile='./key.txt'):
    """
    given a groups file, return a dict of groups.
    Example:
        ### GROUP: TR
        16602083
        16608059
        ### GROUP: TU
        16504000
        16507011
    """
    groups={}
    thisGroup="?"
    with open(keyFile) as f:
        raw=f.read().split("\n")
    for line in raw:
        line=line.strip()
        if len(line)<3:
            continue
        if "### GROUP" in line:
            thisGroup=line.split(": ")[1]
            groups[thisGroup]=[]
        else:
            groups[thisGroup]=groups[thisGroup]+[line]
    return groups


def findRelevantData(fileList,abfs):
    """return an abf of the *FIRST* of every type of thing."""
    relevant=[]
    things={}
    for abf in abfs:
        for fname in fileList:
            if abf in fname and not fname in relevant:
                relevant.append(fname)
    for item in sorted(relevant):
        thing = os.path.basename(item)
        if ".png" in thing:
            continue
        if not "_" in thing:
            continue
        thing=thing.split("_")[-1].split(".")[0]
        if not thing in things.keys(): #prevent overwriting
            things[thing]=item
    return things

def determineProtocol(fname):
    """determine the comment cooked in the protocol."""
    f=open(fname,'rb')
    raw=f.read(5000) #it should be in the first 5k of the file
    f.close()
    protoComment="unknown"
    if b"SWHLab4[" in raw:
        protoComment=raw.split(b"SWHLab4[")[1].split(b"]",1)[0]
    elif b"SWH[" in raw:
        protoComment=raw.split(b"SWH[")[1].split(b"]",1)[0]
    else:
        protoComment="?"
    if not type(protoComment) is str:
        protoComment=protoComment.decode("utf-8")
    return protoComment


def forwardSlash(listOfFiles):
    """convert silly C:\\names\\like\\this.txt to c:/names/like/this.txt"""
    for i,fname in enumerate(listOfFiles):
        listOfFiles[i]=fname.replace("\\","/")
    return listOfFiles

def scanABFfolder(abfFolder):
    """
    scan an ABF directory and subdirectory. Try to do this just once.
    Returns ABF files, SWHLab files, and groups.
    """
    assert os.path.isdir(abfFolder)
    filesABF=forwardSlash(sorted(glob.glob(abfFolder+"/*.*")))
    filesSWH=[]
    if os.path.exists(abfFolder+"/swhlab4/"):
        filesSWH=forwardSlash(sorted(glob.glob(abfFolder+"/swhlab4/*.*")))
    groups=getABFgroups(filesABF)
    return filesABF,filesSWH,groups

def getParent(abfFname):
    """given an ABF file name, return the ABF of its parent."""
    child=os.path.abspath(abfFname)
    files=sorted(glob.glob(os.path.dirname(child)+"/*.*"))
    parentID=abfFname #its own parent
    for fname in files:
        if fname.endswith(".abf") and fname.replace(".abf",".TIF") in files:
            parentID=os.path.basename(fname).replace(".abf","")
        if os.path.basename(child) in fname:
            break
    return parentID

def getParent2(abfFname,groups):
    """given an ABF and the groups dict, return the ID of its parent."""
    if ".abf" in abfFname:
        abfFname=os.path.basename(abfFname).replace(".abf","")
    for parentID in groups.keys():
        if abfFname in groups[parentID]:
            return parentID
    return abfFname #no parent found, return itself

def getNotesForABF(abfFile):
    """given an ABF, find the parent, return that line of experiments.txt"""
    parent=getParent(abfFile)
    parent=os.path.basename(parent).replace(".abf","")
    expFile=os.path.dirname(abfFile)+"/experiment.txt"
    if not os.path.exists(expFile):
        return "no experiment file"
    with open(expFile) as f:
        raw=f.readlines()
    for line in raw:
        if line[0]=='~':
            line=line[1:].strip()
            if line.startswith(parent):
                while "\t\t" in line:
                    line=line.replace("\t\t","\t")
                line=line.replace("\t","\n")
                return line
    return "experiment.txt found, but didn't contain %s"%parent

def getABFgroups(files):
    """
    given a list of ALL files (not just ABFs), return a dict[ID]=[ID,ID,ID].
    Parents are determined if a .abf matches a .TIF.
    This is made to assign children files to parent ABF IDs.
    """
    children=[]
    groups={}
    for fname in sorted(files):
        if fname.endswith(".abf"):
            if fname.replace(".abf",".TIF") in files: #TODO: cap sensitive
                if len(children):
                    groups[children[0]]=children
                children=[os.path.basename(fname)[:-4]]
            else:
                children.append(os.path.basename(fname)[:-4])
    groups[children[0]]=children
    #print(" -- found %d groups of %d ABFs"%(len(groups),len(files)))
    return groups

def getIDfileDict(files):
    """
    given a list of files, return a dict[ID]=[files].
    This is made to assign children files to parent ABF IDs.
    """
    d={}
    orphans=[]
    for fname in files:
        if fname.endswith(".abf"):
            d[os.path.basename(fname)[:-4]]=[]
    for fname in files:
        if fname.endswith(".html") or fname.endswith(".txt"):
            continue #don't try to assign to an ABF
        if len(os.path.basename(fname).split(".")[0])>=8:
            ID = os.path.basename(fname)[:8] #ABF ID (first several chars)
        else:
            ID = os.path.basename(fname).split(".")[0] #short filename, just not extension
        if ID in d.keys():
            d[ID]=d[ID]+[fname]
        else:
            orphans.append(os.path.basename(fname))
            #print(" ?? orphan file",ID,os.path.basename(fname))
    if orphans:
        print(" ?? found %d orphan files"%len(orphans))
    return d

def getIDsFromFiles(files):
    """given a path or list of files, return ABF IDs."""
    if type(files) is str:
        files=glob.glob(files+"/*.*")
    IDs=[]
    for fname in files:
        if fname[-4:].lower()=='.abf':
            ext=fname.split('.')[-1]
            IDs.append(os.path.basename(fname).replace('.'+ext,''))
    return sorted(IDs)

def inspectABF(abf=exampleABF,saveToo=False,justPlot=False):
    """May be given an ABF object or filename."""
    pylab.close('all')
    print(" ~~ inspectABF()")
    if type(abf) is str:
        abf=swhlab.ABF(abf)
    swhlab.plot.new(abf,forceNewFigure=True)
    if abf.sweepInterval*abf.sweeps<60*5: #shorter than 5 minutes
        pylab.subplot(211)
        pylab.title("%s [%s]"%(abf.ID,abf.protoComment))
        swhlab.plot.sweep(abf,'all')
        pylab.subplot(212)
        swhlab.plot.sweep(abf,'all',continuous=True)
        swhlab.plot.comments(abf)
    else:
        print(" -- plotting as long recording")
        swhlab.plot.sweep(abf,'all',continuous=True,minutes=True)
        swhlab.plot.comments(abf,minutes=True)
        pylab.title("%s [%s]"%(abf.ID,abf.protoComment))
    swhlab.plot.annotate(abf)
    if justPlot:
        return
    if saveToo:
        path=os.path.split(abf.fname)[0]
        basename=os.path.basename(abf.fname)
        pylab.savefig(os.path.join(path,"_"+basename.replace(".abf",".png")))
    pylab.show()
    return

def inspectFolder(folder,saveToo=False):
    for fname in glob.glob(folder+"/*.abf"):
        inspectABF(fname,saveToo)

### Web stuff


def download(url,saveAs=False):
    if saveAs:
        return urllib.request.urlretrieve(url, saveAs)
    return urllib.request.urlopen(url).read().decode("ascii")

#def downloadLinks(url,matching='.zip'):
#    """return a list of all <a href=""> contents from a html page."""
#    links=[]
#    html=download(url).split('<a href')[1:]
#    for link in html:
#        link = link.split('"')[1]
#        if not ("/" in link or "." in link):
#            continue
#        if link[0] == '/':
#            continue
#        if matching:
#            if not matching in link:
#                continue
#        links.append(os.path.join(url,link))
#    return links

def ftp_login(folder=None):
    """return an "FTP" object after logging in."""
    pwDir=os.path.realpath(__file__)
    for i in range(3):
        pwDir=os.path.dirname(pwDir)
    pwFile = os.path.join(pwDir,"passwd.txt")
    print(" -- looking for login information in:\n   [%s]"%pwFile)
    try:
        with open(pwFile) as f:
            lines=f.readlines()
        username=lines[0].strip()
        password=lines[1].strip()
        print(" -- found a valid username/password")
    except:
        print(" -- password lookup FAILED.")
        username=TK_askPassword("FTP LOGIN","enter FTP username")
        password=TK_askPassword("FTP LOGIN","enter password for %s"%username)
        if not username or not password:
            print(" !! failed getting login info. aborting FTP effort.")
            return
    print("      username:",username)
    print("      password:","*"*(len(password)))
    print(" -- logging in to FTP ...")
    try:
        ftp = ftplib.FTP("swharden.com")
        ftp.login(username, password)
        if folder:
            ftp.cwd(folder)
        return ftp
    except:
        print(" !! login failure !!")
        return False

def ftp_folder_match(ftp,localFolder,deleteStuff=True):
    """upload everything from localFolder into the current FTP folder."""
    for fname in glob.glob(localFolder+"/*.*"):
        ftp_upload(ftp,fname)
    return

def ftp_upload(ftp,localFname,ftpFname=None):
    print(" -- uploading",os.path.basename(localFname))
    ftp.storbinary("STOR " + os.path.basename(localFname), open(localFname, "rb"), 1024) #for binary files
    if ftpFname:
        ftp.rename(os.path.basename(localFname),ftpFname)
    return


def version_upload(fname,username="nibjb"):
    """Only scott should do this. Upload new version to site."""
    print("popping up pasword window...")
    password=TK_askPassword("FTP LOGIN","enter password for %s"%username)
    if not password:
        return
    print("username:",username)
    print("password:","*"*(len(password)))
    print("connecting...")
    ftp = ftplib.FTP("swharden.com")
    ftp.login(username, password)
    print("successful login!")
    ftp.cwd("/software/swhlab/versions") #IMMEDIATELY GO HERE!!!
    print("uploading",os.path.basename(fname))
    ftp.storbinary("STOR " + os.path.basename(fname), open(fname, "rb"), 1024) #for binary files
    print("disconnecting...")
    ftp.quit()

### TK GUI

def TK_askPassword(title="input",msg="type here:"):
    """use the GUI to ask for a string."""
    root = tkinter.Tk()
    root.withdraw() #hide tk window
    root.attributes("-topmost", True) #always on top
    root.lift() #bring to top
    value=tkinter.simpledialog.askstring(title,msg)
    root.destroy()
    return value

def TK_message(title,msg):
    """use the GUI to pop up a message."""
    root = tkinter.Tk()
    root.withdraw() #hide tk window
    root.attributes("-topmost", True) #always on top
    root.lift() #bring to top
    tkinter.messagebox.showwarning(title, msg)
    root.destroy()

def TK_ask(title,msg):
    """use the GUI to ask YES or NO."""
    root = tkinter.Tk()
    root.attributes("-topmost", True) #always on top
    root.withdraw() #hide tk window
    result=tkinter.messagebox.askyesno(title,msg)
    root.destroy()
    return result


### Imaging

def image_convert(fname,saveAs=True,showToo=False):
    """
    Convert weird TIF files into web-friendly versions.
    Auto contrast is applied (saturating lower and upper 0.1%).
        make saveAs True to save as .TIF.png
        make saveAs False and it won't save at all
        make saveAs "someFile.jpg" to save it as a different path/format
    """

    # load the image
    #im = Image.open(fname) #PIL can't handle 12-bit TIFs well
    im=scipy.ndimage.imread(fname) #scipy does better with it
    im=np.array(im,dtype=float) # now it's a numpy array

    # do all image enhancement here
    cutoffLow=np.percentile(im,.01)
    cutoffHigh=np.percentile(im,99.99)
    im[np.where(im<cutoffLow)]=cutoffLow
    im[np.where(im>cutoffHigh)]=cutoffHigh

    # IMAGE FORMATTING
    im-=np.min(im) #auto contrast
    im/=np.max(im) #normalize
    im*=255 #stretch contrast (8-bit)
    im = Image.fromarray(im)

    # IMAGE DRAWING
    msg="Filename: %s\n"%os.path.basename(fname)
    timestamp = datetime.datetime.fromtimestamp(os.path.getctime(fname))
    msg+="Created: %s\n"%timestamp.strftime('%Y-%m-%d %H:%M:%S')
    d = ImageDraw.Draw(im)
    fnt = ImageFont.truetype("arial.ttf", 20)
    d.text((6,6),msg,font=fnt,fill=0)
    d.text((4,4),msg,font=fnt,fill=255)

    if showToo:
        im.show()
    if saveAs is False:
        return
    if saveAs is True:
        saveAs=fname+".png"
    im.convert('RGB').save(saveAs)

### LOGGING ###
def log_crash(msg):
    f=open('crash.log','a')
    f.write("[]")

if __name__=="__main__":
    print("DONT RUN THIS DIRECTLY.")
    XMLtoPython()
