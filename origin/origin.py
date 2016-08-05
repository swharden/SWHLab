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

from swhlab.origin import task as OR
from swhlab.origin.task import LT

try:
    import PyOrigin #will work in spyder
except:
    pass

# DEVELOPMENT COMMANDS

def cmd_checkout(abfFile,cmd,args):
    cm.checkOut(PyOrigin)

def cmd_test(abfFile,cmd,args):
    OR.note_new("program")
    OR.note_set("wow,\ncool story scott!")
    OR.note_append("I know, right?")
    print(OR.note_read())


##########################################################
### PROCEDURES
# common interactions with cjflab, usually through labtalk

def gain(m1,m2,book="gain",sheet=None,notesFromFile=False):
    """
    perform a standard AP gain analysis. Marker positions required.
    Optionally give it a sheet name (to rename it to).
    All sheets will IMMEDIATELY be moved out of EventsEp.
    Optionally, give noesFromFile and notes will be populated.
    """
    OR.book_close("EventsEp")
    OR.book_close("EventsEpbyEve")
    OR.cjf_selectAbfGraph()

    LT("m1 %f; m2 %f;"%(m1,m2))
    LT("CJFMini;")
    OR.book_select("EventsEp")
    if sheet:
        OR.sheet_select() #select the ONLY sheet in the book
        OR.sheet_rename(sheet)
    if notesFromFile:
        OR.cjf_noteSet(cm.getNotesForABF(notesFromFile))
    OR.sheet_move(book)

    OR.book_close("EventsEp")
    OR.book_close("EventsEpbyEve")
    OR.book_select(book)
    #LT("sc addc")
    cmd_addc(None,None,None)

##########################################################
# COMMANDS ###############################################
# every command gets ABF filename and command string.

### PRE-PROGRAMMED ANALYSIS ROUTINES

def cmd_note(abfFile,cmd,args):
    print(OR.cjf_noteGet())

def cmd_auto(abfFile,cmd,args):
    parent=cm.getParent(abfFile)
    parentID=os.path.basename(parent).replace(".abf","")
    print("analyzing",abfFile)
    abf=swhlab.ABF(abfFile)
    print("protocol:",abf.protoComment)
    if abf.protoComment.startswith("01-13-"):
        print("looks like a dual gain protocol")
        gain( 132.44, 658.63,"gain",sheet="%s_%s_step1"%(parentID,abf.ID))
        gain(1632.44,2158.63,"gain",sheet="%s_%s_step2"%(parentID,abf.ID))
    elif abf.protoComment.startswith("01-01-HP"):
        print("looks like current clamp tau protocol")
        LT("tau")
        OR.book_new("tau","%s_%s"%(parentID,abf.ID))
        tau=float(PyOrigin.LT_get_var("TAUVAL")) #MUST BE ALL CAPS
        OR.sheet_fillCol([tau],name="tau",units="ms",addcol=True)
    elif abf.protoComment.startswith("02-01-MT"):
        print("looks like a memtest protocol")
        OR.book_close("MemTests")
        LT("memtest;")
        OR.book_select("MemTests")
        OR.sheet_rename("%s_%s"%(parentID,abf.ID))
        OR.sheet_move("MT",deleteOldBook=True)
    else:
        print("I don't know what this protocol is!")
    OR.book_select("ABFBook")
    OR.window_minimize()
    #OR.book_close("Book1")
    #OR.cjf_selectAbfGraph()

##########################################################
### WORKSHEET MANIPULATION

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

        >>> sc getcols _E Freq
        ^^^ same as above, but only return data from sheets with _E in them

        >>> sc getcols * 3
        ^^^ it still works if you give it column numbers (starting at 0)

        >>> sc getcols * 0 Freq
        ^^^ you can use both column numbers and string if you want
        ^^^ giving it two arguments creates XY pairs in the output

        >>> sc getcols * command Freq Area Events
        ^^^ if more items are given, XYYYY sets are made. I doubt this is useful.
    """
    if OR.book_getActive() == "collected":
        print("you can't run getcols on the collected worksheet!")
        return
    if not " " in args or len(args.split(" "))<2:
        print("at least 2 arguments required. read docs!")
        return
    args=args.split(" ")
    matching,cols=args[0],args[1:]
    if matching == "*":
        matching=False
    print("COLS:",cols)
    for i,val in enumerate(cols):
        try:
            cols[i]=int(val) #turn string integers into integers
        except:
            pass #don't worry if it doesn't work, leave it a string
    OR.collectCols(cols,matching=matching)
    return

def cmd_addc(abfFile,cmd,args):
    """
    replace column 0 of the selected sheet with command steps.
    This is intended to be used when making IV and AP gain plots.

    example:
        * run a memtest or event analysis and make sure a sheet is selected
        >>> sc addc
    """
    LT("abfPathToLT;")
    abfFileName=PyOrigin.LT_get_str("tmpABFPath$")
    if not len(abfFileName):
        print("active sheet has no metadata.")
        return
    abf=swhlab.ABF(abfFileName)
    vals=abf.clampValues(abf.protoSeqX[1]/abf.rate+.01)
    wks=PyOrigin.ActiveLayer()
    col=wks.Columns(0)
    col.SetLongName("command")
    col.SetUnits(abf.unitsCommand)
    wks.SetData([vals],0,0) #without the [] it makes a row, not a column


### action potentials

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
    docPath = tempfile.gettempdir()+"/swhlab/originDocs.html"
    gendocs(docPath)
    webbrowser.open(docPath)

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
        swhlab.version.update()
    else:
        print(" -- you can force an update with 'sc update force' ")
        swhlab.version.check()

def cmd_version(abfFile,cmd,args):
    """
    reports the current SWHLab distribution version.
    """
    print("SWHLab version:",swhlab.VERSION)

### setting up ABFs
def cmd_fsi(abfFile,cmd,args):
    """
    load a representative FSI gain function. Optionally give it a number.
    >>> sc fsi
    >>> sc fsi 3
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
    print("setting preprogrammed ABF %d of %d"%(i+1,len(filenames)+1))
    LT(r'setpath "%s"'%filenames[i])
    OR.book_setHidden("ABFBook")
    LT("plotsweep -1")
    LT("AutoY")
    print("now enable event detection and hit AP mode")

def cmd_tau(abfFile,cmd,args):
    """
    load a representative FSI tau ABF.
    Optionally give it a number to load a different tau.
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
    print("setting preprogrammed ABF %d of %d"%(i+1,len(filenames)+1))
    LT(r'setpath "%s"'%filenames[i])
    OR.book_setHidden("ABFBook")

def cmd_iv(abfFile,cmd,args):
    """
    load a representative voltage clamp IV ABF.
    Optionally give it a number to load a different tau.
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
    print("setting preprogrammed ABF %d of %d"%(i+1,len(filenames)+1))
    LT(r'setpath "%s"'%filenames[i])
    OR.book_setHidden("ABFBook")

### code snippits that demonstrate python/origin interactions

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

def cmd_pyvals(abfFile,cmd,args):
    """shows data from the last ABFGraph tree."""
    LT("CJFDataTopyVals;")
    pyvals=OR.treeToDict(str(PyOrigin.GetTree("PYVALS")),verbose=True)
    print("pyvals has %d master keys"%len(pyvals))

######################################################
### documentation

def gendocs(docPath):
    """read this file, make docs, save as local webpage."""
    commands,docs,code=availableCommands(True)
    html="""<html><style>
    body{font-family: Verdana, Geneva, sans-serif;
    line-height: 150%;
    }
    .cmd{font-size: 150%; font-weight: bold; border: solid 1px #CCCCCC;
         padding-left:5px;padding-right:5px;background-color:#EEEEEE;}
    .example {color: green;font-family: monospace; padding-left:30px;}
    .star {color: blue;font-family: monospace; padding-left:30px;}
    .tip{font-style: italic; padding-left:60px;font-family: Georgia;color:#6666FF;}
    .doc{font-family: Georgia, serif;padding-left:20px;}
    </style><body>"""
    html+="<h1>CJFLab / SWHLab Commands</h1>"
    for command in sorted(commands):
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
    cmd=cmd.strip()
    if " " in cmd:
        cmd,args=cmd.split(" ",1)
    else:
        cmd,args=cmd,''
    if len(abfFile)<3:
        abfFile=None
    if cmd == '':
        print("""
        Documentation exists at http://swhlab.swharden.com
        Type 'sc help' for a list of commands.
        Type 'sc docs' to learn how to use them.
        """)
    else:
        cmd="cmd_"+cmd
        if cmd in availableCommands():
            globals()[cmd](abfFile,cmd,args)
        else:
            #print(" -- %s() doesn't exist!"%cmd)
            print()
            print(' -- The command "%s" does not do anything.'%cmd.replace("cmd_",''))
            print(' -- here are some ideas starting with %s...'%cmd.replace("cmd_",''))
            cmd_help(None,None,cmd)
            print(' -- run "sc docs" for a info on how to use every command.')


if __name__=="__main__":
    print("DO NOT RUN THIS")