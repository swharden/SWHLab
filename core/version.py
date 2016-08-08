"""
SWHLab versioning routines. Autoamtic updating, etc.
Current versions are in:
    http://www.swharden.com/software/swhlab/versions/

TODO: roll in distribution tasks here.
    -- document generation
    -- demo code
    -- cookbook
"""

import os
import sys
import time
import ftplib
import zipfile
import glob
import webbrowser
import threading
import imp
import shutil
import subprocess

import swhlab
cm=swhlab.core.common

def zipdir(pathToZip, zipFname):
    """
    add all contents of a folder into a zip file.
    certain rules allow exclusion of particular folders and files.
    """
    pathToZip=os.path.abspath(pathToZip)
    zipf = zipfile.ZipFile(zipFname, 'w', zipfile.ZIP_DEFLATED)
    print(" -- creating",zipFname)
    for root, dirs, files in os.walk(pathToZip):
        if '/abfs/' in root.replace("\\","/")+"/":
            continue
        for file in files:
            if file.endswith(".pyc"):
                continue
            print("      compressing %s"%file)
            fullPath=os.path.join(root, file)
            shortPath=fullPath.replace(pathToZip,'')
            zipf.write(fullPath,shortPath)

def unzip(outPath,zipFname):
    """extract a zip file to a given folder."""
    zip_ref = zipfile.ZipFile(zipFname, 'r')
    zip_ref.extractall(outPath)
    zip_ref.close()

def upload(fname):
    """upload the recently zipped version."""
    ftpobj=cm.ftp_login("/swhlab/versions")
    if ftpobj:
        cm.ftp_upload(ftpobj,fname)
        ftpobj.quit()
        return True
    return False

def warnIfNewer():
    """first make sure we aren't trying to distribute an old copy"""
    if check(popup=False):
        print(" -- This version matches that online.")
    else:
        print("#"*40)
        print("The version online is newer!")
        print("STOP! Don't go backwards!")
        print("#"*40)
        for i in range(5):
            input("continue? [%s]"%(5-i))

def distribute():
    """only Scott should run this. Package this module and upload it."""
    if not cm.TK_ask("REALLY?","Are you *SURE* you want to push a public update?"):
        return
    warnIfNewer() #make sure we don't publish something old
    epoch=int(time.time()) #determine current time (new version number)
    if not os.path.exists(swhlab.LOCALPATH+"/version.py"):
        return print("root folder doesn't seem right. aborting.")
    with open(swhlab.LOCALPATH+"/version.py",'w') as f:
        f.write('version = %d'%epoch)
    msg='\n\n'+"-"*7+'[%d / %s]'%(epoch,cm.epochToDatetime(epoch))+"-"*7
    with open(swhlab.LOCALPATH+"/dist/changelog.txt",'a') as f:
        f.write(msg) #update changelog to reflect new version.
    zipFname=os.path.abspath(swhlab.TEMPPATH+"/%d.zip"%epoch)
    zipdir(swhlab.LOCALPATH,zipFname)
    print(" -- finished writing [%s]"%os.path.basename(zipFname))
    if upload(zipFname):
        print("distribution roll-out complete!".upper())
        swhlab.VERSION=epoch
    else:
        print("distribution roll-out FAILED!")

def check(url=swhlab.UPDATECHECK,popup=True):
    """
    check the website to see if this version is the latest.
    returns True if current, False if needs update.
    """

    print("ABANDONING OLD VERSION SYSTEM.")
    print("CHECKING GITHUB...")
    checkGitHub()
    print("GITHUB CHECK COMPLETE.")
    return

    timeStart = time.time()

    fileVersion=None
    try:
        with open(swhlab.LOCALPATH+"/version.py") as f:
            for line in f:
                line=line.strip().replace(" ",'')
                if "=" in line:
                    line=line.split("=")
                    fileVersion=int(line[1])
    except:
        pass

    newestVersion=int(cm.download(swhlab.UPDATECHECK))

    if fileVersion and not fileVersion==swhlab.VERSION:
        print("\n"*2)
        print(" ## PYTHON VERSION CHANGED ##")
        print(" -- the version in memory is different than the one in in your filesystem.")
        print(" -- If you just updated, try reloading all python modules.")
        return True

    daysOldNew=(time.time()-int(newestVersion))/60/60/24
    daysOldThis=(time.time()-int(swhlab.VERSION))/60/60/24
    if int(swhlab.VERSION)>=int(newestVersion):
        print(" ~ SWHLab is current (%.02f days old, check took %d ms)"%(daysOldThis,(time.time()-timeStart)*1000))
        return True
    else:
        if popup:
            msg=" ~ SWHLab updates are available!\n"
            msg+="     the latest version is %.02f days old\n"%daysOldNew
            msg+="     this one is %.02f days old\n"%daysOldThis
            print(msg)
            #cm.TK_message("UPDATE",msg)
            if cm.TK_ask("UPDATE AVAILABLE","I see a SWHLab update.\nDo you want to update now?"):
                print("UPDATING!")
                update()
        return False

def gentleDelete(deleteFolder):
    """
    tries to delete files and folders 1 by 1.
    and doesn't care if it can't delete something.
    This is good for trying to delete files you're currently running.
    """
    deleteFolder=os.path.abspath(deleteFolder)
    print(" -- deleting everything in",deleteFolder)
    sourceFiles=[]
    sourceDirs=[]
    for root, dirs, files in os.walk(deleteFolder):
        for f in files:
            sourceFiles.append(os.path.join(root, f))
        for d in dirs:
            sourceDirs.append(os.path.join(root, d))
    sourceDirs.sort() #creative way to make sure it's in recursive order
    sourceDirs.reverse() #creative way to go in anti-recursive order
    for f in sourceFiles:
        try:
            #print("      deleting",f.replace(deleteFolder,''))
            os.remove(f)
        except:
            #print("     ^^^^^ failed")
            print(" -- not deleting [%s]"%f.replace(deleteFolder,''))
    for d in sourceDirs:
        try:
            #print("      removing",d.replace(deleteFolder,''))
            os.rmdir(d)
        except:
            #print("     ^^^^^ failed")
            print(" -- not deleting [%s]"%d.replace(deleteFolder,''))

def gentleCopyOver(pathFrom,pathTo):
    """
    Try to copy things one by one.
    Don't fret if something doesn't copy.
    Good for copying things currently running.
    """
    pathFrom=os.path.abspath(pathFrom)
    pathTo=os.path.abspath(pathTo)
    print(" -- copying everything from",pathFrom)
    print(" -- copying everything here",pathTo)
    sourceFiles=[]
    sourceDirs=[]
    for root, dirs, files in os.walk(pathFrom):
        for f in files:
            sourceFiles.append(os.path.join(root, f))
        for d in dirs:
            sourceDirs.append(os.path.join(root, d))
    sourceDirs.sort() #creative way to make sure it's in recursive order
    for d in sourceDirs:
        if not os.path.exists(d.replace(pathFrom,pathTo)):
            #print("      creating",d.replace(pathFrom,''))
            os.mkdir(d.replace(pathFrom,pathTo))
    for f in sourceFiles:
        try:
            #print("      copying",f.replace(pathFrom,''))
            shutil.copy(f,f.replace(pathFrom,pathTo))
        except:
            #print("     ^^^^^ failed")
            print(" -- not copying [%s]"%f.replace(pathFrom,''))

def update():
    """download the latest version from the web."""
    print("cleaning temp directory...")
    if not os.path.exists(swhlab.TEMPPATH):
        os.mkdir(swhlab.TEMPPATH)
    for fname in glob.glob(swhlab.TEMPPATH+"/*.*"):
        os.remove(fname)
    newestVersion=cm.download(swhlab.UPDATECHECK)
    recentUrl=swhlab.UPDATEFROM+newestVersion+".zip"
    recentFname=newestVersion+".zip"
    saveAs=os.path.abspath(os.path.join(swhlab.TEMPPATH,recentFname))
    print(" -- downloading %s..."%saveAs)
    cm.download(recentUrl,saveAs)
    print(" -- extracting...")
    NEWSOURCE=swhlab.TEMPPATH+"/"+recentFname.split(".")[0]
    zip_ref = zipfile.ZipFile(saveAs, 'r')
    zip_ref.extractall(NEWSOURCE)
    zip_ref.close()
    overwrite=cm.TK_ask("overwrite?","OVERWRITE local copy?")
    if overwrite:
        gentleDelete(swhlab.LOCALPATH)
        gentleCopyOver(NEWSOURCE,swhlab.LOCALPATH)
        swhlab.VERSION=newestVersion
        print(" ## SWHLAB UPDATE COMPLETE ##")
    else:
        NEWSOURCE=swhlab.TEMPPATH+"/"+recentFname.split(".")[0]
        webbrowser.open(swhlab.LOCALPATH)
        webbrowser.open(NEWSOURCE)
        msg="Here is the latest distribution!\n\n"
        msg+="I've also opened the folder containing /swhlab/\n\n"
        msg+="Update the contents yourself..."
        cm.TK_message("MANUAL FILE COPY",msg)

def check_threaded():
    """
    Check the website to see if this version is the latest.
    This is threaded, so it doesn't hang the console.
    This is an easy thing to call, so don't hesitate to do it.
    """
    t=threading.Thread(target=check)
    t.start()

def prepareForGitHub():
    """
    just move pghd.py to the folder up.
    (customizing it to this path first)
    """
    if os.path.exists(swhlab.LOCALPATH+"/../swhlabUpdate.py"):
        print("../swhlabUpdate.py is where it should be")
        return
    print("../swhlabUpdate.py is not found. Creating one!")
    with open(swhlab.LOCALPATH+'/core/swhlabUpdate.py') as f:
        raw=f.read().split("\n")
    for i,line in enumerate(raw):
        if line.startswith("LOCAL_PATH="):
            raw[i]='LOCAL_PATH=r"%s"'%swhlab.LOCALPATH
            print(raw[i])
    with open(swhlab.LOCALPATH+"/../swhlabUpdate.py",'w') as f:
        f.write("\n".join(raw))
    print("../swhlabUpdate.py now exists and is custom to your computer.")

def checkGitHub():
    prepareForGitHub()
    script=os.path.abspath(swhlab.LOCALPATH+"/../swhlabUpdate.py")
    subprocess.Popen(["python",script])
    return

if __name__=="__main__":
    checkGitHub()
#    if 'distribute' in sys.argv:
#        distribute()
#    if 'forceupdate' in sys.argv:
#        swhlab.VERSION=0
#    check()
