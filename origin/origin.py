"""command interpreter to interface SWHLab with origin.

run origin commands like:

 >>> swhcmd test
 >>> swhcmd version
 >>> swhcmd update
 >>> swhcmd help

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
import pylab

#from swhlab.origin import pyOriginXML
from swhlab.origin import task as OR
from swhlab.origin.task import LT
from swhlab.origin.task import log

try:
    import PyOrigin #allows spyder to access PyOrigin documentation
except:
    pass

### DEVELOPMENT COMMANDS

def cmd_getgroup(*args):
    """
    perform stats on certain columns of a large worksheet organized by group.
    groups live in a note called 'groups' in the same folder.
    read the workflow overview document for how to truly use this function.
    this is a groups-aware wrapper for ccave.

    >>> sc getgroup collected sheetName [16711025_16711028, 16711039_16711045,
    16718034_16718038, 16725007_16725012, 16725016_16725020, 16725031_16725035,
    16725045_16725049, 16725059_16725063, 16803031_16803035, 16803052_16803057,
    16803060_16803064, 16803067_16803071]


    """
    abf,cmd,args=args
    print("ABF:",abf)
    print("CMD:",cmd)
    print("ARGS:",args)

def cmd_onex(*args):
    """
    If you have XYXYXYXY keep the first X column but delete all other Xs.
    This is usually called after getcols if all Xs are the same.
    >>> sc onex
    """
    if len(OR.sheet_getColNames())<3:
        log("not reducing xy pairs because there arent many columns",4)
        return
    LT('wreducecols start:=3 skip:=1')

def cmd_groupstats(*args):
    """
    This is a glorified 'getcols' that is group-aware and uses ccave.
    Run this on a workbook where every sheet is a sheet named PARENT_ABF.
    Runs on every sheet of the selected workbook.
    >>> sc groupstats iHold
    """
    abfFile,cmd,args=args
    GET_FROM_BOOK=OR.getSelectedBookAndSheet()[0]
    GET_FROM_COLUMN=args
    log("looking in book: "+GET_FROM_BOOK,4)
    log("Grouping stats from column:"+GET_FROM_COLUMN,4)
    log("I found %d sheets (cells)"%len(OR.book_getSheetNames()),4)

    # get groups from the groups note
    groups=OR.note_to_groups(OR.note_read("groups"))

    # make groups from the sheets we have in the selected workbook
    groups_sheets={} # this will contain all sheets we will work on
    for sheet in OR.book_getSheetNames(GET_FROM_BOOK):
        for group in groups:
            if sheet.split("_")[0] in groups[group]:
                if not group in groups_sheets.keys():
                    groups_sheets[group]=[]
                groups_sheets[group]=groups_sheets[group]+[sheet]

    # generate some commands to do what we want
    script=""
    for group in groups_sheets:
        script+='\n'
        script+='win -a %s;\n'%GET_FROM_BOOK
        script+='sc getcols [%s] %s;\n'%(", ".join(groups_sheets[group]),GET_FROM_COLUMN)
        OR.sheet_delete(group) # go ahead and remove old stuff
        script+="wks.name$ = %s;\n"%group
        script+="ccave;\n"

    script+='sc getcols;\n' #icing on the cake
    script+='win -r collected %d;\n'%time.time() # unique short name
    script+='page.longname$=collected group %s;\n'%GET_FROM_COLUMN # custom short name
    print("SHOULD NAME TO:",GET_FROM_COLUMN)
    script+='type if you can read this, nothing was cut off this script;'
    OR.runAfter(script)

def cmd_checkout(*args):
    cm.checkOut(PyOrigin)

def html_temp_launch(html):
    fname = tempfile.gettempdir()+"/swhlab/temp.html"
    with open(fname,'w') as f:
        f.write(html)
    webbrowser.open(fname)

def cmd_code_pb():
    """demonstrate how to do an interactive progressbar in labtalk."""
    return

def cmd_logtest(*args):
    """
    show how different log levels work from within python.
    It just so happens that the syntax is identical to C (without ;)
    >>> sc logtest
    """
    log("I just set the log level to 10.")
    log("I'm about the clear the screen...")
    log("clear")
    log("I just cleared the screen.")
    log("I'm about to start the log test now")
    log("let's\ntry\na cool\nmultiline\nmessage w00t!")
    log("okay for real now")
    log("here I go")
    log("this is less important",4)
    log("this is\neven\nless important",5)
    log("this is normal")
    log("this is important",2)
    log("this is some more normal")
    log("this is REALLY important",1)
    log("this is worth stopping for",0)
    log("we are all done now")
    log("phew!",4)
    log("Setting log level back to 3")
    log_level(3)
    log("you shouldn't be able to see this",4)

def cmd_GSupdate(*args):
    """
    run this command after updating the tree structure for an ABFGraph.
    It saves the existing values (in XML), reloads the graph with the new
    default tree settings, and imports settings one by one from the old XML.
    >>> sc GSupdate
    """
    OR.cjf_GS_update()

def cmd_extractAP(*args):
    """
    run this command in current clamp mode with markeres centered around an AP.
    >>> sc extractAP
    """
    ID=os.path.basename(args[0].replace(".abf",""))
    OR.cjf_selectAbfGraph()
    OR.LT("if (LBL_Mark1.Show==0) btn_ToggleMarks; bringmarks;")
    m1s=OR.LT_get("mark1.x")/1000
    m2s=OR.LT_get("mark2.x")/1000
    RATE=int(OR.treeToDict(str(PyOrigin.GetTree("PYABF")))["dRate"])
    m1i=int(m1s*RATE)
    m2i=int(m2s*RATE)
    print("extracting from points:",m1i,m2i)

    OR.book_select("ABFBook")
    OR.sheet_select("ABFData")
    data,name=OR.sheet_getColData(1)
    data=data[m1i:m2i].astype(np.float)
    deriv=np.diff(data)*RATE/1000 #because it's mV not V
    data=data[:-1] # to make it match, pluck 1 data point

    # EXTRACT RAW DATA
    OR.book_new("extracted","raw")
    if not len(OR.sheet_getColNames()):
        OR.sheet_fillCol(data=[np.arange(len(data))/RATE],addcol=True,name="time",units="sec",coltype="X")
    OR.sheet_fillCol(data=[data],addcol=True,comments=ID,name="%d-%d"%(m1i,m2i),units="mV")

    # CREATE DV PLOTS
    OR.book_new("extracted","derivative")
    if not len(OR.sheet_getColNames()):
        OR.sheet_fillCol(data=[np.arange(len(deriv))/RATE],addcol=True,name="time",units="sec",coltype="X")
    OR.sheet_fillCol(data=[deriv],addcol=True,comments=ID,name="%d-%d"%(m1i,m2i),units="mV/ms")

    # CREATE PHASE PLOT
    OR.book_new("extracted","phase")
    OR.sheet_fillCol(data=[data],addcol=True,units="mV",coltype="X",comments=ID,name="%d-%d"%(m1i,m2i))
    OR.sheet_fillCol(data=[deriv],addcol=True,units="V/S",comments=ID,name="%d-%d"%(m1i,m2i))


### ACTIONS

def viewContinuous(enable=True):
    OR.cjf_selectAbfGraph()
    if enable:
        LT("iSweepScale=100;plotsweep(1);AutoX;AutoY;")
    else:
        LT("iSweepScale=1;plotsweep(1);AutoX;AutoY;")

def addClamps(abfFile,pointSec=None):
    """
    given a time point (in sec), add a column to the selected worksheet
    that contains the clamp values at that time point.
    """
    #TODO: warn and exit if a worksheet isn't selected.
    #TODO: if OR.notWorksheet(): return
    abf=swhlab.ABF(abfFile)
    if not type(pointSec) in [int,float]:
        pointSec=abf.protoSeqX[1]/abf.rate+.001
    vals=abf.clampValues(pointSec)
    log("determined clamp values: [%s]"%str(vals),5)
    OR.sheet_fillCol([vals],addcol=True, name="command",units=abf.unitsCommand,
                     comments="%d ms"%(pointSec*1000))

##########################################################
### PROCEDURES
# common interactions with cjflab, usually through labtalk

def addSheetNotesFromABF(abfFile):
    """
    get notes from an ABFfile and push them into the selected sheet.
    These notes come from experiment.txt in the abf folder.
    """
    OR.cjf_noteSet(cm.getNotesForABF(abfFile))

def ramp(book,sheet):
    """
    perform AP analysis on a current clamp ramp protocol.
    almost identical to gain()
    """
    #TODO: add function to warn/abort if "EventsEp" worksheet exists.
    OR.book_close("EventsEp") #TODO: lots of these lines can be eliminated now
    OR.book_close("EventsEpbyEve")
    OR.cjf_selectAbfGraph()

    LT("CJFMini;")

    OR.book_select("EventsEp")
    OR.sheet_select()
    OR.sheet_rename(sheet)
    OR.sheet_move(book+"gain")
    cmd_addc(None)
    OR.book_close("EventsEp")

    OR.book_select("EventsEpbyEve")
    OR.sheet_select()
    OR.sheet_rename(sheet)
    OR.sheet_move(book+"aps")

    # make event time experiment time
    LT('col(B)/=1000; col(B)+=col(A)')

    # instantaneous command is needed
    LT('wks.AddCol(pA)')
    LT('copy col(B) col(pA); col(pA)/=100; col(pA)+=10*col(A)')
    LT('wks.col = wks.nCols; wks.col.unit$=pA; wks.col.lname$=command')

    OR.book_close("EventsEpbyEve")

def gain(m1,m2,book,sheet):
    """
    perform a standard AP gain analysis. Marker positions required.
    Optionally give it a sheet name (to rename it to).
    All sheets will IMMEDIATELY be moved out of EventsEp.
    Optionally, give noesFromFile and notes will be populated.
    Note that "Events" worksheets will be deleted, created, and deleted again.
    -- m1 and m2: marker positions (ms)
    -- book/sheet: output workbook/worksheet
    """
    #TODO: add function to warn/abort if "EventsEp" worksheet exists.
    OR.book_close("EventsEp") #TODO: lots of these lines can be eliminated now
    OR.book_close("EventsEpbyEve")
    OR.cjf_selectAbfGraph()

    LT("m1 %f; m2 %f;"%(m1,m2))
    LT("CJFMini;")
    OR.book_select("EventsEp")
    OR.sheet_select() #select the ONLY sheet in the book
    OR.sheet_rename(sheet)
    OR.sheet_move(book)

    OR.book_close("EventsEp")
    OR.book_close("EventsEpbyEve")
    OR.book_select(book)
    cmd_addc(None)

def VCIV(m1,m2,book,sheet):
    """
    perform voltage clamp IV analysis on a range of markers.
    Note that "MarkerStatsEp" worksheets will be deleted.
    -- m1 and m2: marker positions (ms)
    -- book/sheet: output workbook/worksheet
    """
    #TODO: add function to warn/abort if "MarkerStatsEp" worksheet exists.
    OR.cjf_selectAbfGraph()
    LT("m1 %f; m2 %f;"%(m1,m2))
    OR.book_close("MarkerStatsEp")
    LT("getstats;")
    OR.book_select("MarkerStatsEp") #TODO: add command to calculate Rm
    OR.sheet_rename(sheet)
    OR.sheet_move(book, deleteOldBook=True)


##########################################################
# COMMANDS ###############################################
# every command gets ABF filename and command string.

### Experiment text files

def cmd_loadexp(abfFile,cmd,args):
    """
    load experiment text file.
    tries to find experiment.txt in the same folder as the last loaded ABF.
    >>> sc loadexp
    """
    OR.note_new("experiment.txt")
    expFile = os.path.abspath(os.path.dirname(abfFile)+"/experiment.txt")
    if not os.path.exists(expFile):
        print("!! experiment file does not exist:",expFile)
        return
    with open(expFile) as f:
        raw=f.read()
    OR.note_set(raw)

def cmd_groupExp(abfFile,cmd,args):
    """
    add groups to the note window 'groups' from the experiment.txt in the
    same folder as the currently loaded ABF in ABFGraph
    >>> sc groupExp
    """
    expFile = os.path.abspath(os.path.dirname(abfFile)+"/experiment.txt")
    if not os.path.exists(expFile):
        print("!! experiment file does not exist:",expFile)
        return
    with open(expFile) as f:
        raw=f.read().split("\n")
    for line in raw:
        if len(line)<3:
            continue
        if line[0]=="~":
            line=line.replace("\t"," ")
            while "  " in line:
                line=line.replace("  "," ")
            line=line[1:].split(" ")
            group_addParent(line[0],line[1])

def getPythonScriptOutput(script,args=[],showConsole=False):
    """
    launch a python script (optionally without a console window) and
    return the text output.
    """
    #TODO: get absolute python path a CJFLab.ini file or something.
    #if it's not an absolute path, it needs to be set in the PATH variables
    if showConsole:
        pythonProgram="python"
    else:
        pythonProgram="pythonw"
    args=[pythonProgram,script,args]
    process = subprocess.Popen(args, stdout=subprocess.PIPE)
    out, err = process.communicate()
    return out.decode('utf-8')

def cmd_setpaths(abfFile,cmd,args):
    """
    set multiple paths and run sc auto on all of them.
    For now, this can only be run if an ABF is already up. It'll check the
    directory of that abf.
    Preceed this command with 'sc mt' if you want an abf to get you started.
    >>> sc setpaths
    """

    if not abfFile:
        print(" !! an ABF must be loaded frst!")
        return

    # Launch QT gui from within Origin's python instance
    from swhlab.origin import win_abfSelect
    abfs = win_abfSelect.getABFlist(os.path.dirname(abfFile))

    if not len(abfs):
        print(" !! no abfs selected")
        return
    print(" -- selected %d ABFS"%len(abfs))
    OR.cjf_eventsOff()
    OR.cjf_marksOff()

    # create a script to run 'sc auto' on every abf but allow breaking.
    LT('del -al ABFS') # start clean
    LT('StringArray ABFS') # make a string array
    for path in abfs:
        path=os.path.join(os.path.dirname(abfFile),path+".abf")
        LT('ABFS.Add("%s")'%path) # add to the string array
    script="""
    for (ii = 1; ii <= ABFS.GetSize(); ii++){
        	setpath ABFS.GetAt(ii)$;
        	win -a ABFGraph; // raise it
        	ManualRefresh; // redraw it
         sc auto; // do the thing
         sec -p .5; // give time for old progress bars to fade away
         break -b SWHLab analyzing abf $(ii) of $(ABFS.GetSize()); // launch new progressbar
         break -r 1 ABFS.GetSize(); // set scale of progress bar
        	break -p ii; // update progress bar value
         sec -p 1.5; // must come at end of for loop to allow breaking
    }
    break -end;
    """
    OR.runAfter(script) # load it into the runafter spot


def cmd_egg(*args):
    """html demo"""
    html="""
    <h1>&nbsp;&nbsp;SWHLab</h1>
    <h3>&nbsp;&nbsp;Generated: %s</h3>
        <img src="http://swharden.com/tmp/pub/bitmoji_hello.png"
        style="text-align: center; position: absolute; bottom: 0px;">
    """%(time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()))
    html=html.replace('"',"'")
    LT('type -html "%s"'%html)

### group note management
def group_addParent(parentID,group="uncategorized"):
    """
    if the parent isn't already in the group, add a line.
    if the group already exists, add the parent to that group.
    if the group doesn't exist, make the group, and add the parent.
    """
    OR.note_new("groups")
    existing=OR.note_read()
    if len(existing)<3:
        msg="""# ABF GROUPS FILE
        #
        # Lines beginning with # are ignored.
        # The first word of each line is considered the ABF ID of a parent.
        # If the line starts with "GROUP: ", a new group is made and
        #   all ABFs (parent IDs) listed below it belong to that group.
        # Running 'sc auto' adds new parents to this list.
        """.replace("        ","")
        OR.note_append(msg)
    if parentID in existing:
        log("parent %s is already in the groups note"%parentID,4)
    else:
        log("adding %s to the groups note"%parentID,4)
        if not "GROUP: %s"%(group) in existing:
            OR.note_append("\nGROUP: %s"%(group))
        existing=OR.note_read().split("\n")
        for i,line in enumerate(existing):
            if line.strip()=="GROUP: %s"%(group):
                existing[i]=existing[i]+"\n"+parentID
        OR.note_set("\n".join(existing))



### PRE-PROGRAMMED ANALYSIS ROUTINES

def cmd_note(*args):
    print(OR.cjf_noteGet())

def cmd_auto(abfFile,cmd,args):
    """
    automatically analyze the current ABF based on its protocol information.
    protocol comments are how this program knows how to analyze the file.
    >>> sc auto
    >>> sc auto all

    """

    OR.cjf_selectAbfGraph() # you may have to keep doing this!
    parent=cm.getParent(abfFile)
    parentID=os.path.basename(parent).replace(".abf","")
    print("analyzing",abfFile)
    abf=swhlab.ABF(abfFile)
    print("protocol:",abf.protoComment)
    addToGroups=True

    # by default events and markers are set to OFF
    OR.cjf_eventsOff()
    OR.cjf_events_set(saveData=0)
    OR.cjf_marksOff()


    if abf.protoComment.startswith("01-13-"):
        log("looks like a dual gain protocol")
        OR.cjf_eventsOn()
        OR.cjf_events_default_AP()
        gain( 132.44, 658.63,"gain","%s_%s_step1"%(parentID,abf.ID))
        gain(1632.44,2158.63,"gain","%s_%s_step2"%(parentID,abf.ID))

    elif abf.protoComment.startswith("01-01-HP"):
        log("looks like current clamp tau protocol")
        LT("tau")
        OR.book_new("tau","%s_%s"%(parentID,abf.ID))
        tau=OR.LT_get('tauval')
        log(" -- TAU: %s"%tau,4)
        OR.sheet_fillCol([[tau]],addcol=True, name="tau",units="ms")

    elif abf.protoComment.startswith("02-01-MT"):
        log("looks like a memtest protocol") #TODO: event detection?
        OR.book_close("MemTests")
        LT("memtest;")
        OR.book_select("MemTests")
        OR.sheet_rename("%s_%s"%(parentID,abf.ID))
        OR.sheet_move("MT",deleteOldBook=True)

    elif abf.protoComment.startswith("02-02-IV"):
        log("looks like a voltage clamp IV protocol")
        OR.cjf_gs_set(phasic=True)
        VCIV( 900,1050,"IV","%s_%s_step1"%(parentID,abf.ID))
        addClamps(abfFile,.900)
        VCIV(2400,2550,"IV","%s_%s_step2"%(parentID,abf.ID))
        addClamps(abfFile,2.400)

    elif abf.protoComment.startswith("01-11-rampStep"):
        log("looks like a current clamp ramp protocol")
        OR.cjf_eventsOn()
        OR.cjf_events_default_AP()
        OR.cjf_events_set(saveData=1)
        ramp("RAMP","%s_%s"%(parentID,abf.ID))

    elif abf.protoComment.startswith("04-01-MTmon"):
        log("looks like a memtest protocol where drugs are applied")
        OR.cjf_gs_set(phasic=True)
        LT("varTags")
        OR.book_close("MemTests")
        LT("memtest;")
        OR.book_select("MemTests")
        OR.sheet_setComment(OR.LT_get("varTags",True).strip()) #topleft cell
        OR.sheet_rename("%s_%s"%(parentID,abf.ID))
        OR.sheet_move("drugVC",deleteOldBook=True)

    else:
        log("I don't know how to analyze protocol: [%s]"%abf.protoComment,2)
        addToGroups=False

    if addToGroups:
        group_addParent(parentID)

    # clean up
    OR.cjf_eventsOff()
    OR.cjf_marksOff()
    OR.cjf_selectAbfGraph()
    OR.redraw()



##########################################################
### WORKSHEET MANIPULATION

def cmd_pickle(*args):
    """save the selected workbook as a pickled dictionary."""
    LT('dlgSave picklePath ext:=*.pkl title:="Where do you want your pickle?"')
    fname=OR.LT_get('picklePath',True)
    book,sheet=OR.getSelectedBookAndSheet()
    cm.pickle_save(OR.book_toDict(book),fname)
    log("pickle saved as: %s"%fname,2)

def cmd_alignXY(abfFile,cmd,args):
    """
    aligns XYXYXY vetically by similar Xs.
    Run on an active sheet, and it produces new XYYY output sheet.
    >>> sc alignXY
    """
    orig=OR.sheet_toDict()
    data=cm.numpyAlignXY(orig["data"])
    d={} #new workbook dictionary from scratch
    d["data"]=data
    d["names"]=[""]+orig["names"][1::2]
    d["units"]=[""]+orig["units"][1::2]
    d["comments"]=[""]+orig["comments"][1::2]
    d["types"]=["X"]+orig["types"][1::2]
    book,sheet=OR.getSelectedBookAndSheet()
    OR.sheet_fromDict(d,sheet+".aligned")

def cmd_roundX(abfFile,cmd,args):
    """
    finds all X columns and rounds them to the given number.
    creates a new sheet.

    >>> sc roundX 10
    ^^^ will turn an X value of 35 into 30
    """
    try:
        roundto=float(args)
        print("rounding to:",roundto)
    except:
        print("need a argument! see docs.")
        return
    d=OR.sheet_toDict()
    for col,coltype in enumerate(d["types"]):
        if coltype==3: #X column
            values=d["data"][:,col]
            #values=np.array(values/roundto).astype(int)*roundto
            values=np.round(values/roundto)*roundto
            print(values)
            d["data"][:,col]=values
        print(col,coltype)
    book,sheet=OR.getSelectedBookAndSheet()
    OR.sheet_fromDict(d,sheet+".rounded")


def cmd_replace(abfFile,cmd,args):
    """
    finds/replaces all cells in a workbook.

    >>> sc replae nan 0
    ^^^ good for SteadyStateFreq

    >>> sc replace "" 0
    ^^^ this is how you fill blank spaces

    >>> sc replace 0 ""
    ^^^ remove all zeros
    """
    args=args.split(" ")
    if not len(args)==2:
        print("should have 2 arguments. see docs.")
    print(" -- replacing [%s] with [%s]"%(args[0],args[1]))
    OR.sheet_findReplace(args[0],args[1])

def cmd_getcols(abfFile,cmd,args):
    """
    Variant of CJFLab getcols / collectcols.
    Runs on the currently active worksheet.
    Can take column numbers (start at 0) or a string to match in long name.
    For even more options, read the swhlab.origin.tasks.py docs.

    Examples:

        >>> sc getcols * Freq
        ^^^ finds the first column with a name containing "Freq" and puts that
        same column in every worksheet and copies that data into a new sheet
        of a "collected" workbook.
        ^^^ this now automatically generates XY pairs using the first column as X
        would there be a need for 'sc getcols nox Freq'?

        >>> sc getcols _E Freq
        ^^^ same as above, but only return data from sheets with _E in them

        >>> sc getcols * 3
        ^^^ it still works if you give it column numbers (starting at 0)

        >>> sc getcols * 0 Freq
        ^^^ you can use both column numbers and string if you want
        ^^^ giving it two arguments creates XY pairs in the output

        >>> sc getcols * command Freq Area Events
        ^^^ if more items are given, XYYYY sets are made. I doubt this is useful.

    Advanced Scripting:
        This probably should only be used inside scripts, but note that
        matching works both ways! The matching string be something like "_EVN",
        or a huge string containing a list of sheet names like:
            "16711025_16711028, 16711039_16711045, 16718034_16718038..."
        this way you can select all columns from a group by sending it all
        of the group worksheet names. When sending huge strings with spaces
        from labtalk commands, wrap it in [a, b, c] instead of "a, b, c"

        >>> sc getcols [16711025, 16711028, 16711039] iHold
        ^^^ sc commands now allow multiline inputs so this can be 100s of ABFs

    Special Case: accumulating statistics by group
        Running 'sc getcols' on a selected workbook dumps output into a new
        'collected' workbook. Therefore, 'sc getcols' never has any use if it
        is run with the 'collected' workbook selected. A special case is
        therefore called when this happens...
            >>> sc getcols
            - assumes ccave has been run on every sheet of the 'collected' book
            - creates a summary sheet with Y,yEr pairs of all ccave results
            ^^^ this is a HUGE time savings and a major advantage of SWHLab

    """
    CCAVEs=False
    if OR.book_getActive() == "collected" and args=="":
        log("special case usage (see docs): overriding arguments")
        args="* Average SE"
        OR.sheet_delete("_CCAVEs_")
        CCAVEs=True
    if not " " in args or len(args.split(" "))<2:
        print("at least 2 arguments required. read docs!")
        return
    if "[" in args and "]" in args:
        # it contains a huge list. tread carefully.
        args=args.split("] ")
    else:
        # it's a simple argument list
        args=args.split(" ")
    matching,cols=args[0],args[1:]
    if matching == "*":
        matching=False
    for i,val in enumerate(cols):
        try:
            cols[i]=int(val) #turn string integers into integers
        except:
            pass #don't worry if it doesn't work, leave it a string
    OR.collectCols(cols,matching=matching)
    if len(args)==2 and CCAVEs==False:
        log("turning XYXYXY into XYYY")
        cmd_onex(None)
    if CCAVEs:
        OR.sheet_rename("_CCAVEs_")
        log("special case usage (see docs): setting column types")
        wks=PyOrigin.ActiveLayer()
        for col in range(wks.GetColCount()):
            if col%2==0:
                wks.Columns(col).SetType(0) # Y
            else:
                wks.Columns(col).SetType(2) #yEr
    return

def cmd_addc(*args):
    """
    replace column 0 of the selected sheet with command steps.
    This is intended to be used when making IV and AP gain plots.
    args:
        hold: if 'hold' in args will correct command steps to be offset from holding current.

    example:
        * run a memtest or event analysis and make sure a sheet is selected
        >>> sc addc
        >>> sc addc hold
        ^^^ corrects command steps to be offset from holding current.
    """
    LT("abfPathToLT;")
    abfFileName=OR.LT_get('tmpABFPath',True)
    if not len(abfFileName):
        print("active sheet has no metadata.")
        return
    abf=swhlab.ABF(abfFileName)
    vals=abf.clampValues(abf.protoSeqX[1]/abf.rate+.01)
    if "hold" in args:
        vals-=abf.holding
    wks=PyOrigin.ActiveLayer()
    col=wks.Columns(0)
    col.SetLongName("command")
    col.SetUnits(abf.unitsCommand)
    wks.SetData([vals],0,0) #without the [] it makes a row, not a column

def cmd_aps(abfFile,cmd,args):
    """
    Analyze action potentials in the current ABF.
    Output will be 2 worksheets:
        "APs" has info about every AP (AHP, HW, threshold, etc.)
        "APSweeps" has info bout each sweep (average frequency, accomodation, etc.)

    APs Measurements (those ending with I are internal and can be ignored):
        * expT	- time in the experiment the AP occured (in sec). Don't confuse with sweepT.
        * AHP	 - size of the AHP (mV)
        * AHPheight	- actual mV point of the nadir of the AHP
        * AHPreturn	- the point (mV) to which the AHP should return to be counted as AHP half-wdith
        * AHPrisetime - how long it takes to get from threshold to peak (ms)
        * AHPupslope - average slope of the AHP recovery (extrapolated from time it takes to go from peak to the half-point between the AHP and threshold)
        * downslope	 - maximal repolarization velocity (mV/ms)
        * freq	- average instantaneous frequency of APs
        * halfwidth	- time (ms) to cross (twice) the halfwidthPoint
        * halfwidthPoint	 - the point (mV) halfway between threshold and peak
        * height - voltage between threshold and peak (mV)
        * peak	- peak voltage (mV)
        * rate	- sample rate of the amplifier
        * riseTime - how long the AP took to go from threshold to peak
        * sweep	 - sweep number this AP came in
        * sweepT	- time in the sweep of this AP (centered on peak upslope)
        * threshold	- voltage where AP first depolarized beyond 10mV/ms
        * upslope	- peak depolarization velocity (mV/ms)

    AP sweep measurements (those ending with I are internal and can be ignored):
        * commandI - the current step for this sweep
        * accom1Avg - accomodation ratio (first freq / average of all freqs)
        * accom1Steady25 - accomodation ratio (first freq / steady state of last 25%)
        * accom5Avg - accomodation ratio (average of first 5 freqs / average of all freqs)
        * accom5Steady25 - accomodation ratio (average of first 5 freqs / steady state of last 25%)
        * centerBinFrac	- weigt (ratio) of average AP from center (0) to back (1) (binned)
        * centerBinTime	- the time of the average AP (binned)
        * centerFrac - weigt (ratio) of average AP from center (0) to back (1) (from first AP to last)
        * centerTime - the time of the average AP (from first AP to last)
        * freqAvg - average frequency of all APs in sweep
        * freqBin	- binned frequency (# APs / length of step. less accurate.)
        * freqCV - coefficient of variation of AP frequencies (will be lower if regular)
        * freqFirst1 - instanteous frequency of first AP
        * freqFirst5 - average instanteous frequency of first 5 APs
        * freqLast - instanteous frequency of the last AP
        * freqSteady25	 - steady state frequency (average of last 25% of instanteous frequencies)
        * msToFirst	- ms to first AP from the start of the command pulse (not start of sweep!)
        * nAPs - number of APs in this sweep
        * sweep - sweep number

    """
    abf=swhlab.ABF(abfFile)
    swhlab.core.ap.detect(abf)
    swhlab.core.common.matrixToWks(abf.APs,bookName="APs",sheetName=abf.ID,xCol='expT')
    swhlab.core.common.matrixToWks(abf.SAP,bookName="APsweeps",sheetName=abf.ID,xCol='commandI')

### internal tests

def cmd_test_crash(abfFile,cmd,args):
    """
    intentionally crashes.
    """
    print("get ready to go boom!")
    print(1/0)
    print("should be dead.")

### command file paths

def cmd_parent(childPath,cmd,args):
    """
    find the ABF ID of the parent file (.abf with matching .TIF)
    Give this a string (path to an abf) and it will assign it to
    the labtalk variables parentID$ and parentPATH$
        >>> sc parent "C:/some/file/name.abf"
        >>> parentID$=
        >>> parentPATH$=
    """
    if args and os.path.exists(os.path.abspath(args)):
        childPath=os.path.abspath(args)
        folder,childFilename=os.path.split(childPath)
        files=sorted(glob.glob(folder+"/*.*"))
        parent=None
        for fname in files:
            if not fname.endswith(".abf"):
                continue
            if fname.replace(".abf",".TIF") in files:
                parent=fname
            if parent and childFilename in fname:
                parentID=os.path.basename(parent).split(".")[0]
                LTcommand='parentID$="%s";\n'%parentID
                LTcommand+='parentPATH$="%s";'%os.path.abspath(parent)
                LT(LTcommand)
                return parentID
    LTcommand='parentID$="";parentPATH$="";'
    LT(LTcommand)
    return ""

### command distribution

def cmd_docs(abfFile,cmd,args):
    """
    Launch SWHLab website containing details about these scripts.
    For now, it's locally hosted.
    """

    # generate CJFLab documentation
    # TODO: fix this absoute file path madness
    print(" -- generating CJFLab docs by parsing C files...")
    originPath=r"X:\Software\OriginC\On-line\OriginPro 2016"
    from swhlab.origin import CJFdoc as CJFdoc
    CJFdoc.documentOriginCfolder(originPath)
    cjfLabDoc=originPath+"/CJF_doc.html"

    # generate SWHLab documentation
    print(" -- generating SWHLab docs by parsing python files...")
    swhLabDoc = tempfile.gettempdir()+"/swhlab/originDocs.html"
    gendocs(swhLabDoc)

    # launch browser with both docs
    print(" -- launching documentation in browser")
    webbrowser.open(cjfLabDoc)
    webbrowser.open(swhLabDoc)

def cmd_help(abfFile,cmd,matching):
    """
    Display a list of commands available to use.
    Given a partial string will show only functions matching.

    example usage:

        >>> sc help
            ^^^ this will show all available commands

        >>> sc help test
            ^^^ this will show all commands starting with "help"
    """
    commands,docs,code=availableCommands(True)
    print(" -- available commands:")
    for c in commands:
        if matching:
            if not matching in c:
                continue
        cmd=c.replace("cmd_",'')
        print("     ",cmd)
    return

def cmd_path(abfFile,cmd,args):
    """
    shows the path of the SWHLab distribution being used
    """
    print("SWHLab version:",swhlab.VERSION)
    print(swhlab.LOCALPATH)

def cmd_echo(*args):
    """
    run this to enable/disable verbose labtalk echoing.
    It's good for troubleshooting, but gets in the way most of the time.
    >>> sc echo
    """
    log("OLD log level: %s"%OR.log_level())
    if OR.log_level()==3:
        OR.log_level(10)
    else:
        OR.log_level(3)
    log("NEW log level: %s"%OR.log_level())
    if OR.log_level()>3:
        log("### DEBUG MODE ENABLED ###")
    else:
        log("--- REGULAR LOG MODE ---")



def cmd_run(run,cmd,args):
    """
    run a file from the X drive using a short command.
    Files live in: X:\Software\OriginC\On-line\python
    Call them by their file name (without .py)
    >>> sc run test
    ^^^ (this will run X:\Software\OriginC\On-line\python\test.py)

    Also try the 'sc edit' command.
    """
    runThis=False
    if args:
        trypath=r"X:\Software\OriginC\On-line\python/"+args+".py"
        if os.path.exists(trypath):
            print(" -- running",os.path.abspath(trypath))
            runThis=trypath
        else:
            print(" -- doesn't exist:",os.path.abspath(trypath))

    if runThis:
        try:
            sys.path.append(os.path.dirname(runThis))
            imp.load_source('tempModule',runThis)
        except:
            print("CRASHED")
            print(traceback.format_exc())
        print(" -- code finished running!")

    else:
        print(r" -- Python scripts available in: X:\Software\OriginC\On-line\python")
        for fname in sorted(glob.glob(r"X:\Software\OriginC\On-line\python\*.py")):
            print("    - ",os.path.basename(fname).replace(".py",''))

def cmd_edit(run,cmd,args):
    """
    Edit a file from the X drive using a short command.
    Files live in: X:\Software\OriginC\On-line\python
    Call them by their file name (without .py)
    >>> sc edit test
    ^^^ this will edit X:\Software\OriginC\On-line\python\test.py
    ^^^ If the file doesn't exist, it will be created

    Also try the 'sc run' command.
    """
    trypath=r"X:\Software\OriginC\On-line\python/"+args+".py"
    trypath=os.path.abspath(trypath)
    #cmd='notepad "%s"'%(trypath)
    subprocess.Popen(['notepad',trypath])


def cmd_site(abfFile,cmd,args):
    """
    Launch SWHLab website
    """
    webbrowser.open("http://swhlab.swharden.com")

def cmd_update(abfFile,cmd,args):
    """
    See if SWHLab is up to date. If not, offer to upgrade.
    """
    if "force" in args:
        print(" -- forcing an update.")
        swhlab.version.check(True)
    else:
        print(" -- you can force an update with 'sc update force' ")
        swhlab.version.check()

def cmd_version(abfFile,cmd,args):
    """
    reports the current SWHLab distribution version.
    """
    print("SWHLab version:",swhlab.VERSION)

### setting up ABFs

def cmd_gain(abfFile,cmd,args):
    """
    load a representative gain function.
    Optionally give it a number to load a different ABF.
    >>> sc gain
    >>> sc gain 3
    """
    basedir=r"X:\Data\2P01\2016\2016-07-11 PIR TR IHC"
    filenames="""16711015,16711016,16711033,16711048,16718019,16718020,
    16718029,16718030,16803025,16803026,16803061,16803062
    """.replace(" ","").replace("\n","").split(",")
    for i,fname in enumerate(filenames):
        filenames[i]=os.path.abspath(os.path.join(basedir,fname+".abf"))
    try:
        i=min(int(args)-1,len(filenames))
    except:
        i=0
    log("setting preprogrammed ABF %d of %d"%(i+1,len(filenames)+1))
    OR.cjf_setpath(filenames[i])
    OR.book_setHidden("ABFBook")
    LT("plotsweep -1")
    LT("AutoY")

    OR.cjf_eventsOn() # enable events
    OR.cjf_events_default_AP() # load with default AP settings
    OR.cjf_events_set(saveData=1) # demo how to set only one thing


def cmd_tau(abfFile,cmd,args):
    """
    load a representative tau ABF.
    Optionally give it a number to load a different ABF.
    >>> sc tau
    >>> sc tau 3
    """

    basedir=r"X:\Data\2P01\2016\2016-07-11 PIR TR IHC"
    filenames="""16711026,16711051,16725034,16725048,16722032,
    16722025,16722018,16722003
    """.replace(" ","").replace("\n","").split(",")
    for i,fname in enumerate(filenames):
        filenames[i]=os.path.abspath(os.path.join(basedir,fname+".abf"))
    try:
        i=min(int(args)-1,len(filenames))
    except:
        i=0
    log("setting preprogrammed ABF %d of %d"%(i+1,len(filenames)+1))
    OR.cjf_setpath(filenames[i])
    OR.book_setHidden("ABFBook")

def cmd_iv(abfFile,cmd,args):
    """
    load a representative voltage clamp IV ABF.
    Optionally give it a number to load a different ABF.
    >>> sc iv
    >>> sc iv 3
    """

    basedir=r"X:\Data\2P01\2016\2016-07-11 PIR TR IHC"
    filenames="""16725005,16725013,16725021,16725029,16725036,16725043,
    16725050,16725057
    """.replace(" ","").replace("\n","").split(",")
    for i,fname in enumerate(filenames):
        filenames[i]=os.path.abspath(os.path.join(basedir,fname+".abf"))
    try:
        i=min(int(args)-1,len(filenames))
    except:
        i=0
    log("setting preprogrammed ABF %d of %d"%(i+1,len(filenames)+1))
    OR.cjf_setpath(filenames[i])
    OR.book_setHidden("ABFBook")

def cmd_mt(abfFile,cmd,args):
    """
    load a representative 20 sweep memtest.
    Optionally give it a number to load a different ABF.
    >>> sc mt
    >>> sc mt 3
    """

    basedir=r"X:\Data\2P01\2016\2016-07-11 PIR TR IHC"
    filenames="""16725004,16725012,16725020,16725028,16725035,16725042,
    16725049,16725056
    """.replace(" ","").replace("\n","").split(",")
    for i,fname in enumerate(filenames):
        filenames[i]=os.path.abspath(os.path.join(basedir,fname+".abf"))
    try:
        i=min(int(args)-1,len(filenames))
    except:
        i=0
    log("setting preprogrammed ABF %d of %d"%(i+1,len(filenames)+1))
    OR.cjf_setpath(filenames[i])
    OR.book_setHidden("ABFBook")


def cmd_ramp(abfFile,cmd,args):
    """
    load a representative current clamp ramp used for AP inspection.
    Optionally give it a number to load a different ABF.
    >>> sc ramp
    >>> sc ramp 3
    """

    basedir=r"X:\Data\2P01\2016\2016-07-11 PIR TR IHC"
    filenames="""16725000,16725007,16725016,16725023,16725031,16725038,
    16725045,16725052,16725058,16725059
    """.replace(" ","").replace("\n","").split(",")
    for i,fname in enumerate(filenames):
        filenames[i]=os.path.abspath(os.path.join(basedir,fname+".abf"))
    try:
        i=min(int(args)-1,len(filenames))
    except:
        i=0
    log("setting preprogrammed ABF %d of %d"%(i+1,len(filenames)+1))
    OR.cjf_setpath(filenames[i])
    OR.book_setHidden("ABFBook")
    #viewContinuous(True)

def cmd_drug(abfFile,cmd,args):
    """
    load a representative drug application (VC mode, repeated memtest).
    Optionally give it a number to load a different ABF.
    >>> sc drug
    >>> sc drug 3
    """

    basedir=r"X:\Data\2P01\2016\2016-07-11 PIR TR IHC"
    filenames="""16711024,16711038,16711054,16718025,16718033,
    16711030,16711046,16718040,16718007,16718014
    """.replace(" ","").replace("\n","").split(",")
    for i,fname in enumerate(filenames):
        filenames[i]=os.path.abspath(os.path.join(basedir,fname+".abf"))
    try:
        i=min(int(args)-1,len(filenames))
    except:
        i=0
    log("setting preprogrammed ABF %d of %d"%(i+1,len(filenames)+1))
    OR.cjf_setpath(filenames[i])
    OR.book_setHidden("ABFBook")



### code snippets that demonstrate python/origin interactions

def cmd_sweep(abfFile,cmd,args):
    """
    display current ABF in sweep view (opposite of continuous)
    >>> sc sweep
    (see sister function, 'continuous')
    """
    viewContinuous(False)

def cmd_continuous(abfFile,cmd,args):
    """
    display current ABF as a continuous trace. This could be slow.
    >>> sc continuous
    (see sister function, 'sweep')
    """
    viewContinuous(True)

def cmd_redraw(abfFile,cmd,args):
    """
    forces redrawing of the active window.
    >>> redraw
    """
    OR.redraw()

def cmd_move(abfFile,cmd,args):
    """
    move the currently selected sheet to the given workbook.
    Just takes inputs and feeds them to OR.sheet_move()

    simple example:
        >>> sc move newBook
        ^^^ move the selected sheet into newBook

    full functionality example:
        >>> sc move newBook oldBook oldSheet newSheet
        ^^^ If [oldBook]oldSheet exists, move it to [newBook]newSheet
    """
    args=args.split(" ")
    args=args+[None]*4
    if len(args)<3:
        print("not enough arguments. see docs.")
    else:
        OR.sheet_move(args[0],args[1],args[2])
    return

def cmd_treeshow(abfFile,cmd,args):
    """
    display any origin tree object. Only

    example:
        >>> sc treeshow pyvals
        >>> sc treeshow pynotes
    """
    args=args.strip().upper()
    print(str(PyOrigin.GetTree(args)))

#def cmd_pyvals(abfFile,cmd,args):
#    """shows data from the last ABFGraph tree."""
#    LT("CJFDataTopyVals;")
#    pyvals=OR.treeToDict(str(PyOrigin.GetTree("PYVALS")),verbose=True)
#    print("pyvals has %d master keys"%len(pyvals))

######################################################
### documentation

def gendocs(docPath):
    """read this file, make docs, save as local webpage."""
    commands,docs,code=availableCommands(True)
    html="""<html><style>
    body{font-family: Verdana, Geneva, sans-serif;line-height: 150%;}
    a {color: blue; text-decoration: none;}
    a:visited {color: blue;}
    a:hover {text-decoration: underline;}
    .cmd{font-size: 150%; font-weight: bold; border: solid 1px #CCCCCC;
         padding-left:5px;padding-right:5px;background-color:#EEEEEE;}
    .example {color: green;font-family: monospace; padding-left:30px;}
    .star {color: blue;font-family: monospace; padding-left:30px;}
    .tip{font-style: italic; padding-left:60px;font-family: Georgia;color:#6666FF;}
    .doc{font-family: Georgia, serif;padding-left:20px;}
    </style><body>"""
    html+="<h1>SWHLab Command Reference</h1>"
    for command in sorted(commands):
        html+='<a href="#%s">%s</a>, '%(command,command.replace("cmd_",""))
    html=html[:-2] #remove trailing comma
    html+="<hr>"
    for command in sorted(commands):
        html+='<a name="%s"></a>'%command
        html+='<code class="cmd">%s</code><br>'%command.replace("cmd_","sc ")
        d=docs[command].replace("<","&lt;").replace(">","&gt;")
        d=d.strip().split("\n")
        for line in d:
            if "&gt;&gt;&gt;" in line:
                html+='<code class="example">%s</code>'%line
            elif "^^^" in line:
                html+='<code class="tip">%s</code>'%line.replace("^^^",'&#9757;')
            elif len(line.strip()) and line.strip()[0]=="*":
                html+='<code class="star">%s</code>'%line.strip()[1:]
            else:
                html+='<span class="doc">%s</span>'%line
            html+="<br>"
        html+="<br><br>"
    html+="</body></html>"
    with open(docPath,'w') as f:
        f.write(html)

### command parsing

def availableCommands(commentsAndCode=False):
    """return a list of commands (and attach the function)."""
    commands=[]
    code={}
    docs={}
    for item in globals():
        if 'function' in str(type(globals()[item])):
            if item.startswith("cmd_"):
                commands.append(item)
    if commentsAndCode==False:
        return sorted(commands)
    with open(os.path.realpath(__file__)) as f:
        raw=f.read()
    for func in raw.split("\ndef ")[1:]:
        funcname=func.split("\n")[0].split("(")[0]
        if not funcname.startswith("cmd_"):
            continue
        code[funcname]=func
        doc=' *** (no docs for this)'
        if len(func.split('"""'))>2:
            doc=func.split('"""')[1]
        docs[funcname]=doc
    return sorted(commands),docs,code

def swhcmd(abfFile,cmd):
    """this is called directly by origin."""
    OR.LT("pyABF_update") # populate pyABF labtalk tree with abf data
    #print(OR.treeToDict(str(PyOrigin.GetTree("PYABF")),verbose=True))
    cmd=cmd.replace("\n"," ").strip()
    if " " in cmd:
        cmd,args=cmd.split(" ",1)
    else:
        cmd,args=cmd,''
    if len(abfFile)<3:
        abfFile=None
    if cmd == '':
        print("""
        DEBUGGING:
            type 'sc echo' to enable/disable verbose mode

        DOCUMENTATION:
            Type 'sc help' for a list of commands.
            Type 'sc docs' to learn how to use them.

        """)
    else:
        cmd="cmd_"+cmd
        if cmd in availableCommands():
            log("calling python function: %s()"%(cmd),4)
            log("sending ABF: %s"%abfFile,4)
            log("sending args: [%s]"%args,4)
            try:
                globals()[cmd](abfFile,cmd,args)
            except:
                log("sc command terminated unexpectedly.\n"+\
                    " use 'sc docs' to review command usage.\n"
                    " use 'sc echo' to enable/disable debug mode.",1)
                log("#"*10+" TRACEBACK "+"#"*10,4)
                log(traceback.format_exc(),4)
                log("#"*50,4)
        else:
            #print(" -- %s() doesn't exist!"%cmd)
            print()
            print(' -- The command "%s" does not do anything.'%cmd.replace("cmd_",''))
            print(' -- here are some ideas starting with %s...'%cmd.replace("cmd_",''))
            cmd_help(None,None,cmd)
            print(' -- run "sc docs" for a info on how to use every command.')

if __name__=="__main__":
    print("DO NOT RUN THIS")