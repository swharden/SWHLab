# -*- coding: utf-8 -*-
"""
Python GitGub Downloader (PGHD)
Created by Scott Harden (www.SWHarden.com)

This python 3 script is intended to make it easy to maintain an active project
on a local computer, and periodically check it against the version hosted
at github.com. If a newer version (with releases newer than the local version)
is seen, it downloads the online copy, and extracts it where the local one used
to be. It probably goes without saying that this script should live outside
the project folder!

Advantages of this method:
    -- uses only standard python libraries
    -- do not have to have a git client installed on the system
    -- works natively on every OS
    -- only requires a single python file
    -- works for any github reposatory with *releases* (not commits)

Note that the default action during an upgrade is to rename the old project
folder from something to something.old.timestamp. If you edit the code
and set "deleteOldFolder=True" it will then delete/replace the project folder
by defult during an upgrade.
"""

### CUSTOMIZE THIS ###########################################################
# If you don't want to launch this script from a command line, set your
# project source and destination here, then run this script however you want.
GIT_PROJECT="https://github.com/swharden/SWHLab"
LOCAL_PATH=r"C:\temp\swhlab"
# you'll have to uncomment 'update()' near the very end of the script.
##############################################################################

import urllib
import urllib.request
import dateutil
import dateutil.parser
import os
import glob
import tkinter
import tkinter.messagebox
import zipfile
import time
import shutil
import sys

def askYesNo(question="did you forget the argument?"):
    """launch a TK window and get a yes/no answer."""
    root = tkinter.Tk()
    root.attributes("-topmost", True) #always on top
    root.withdraw() #hide tk window
    result=tkinter.messagebox.askyesno(os.path.basename(GIT_PROJECT),question)
    root.destroy()
    return result

def getLocalReleaseDate():
    """determine the date of the local copy by looking at file time."""
    files=glob.glob(LOCAL_PATH+"/*.*")
    if len(files)==0:
        return 0
    return int(os.path.getmtime(files[0]))

def getLatestReleaseDate():
    """determine the date of the latest GitHub release by parsing the HTML."""
    url=GIT_PROJECT+"/releases"
    html=downloadText(url)
    for line in html.split(r"\n"):
        if "<relative-time datetime" in line:
            line=line.strip().split('"')[1]
            return int(dateutil.parser.parse(line).timestamp())
    print("NO RELEASES FOUND!")
    return False

def downloadText(url):
    """get text from a URL."""
    return str(urllib.request.urlopen(url).read())

def downloadSave(url,saveAs):
    """save a (binary) file from the web to disk."""
    urllib.request.urlretrieve(url, saveAs)

def updateNeeded():
    """return True if the GitHub release is later than the local one."""
    stampNet=getLatestReleaseDate()
    stampLocal=getLocalReleaseDate()
    diffDays=abs(stampNet-stampLocal)/60/60/24
    if stampNet>stampLocal:
        print("UPDATE REQUIRED")
        print("GitHub has a release %.03f days newer than yours"%diffDays)
        return True
    else:
        print("You're up to date!")
        print("Your version is %.03f days newer than GitHub"%diffDays)
        return False

def unzip(outPath,zipFname):
    """extract a zip file to a given folder."""
    zip_ref = zipfile.ZipFile(zipFname, 'r')
    zip_ref.extractall(outPath)
    zip_ref.close()

def update(forceUpdate=False,deleteOldFolder=False):
    """replace local software folder it with the latest internet release."""
    global GIT_PROJECT
    global LOCAL_PATH
    ## clean up file paths
    if not "http" in GIT_PROJECT:
        GIT_PROJECT="https://github.com/"+GIT_PROJECT
    if LOCAL_PATH[-1] in "\\/":
        LOCAL_PATH=LOCAL_PATH[:-1]
    if GIT_PROJECT[-1] in "\\/":
        GIT_PROJECT=GIT_PROJECT[:-1]

    if not os.path.exists(LOCAL_PATH):
        print("creating",LOCAL_PATH)
        os.makedirs(LOCAL_PATH)

    if updateNeeded() or forceUpdate:
        msg="A new release of %s is available!"%(os.path.basename(GIT_PROJECT))
        msg+="\nDo you want to update now?"
        if not askYesNo(msg):
            print("update not desired. exiting!")
            return
        else:
            print("proceeding with update...")
    else:
        print("update not needed. exiting!")
        return
    # step 0: determine our URL to get from and our local path to save to
    url=GIT_PROJECT+"/archive/master.zip"
    zipFname=os.path.join(os.path.dirname(LOCAL_PATH),
                          os.path.basename(LOCAL_PATH+".zip"))


    # step 1: delete old folder (or rename it to something old)
    if os.path.exists(LOCAL_PATH):
        if deleteOldFolder:
            print("-- deleting",LOCAL_PATH)
            os.rmdir(LOCAL_PATH)
        else:
            oldFolder=LOCAL_PATH+".old.%d"%time.time()
            print("-- renaming to",oldFolder)
            os.rename(LOCAL_PATH,oldFolder)

    # step 2: download zip to folder

    print("-- downloading:",url)
    print("-- saving as:",zipFname)
    downloadSave(url,zipFname)
    print("-- download complete")

    # step 3: extract zip into folder then delete the zip
    zipTo=LOCAL_PATH+".new"
    print("-- extracting to:",zipTo)
    unzip(zipTo,zipFname)
    source=glob.glob(zipTo+"/*master")[0]
    print("-- moving",source)
    os.rename(source,LOCAL_PATH.lower()) # rename SWHLab to swhlab to make importing easier
    print("-- deleting",zipTo)
    shutil.rmtree(zipTo)
    print("-- deleting",zipFname)
    os.remove(zipFname)
    print("UPDATE COMPLETE!")

if __name__=="__main__":

    ### uncomment one of lines to allow standalone operation ###
    #update(True) #set True to force an update.
    update() #leave blank to only update if a newer version is available

    ### this section is for command line operation
#    if not len(sys.argv)==3:
#        print("improper number of arguments! See README file for details.")
#        print("arguments are github user/project and destination path.")
#        print("I expect input like this (mind your slashes):")
#        print("python pghd.py swharden/swhlab c:/my/project/destination")
#    else:
#        _,GIT_PROJECT,LOCAL_PATH=sys.argv
#        LOCAL_PATH=os.path.abspath(LOCAL_PATH)
#        print("checking project:",GIT_PROJECT)
#        print("against local copy:",LOCAL_PATH)
#        update()
