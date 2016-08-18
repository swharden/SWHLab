"""
standalone common tasks in Origin.
Some tasks are specific to CJFLab.
Many are not.
"""

import swhlab
import os
import swhlab
import numpy as np
import webbrowser
import tempfile
import glob
import imp
import traceback
import sys
import subprocess
import swhlab.core.common as cm
import time

from swhlab.origin import pyOriginXML

try:
    import PyOrigin #will work in spyder
except:
    pass

### LABTALK

def log(msg,level=3):
    if type(msg) in [str,int,float]:
        msg=[[msg,level]]
    for item in msg:
        line=str(item[0])+" "+str(item[1])
        line=" ".join(line.split(" "))
        # by now the last single character is the loglevel
        cmd='log [%s] %s'%(line[:-2],line[-1])
    LT(cmd,False)

def log_level(level=None):
    if type(level) is int:
        LT('log_level %d'%(level))
    return LT_get("LOGLEVEL")


def LT(cmd,logit=True):
    """execute a labtalk command."""
    cmd=cmd.replace("\\","/") #I know, right?
    cmd=cmd.strip()
    if not cmd.endswith(";"):
        cmd=cmd+";"
    if logit:
        log("~>%s"%cmd,4)
    PyOrigin.LT_execute(cmd)

def LT_set(name,val):
    """set a labtalk variable. Knows to add $ if it's a string."""
    if type(val) is str:
        PyOrigin.LT_set_str(name,val)
    else:
        PyOrigin.LT_set_var(name,val)
    return

def LT_get(name,string=False):
    """get a labtalk variable. If it's a string, it'll add the $."""
    if string:
        if not name.endswith("$"):
            name+="$"
        val=str(PyOrigin.LT_get_str(name.upper()))
    else:
        val=float(PyOrigin.LT_get_var(name.upper())) #MUST BE ALL CAPS
    log(" -- LT [%s]=%s"%(name.upper(),val),4)
    return val

### CONVERSIONS

def treeToDict(s):
    """
    given a str(PyOrigin.tree), return a dictionary of dictionaries.
    This is done by dynamically generating python scipt to populate the
    dictionary pyvals{}, then return it. Technically malicious code
    could be inserted in strings in the pyvals, and it will be evaluated.
    """
    log(" -- treeToDict() is old! use XML methods!")
    def levelFromLine(s):
        """yes I'm putting a function inside a function."""
        level=0
        while len(s) and s[0]==" ":
            s=s[1:]
            level+=1
        return level+1
    s=s.replace("\\","/")
    s=s.replace("  "," ")
    s=s.split("\n")
    parents=[]
    pyvals={}
    for i,line in enumerate(s):
        if len(line.strip())<3:
            continue
        name,val=line,None
        if " = " in line:
            name,val=line.split(" = ")
            val=val.strip()
        name=name.strip()
        level=levelFromLine(line)
        if level>len(parents):
            parents.append(None)
        parents[level-1]=name
        s[i]='pyvals'
        for parent in parents[:level]:
            s[i]=s[i]+'["%s"]'%parent
        #s[i]=".".join(parents[:level])
        if val:
            s[i]+=' = "%s"'%val
        else:
            s[i]+=' = {}'
    for line in sorted(s):
        if VERBOSE:
            log(line)
        exec(line)
    return pyvals

### NOTE ACTIONS

def note_new(name="note"):
    """make a new notes window."""
    note_select(name)
    selectedNotesPage=""
    try:
        selectedNotesPage=str(PyOrigin.ActiveNotePage())
    except:
        pass
    if not str(selectedNotesPage) == str(name):
        LT('win -n notes %s'%name)

def note_select(name):
    """select a note window."""
    LT('win -an %s'%name)

def note_read(selectNote=False):
    """
    Return contents of the active notes page.
    If a note name is given, select that notes page first.
    """
    if selectNote:
        note_select(selectNote)
    return PyOrigin.ActiveNotePage().GetText()

def note_set(text):
    """set contents of the active notes page."""
    PyOrigin.ActiveNotePage().SetText(text)

def note_append(text,pre="\n"):
    """append text to the active notes page."""
    note_set(note_read()+pre+text)

def note_to_groups(text,d={}):
    """
    given text from a note objet, return a groups dictionary.
    optionally give this a dictionary to add to.
    if text is a .txt filename, load its contents.
    """
    if text.endswith(".txt") and os.path.exists(text):
        with open(text) as f:
            text=f.read()
    text=text.split("\n")
    currentGroup=["NOTES MUST START WITH A GROUP"]
    for line in text:
        if len(line)<3 or line.startswith("#"):
            continue
        line=line.upper()
        if line.startswith("GROUP:"):
            currentGroup=line.replace("GROUP:","").strip()
        else:
            if not currentGroup in d.keys():
                d[currentGroup]=[]
            d[currentGroup]=d[currentGroup]+[line.strip()]
    return d

### BOOK ACTIONS

def book_setHidden(book=None,hidden=1):
    """sets hidden state of the currently active book."""
    if book:
        book_select(book)
    else:
        book=book_getActive()
    LT('win -ch %d "%s"'%(hidden,book))

def book_getNames():
    """return list of names for all books."""
    names=[]
    if PyOrigin.WorksheetPages().GetCount()==0:
        return names
    for book in PyOrigin.WorksheetPages():
        names.append(book.GetName())
    return sorted(names)

def book_new(book,sheet=False):
    if not book in book_getNames():
        LT('newbook name:="%s" sheet:=0 option:=lsname;'%book)
    book_select(book)
    if sheet:
        sheet_new(sheet)

def book_select(book,sheet=False):
    """select the given workbook."""
    LT('win -a %s;'%book) #TODO: warn if book doesn't eixst
    #redraw() this is slow
    if sheet:
        sheet_select(sheet)

def book_getActive():
    """
    returns the name of the selected book.
    returns False if no book is selected.
    """
    try:
        return PyOrigin.ActivePage().GetName()
    except:
        return False

def book_close(book):
    """close the given book, delete data"""
    LT('win -cd "%s";'%book)

def book_rename(newname,workbook=None):
    """rename the currently selected workbook to something (spaces OK)"""
    #TODO: active book
    LT("win -r %s %s;"%(workbook,newname))

def book_toDict(bookName=None):
    """
    given the name of a workbook, return all its contents as a dict.
    if no book name is given, use the active workbook.
    """
    if bookName is None:
        bookName=book_getActive()
    book_select(bookName) #make it active by its name
    book={"name":bookName}
    for sheetNum in range(PyOrigin.Pages(bookName).Layers().GetCount()):
        sheetName=str(PyOrigin.Pages(bookName).Layers(sheetNum))
        sheet_select(sheetName)
        book[sheetName]=sheet_toDict()
    return book

def book_fromDict(bookName="ABFBook"):
    return #TODO:

def book_dictInfo(d):
    """print stats about a workbook dictionary."""
    assert type(d) is dict
    log("workbook dictionary of size %.02f kb"%(sys.getsizeof(d)/1000))
    log(' -- called "%s"'%d["name"])
    log(" -- contains %d sheets:"%(len(d.keys())-1))
    msg=""
    for item in sorted(d.keys()):
        if not item is "name":
            msg+=item+", "
            sheet=item
    if len(msg)>75:
        msg=msg[:75]+"..."
    log(" -- "+msg)
    log(' -- looking closer at sheet "%s" ...'%sheet)
    log(" --- %d rows, %d columns"%(len(d[sheet]["data"]),len(d[sheet]["units"])))
    log(" --- names: %s"%d[sheet]["names"])
    log(" --- units: %s"%d[sheet]["units"])
    log(" --- comments: %s"%d[sheet]["comments"])
    log(" --- data shape: %s"%d[sheet]["data"].shape)

def book_getSheetNames(selectBook=False):
    """return list of sheet names in the current workbook."""
    if selectBook:
        book_select(selectBook)
    names=[]
    for i in range(PyOrigin.ActivePage().Layers().GetCount()):
        names.append(PyOrigin.ActivePage().Layers(i).GetName())
    return names

### SHEET ACTIONS
def sheet_new(sheet):
    """makes the sheet, or selects it if already there."""
    if not sheet in book_getSheetNames():
        LT('newsheet name:="%s" cols:=0 use:=1;'%sheet)
    sheet_select(sheet)

def sheet_delete(title):
    """delete the given sheet in the active book."""
    LT('layer -d "%s";'%title)
    return

def sheet_move(toBook, fromBook=None, fromSheet=None, deleteOldBook=False):
    """
    Move a given worksheet into the given workbook.
    if no fromBook is given, the active book will be used.
    if no fromSheet is given, the active sheet of fromBook will be used.
    if no toSheet is given, it will keep its same name.
    it the toBook doesn't exist, it will be created.
    """
    if fromBook is None:
        fromBook=PyOrigin.ActivePage().GetName()
    book_select(fromBook)
    if fromSheet is None:
        fromSheet=PyOrigin.ActiveLayer().GetName()
    sheet_select(fromSheet)
    sheet_rename("~"+fromSheet)
    log("moving [%s](%s) to [%s](%s)"%(fromBook,fromSheet,toBook,fromSheet),4)
    LT("ExtractByString %s %s 0"%("~"+fromSheet,toBook))
    book_select(toBook)
    LT('layer -d "%s";'%fromSheet)
    sheet_select("~"+fromSheet)
    sheet_rename(fromSheet)
    if deleteOldBook:
        book_close(fromBook)

def sheet_select(sheet=None):
    """select the sheet in the current book. Return False if doesnt exist."""
    if not sheet in book_getSheetNames():
        log("sheet (%s) doesn't exist so I can't select it."%(sheet),4)
        return False
    LT('page.active$ = "%s";'%sheet)
    #redraw() this is slow
    return True

def sheet_getActive():
    """
    returns the name of the active sheet.
    returns Fasle if no sheet is active (well, if no book is active)
    """
    try:
        return PyOrigin.ActivePage().Layers(0).GetName()
    except:
        return False

def sheet_rename(newname):
    """rename the currently selected sheet to something (spaces OK)"""
    LT("wks.name$ = %s;"%newname)

def sheet_addCol():
    """add a column to the current sheet"""
    LT("wks.addCol()")

def sheet_setComment(comment,index=0):
    """set the comments at position [index] of the selected sheet."""
    wks=PyOrigin.ActiveLayer()
    wks.Columns(index).SetComments(comment)
    return

def sheet_fillCol(data=None,index=-1,name="",units="",comments="",
                  coltype="Y",addcol=False):
    """
    fill a column of the the selected worksheet with data.
    If index is 0, the first column will be filled.
    If it's negative, it counts from the end.
    If no data is given, fill it with row numbers.
    if addcol, it'll add a new column for this data (and index is ignored).
    If data is a single number (int or float), all cells will be that number.
    Coltype should be an integer (3 for X, 0 for Y).
        It could be a string "X" or "Y"
    """
    if coltype=="X":
        coltype=3
    if coltype=="Y":
        coltype=0
    if coltype=="":
        coltype=0
    if not type(coltype) == int:
        log("WARNING: column type is not understood.")
    data=np.array(data)
    if addcol:
        sheet_addCol()
        index=-1
    wks=PyOrigin.ActiveLayer()
    if index<0:
        index=wks.GetColCount()+index
    if data is None:
        data=np.arange(len(wks.Columns(0).GetData()))+1
    if "float" in str(type(data)) or "int" in str(type(data)):
        data=[data]*len(wks.Columns(0).GetData())
    wks.Columns(index).SetLongName(name)
    wks.Columns(index).SetUnits(units)
    wks.Columns(index).SetComments(comments)
    wks.Columns(index).SetType(coltype)
    data=data.astype(str)
    data[np.where(data=='nan')]=''
    wks.SetData([data],0,index) #without the [] it makes a row, not a column

def sheet_getColNames():
    """return a list of the long names of each column in a sheet."""
    sheet=PyOrigin.ActiveLayer()
    cols=sheet.GetColCount()
    names=[]
    for x in range(cols):
        names.append(sheet.Columns(x).GetLongName())
    return names

def sheet_getColData(col=0):
    """return [data,colname] from column (index or matching string)"""
    #TODO: make separate functions for data and name/units/comments
    name=""
    if type(col) is str:
        for i,name in enumerate(sheet_getColNames()):
            if col in name:
                log("[%s] matched to column %d (%s)"%(col,i,name),4)
                col=i
                break
    if type(col) is str:
        col=0 #no match found
    sheet=PyOrigin.ActiveLayer()
    data=np.array(sheet.Columns(col).GetData()).astype('U32')
    data[np.where(data=='')]=np.nan
    return data, name

def sheet_toDict(): #works on active sheet
    """
    return a sheet as a dictionary with keys:
        data, names, units, comments, types
    """
    sheet=PyOrigin.ActiveLayer()
    cols=sheet.GetColCount()
    rows=sheet.GetRowCount()
    data=np.empty((rows,cols),dtype=np.float)*np.nan
    names,units,comments,types=[],[],[],[]
    for x in range(cols):
        names.append(sheet.Columns(x).GetLongName())
        units.append(sheet.Columns(x).GetUnits())
        comments.append(sheet.Columns(x).GetComments())
        types.append(sheet.Columns(x).GetType())
        thing=np.array(sheet.Columns(x).GetData()).astype('U32')
        thing[np.where(thing=='')]=np.nan
        data[:len(thing),x]=thing
    while np.all(np.isnan(data[-1])): #trimn off extra rows
        data=data[:-1]
    d={"names":names,"units":units,"comments":comments,"data":data,"types":types}
    return d

def sheet_fromDict(d={},newSheet=False):
    """
    given a worksheet dict (like that from sheet_toDict()) make a worksheet.
    at minimum must have a 2d numpy array in d["data"]
        if newSheet is False, fill active sheet.
        if newSheet is True, make a new unique sheet.
        if newSheet is a string, make that sheet.
    """
    if newSheet is True:
        newSheet=str(time.time())
    if type(newSheet) is str:
        sheet_new(newSheet)
    rows,cols=d["data"].shape
    for key in ['names','units','comments','types']:
        if not key in d.keys():
            d[key]=[""]*cols
    for col in range(len(d["data"][0])):
        sheet_fillCol(data=d["data"][:,col],
                      name=d["names"][col],
                      units=d["units"][col],
                      comments=d["comments"][col],
                      coltype=d["types"][col],
                      addcol=True)






#############################################################################
### WINDOW ACTIONS

def window_minimize():
    """minimize the active window."""
    LT("win -i")

### ORIGIN HIGH LEVEL

def runAfter(script):
    """add commands to be run after this python script exits."""
    tree=PyOrigin.GetTree("PYVALS")
    tree.SetStrValue(script,"runAfter") # this crashes if the string is too long
    log("runAfter loaded with %d characters"%len(script),4)
    if len(script)>5000:
        log(" ^^^ THATS KIND OF A LOT!"%len(script),4)

def redraw():
    """force redraw of the selected graph or workbook"""
    log(" ### WARNING: performing ManualRefresh() which is slow...",4)
    LT('ManualRefresh')
    # PyOrigin.ActivePage().Refresh() # doesn't exist in PyOrigin

def clearProject():
    """clear origin project (with dialog asking about saving)"""
    LT("doc -d")

def getSelectedBookAndSheet():
    """return names of the selected [book,sheet]."""
    book=PyOrigin.ActivePage().GetName()
    sheet=PyOrigin.ActiveLayer().GetName()
    return book,sheet

def sheet_findReplace(find="nan",replace=0):
    """in the currently selected workbook, find/replace."""
    sheet=PyOrigin.ActiveLayer()
    for x in range(sheet.GetColCount()):
        coldata=np.array(sheet.Columns(x).GetData()).astype('U32')
        coldata[np.where(coldata==find)]=replace
        sheet.SetData([coldata],0,x) # [] it makes a column

#############################################################################
### CJFLab Specific

def cjf_getLast():
    """
    Return the most recently created [book,sheet] from pyvals"""
    pyvals=treeToDict(str(PyOrigin.GetTree("pyLastBookSheet".upper())))
    return pyvals["pyNameBookShort"],pyvals["pyNameSheetShort"]

def cjf_marksOn():
    LT("marks on")
def cjf_marksOff():
    LT("marks off")

def cjf_eventsOn():
    """forcably enables event detection."""
    log("turning event detection ON")
    cmd="""if (btnEventDetection.color==1){
    btn_ToggleCJFMiniControls;
    btnEventDetection.color = 2;
    MiniPrep_CheckOtherSettings;
    testmini;}"""
    LT(cmd)

def cjf_eventsOff():
    """forcably disables event detection."""
    log(" -- turning event detection OFF")
    cmd="""
    if (btnEventDetection.color==2) {
        btn_ToggleCJFMiniControls;
        btnEventDetection.color = 1;
        MiniPrep_CheckOtherSettings;
        testmini;
        hideeventmarkers;
    }
    """
    LT(cmd)

def cjf_selectAbfGraph():
    """force the ABFGraph to be selected."""
    LT("win -a ABFGraph")
    #redraw() this is slow

def cjf_selectLast():
    """force active of the last made worksheet."""
    book,sheet=cjf_getLast()
    LT('win -a %s;'%book)
    LT('page.active$ = "%s";'%sheet)

def cjf_setpath(fname):
    fname=os.path.abspath(fname)
    fname=fname.replace("\\","/")
    cmd='setpath "%s" 0;'%fname
    LT(cmd)

def cjf_noteSet(s):
    """set contents of a worksheet note."""
    LT("wksClearNote;")
    LT('wksAddNote "%s";'%(s.replace('"',"'")))

def cjf_noteGet():
    """get contents of a worksheet note."""
    return

def cjf_events_saveEvents(setTo=1):
    """modify minip tree to enable/disable saving of events."""
    cjf_events_set(saveData=1)

def cjf_events_default_GABA():
    """enable event detection with default GABA settings."""
    cjf_events_set(area=60, positive=0, threshold=10, saveData=1, baseline=10,
                   baselineTime=.5, decayTime=30, decayValue=37, localMax=10)

def cjf_events_default_AP():
    """enable event detection with default AP settings."""
    cjf_events_set(area=0, positive=1, threshold=10, saveData=1, baseline=2,
                   baselineTime=.5, decayTime=10, decayValue=5, localMax=5)

def cjf_events_set(area=False,positive=False,threshold=False,saveData=False,
                   baseline=False,baselineTime=False,decayTime=False,
                   decayValue=False,localMax=None):
    """set event detection properties. Set only what you want to change."""
    LT('XML_from_minip("XML_MINIP")')
    tree=PyOrigin.GetTree("XML_MINIP")
    XML=pyOriginXML.OriginXML(tree.GetStrValue("xml"))
    if area: XML.set("GetN.Area",area)
    if positive: XML.set("GetN.Polarity",positive)
    if threshold: XML.set("GetN.Threshold",threshold)
    if saveData: XML.set("GetN.bSaveMarkerData",saveData)
    if baseline: XML.set("GetN.tBaseline",baseline)
    if baselineTime: XML.set("GetN.tBaselineTime",baselineTime)
    if decayTime: XML.set("GetN.tDecayTime",decayTime)
    if decayValue: XML.set("GetN.tDecayValue",decayValue)
    if localMax: XML.set("GetN.tLocalMax",localMax)
    log(XML.thelog)
    tree.FirstChild().NextSibling().SetStrValue(XML.toString()) #TODO: STRONGER
    LT('XML_to_minip("XML_MINIP")')
    LT('del -vs XML_MINIP')
    LT('testmini') # to redraw graph window

def cjf_gs_set(decimateBy=False,phasic=False):
    """set graph settings."""
    LT('XML_from_gs("XML_GS")')
    tree=PyOrigin.GetTree("XML_GS")
    XML=pyOriginXML.OriginXML(tree.GetStrValue("xml"))
    XML.use("phasic/tonic",phasic)
    for key in XML.keys():
        if decimateBy and "bDecimate.dDecBy" in key:
            XML.set(key)
    log(XML.thelog)
    tree.FirstChild().NextSibling().SetStrValue(XML.toString()) #TODO: STRONGER
    LT('XML_to_gs("XML_GS")')
    LT('del -vs XML_GS')

def cjf_GS_update():
    """save existing graph settings, reload, import old settings."""

    # prepare LT editor objects containing tree/xml pairs
    cjf_selectAbfGraph()
    LT('XML_from_gs("XML_OLD")')
    LT('gs default 1')
    cjf_selectAbfGraph()
    LT('XML_from_gs("XML_NEW")')

    # load XML string from an editor object
    tree_old=PyOrigin.GetTree("XML_OLD")
    xml_old=tree_old.GetStrValue("xml")

    # load XML string from an editor object
    tree_new=PyOrigin.GetTree("XML_NEW")
    xml_new=tree_new.GetStrValue("xml")

    # pull values from the old tree into the new tree
    xml_new,thelog=pyOriginXML.updateTree(xml_old,xml_new)
    xml_new=xml_new.replace("MemTests","SCOTTS THING WORKS")
    log(thelog)

    # update the new editor XML
    tree_new.SetStrValue(xml_new,"xml")

    # update graph settings from the XML editor
    LT('XML_to_gs("XML_NEW")')

    # clean up
    LT('del -vs XML_NEW')
    LT('del -vs XML_OLD')



#############################################################################
### COMMON TASKS
# This is really the point of this module.

def collectCols(cols=["command","Freq"],book=None,newBook="collected",
                matching=False):
    """
    assume each sheet is a cell and grab a column (or columns) to combine
    into a new workbook/worksheet. Columns can be in index values (starting
    at 0) or names (for partial match). Columns can be single or multiple
    (for X,Y,Y,Y sets).
    If matching is given, only return data from sheets with that string in it.

    Examples:
        collectCols(3) # move all of the 4th column to a new book
        collectCols([0,3]) # same thing, but for X,Y pairs
        collectCols([0,"Freq"]) # partial string matches also work
        collectCols(["Freq"],matching="_step1") # string matching

    Matching works both ways!
        matching could be something like "_EVN" or a huge string containing
        a list of sheet names like:
            "16711025_16711028, 16711039_16711045, 16718034_16718038..."
        this way you can select all columns from a group by sending it all
        of the group worksheet names.
    """
    if type(cols) is str:
        cols=[cols]
    if book:
        book_select(book)
    book=book_getActive()
    sheets=book_getSheetNames()
    newSheet="%.02f"%time.time()
    book_new(newBook,newSheet)
    data=[]
    for sheet in sheets:
        if matching and not matching in sheet and not sheet in matching:
            continue
        for col in cols:
            book_select(book,sheet) #old book
            data,colName=sheet_getColData(col)
            book_select(newBook,newSheet) #new book
            coltype="Y"
            if len(cols)>1 and col==cols[0]:
                coltype="X"
            sheet_fillCol(data,name=colName,comments=sheet,addcol=True,
                          coltype=coltype)
    return

if __name__=="__main__":
    print("DO NOT RUN THIS")








