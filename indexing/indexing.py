"""Things here to webpage indexes of files."""

import os
import sys
import pylab
import numpy as np
import time
import glob

import swhlab
from swhlab.core import common as cm #shorthand

TEMPLATES={} #pythonic way to have HTML templates ready to go and read only once
for fname in glob.glob(swhlab.LOCALPATH+'/indexing/templates/template_*.html'):
    templateName=os.path.basename(fname).split("_")[1].replace('.html','')
    with open(fname) as f:
        TEMPLATES[templateName]=f.read()
for key in TEMPLATES:
    TEMPLATES[key]=TEMPLATES[key].replace("~STYLE~",TEMPLATES['style'])

print(" -- loaded data from %d HTML templates"%len(TEMPLATES))

def genPNGs(folder,files=None):
    """Convert each TIF to PNG. Return filenames of new PNGs."""
    if files is None:
        files=glob.glob(folder+"/*.*")
    new=[]
    for fname in files:
        ext=os.path.basename(fname).split(".")[-1].lower()
        if ext in ['tif','tiff']:
            if not os.path.exists(fname+".png"):
                print(" -- converting %s to PNG..."%os.path.basename(fname))
                cm.image_convert(fname)
                new.append(fname) #fancy burn-in of image data
            else:
                pass
                #print(" -- already converted %s to PNG..."%os.path.basename(fname))
    return new

def htmlABFcontent(ID,group,d):
    """generate text to go inside <body> for single ABF page."""
    html=""
    files=[]
    for abfID in group:
        files.extend(d[abfID])
    files=sorted(files)

    #start with root images
    html+="<hr>"
    for fname in files:
        if ".png" in fname.lower() and not "swhlab4" in fname:
            fname="../"+os.path.basename(fname)
            html+='<a href="%s"><img src="%s" width="348"></a> '%(fname,fname)

    #progress to /swhlab4/ images
    html+="<hr>"
    #ABFinfo
    lastID=''
    for fname in sorted(files):
        if not "swhlab4" in fname:
            continue
        ID=os.path.basename(fname).split("_")[0]
        if not ID==lastID:
            lastID=ID
            html+="<h3>%s</h3>"%os.path.basename(fname).split("_")[0]
        if ".png" in fname.lower():
            fname=os.path.basename(fname)
            html+='<a href="%s"><img src="%s" height="300"></a> '%(fname,fname)
            continue

    html+="<hr>"
    for fname in files:
        if not "swhlab4" in fname:
            continue
        if ".pkl" in fname:
            callit=os.path.basename(fname)
            thing=cm.getPkl(fname)
            if "_APs.pkl" in fname:
                callit+=" (first AP)"
                thing=cm.dictFlat(thing)
                if len(thing):
                    thing=thing[0]
            elif "_MTs.pkl" in fname:
                if type(thing) == dict:
                    callit+=" (from AVG of all sweeps)"
                else:
                    callit+=" (first sweep)"
                    thing=thing[0]
            elif "_SAP.pkl" in fname:
                continue #don't plot those, too complicated
            elif "_info.pkl" in fname or "_iv.pkl" in fname:
                pass #no trouble, go for it
            else:
                print(" ?? not sure how to index [%s]"%os.path.basename(fname))
                continue
            if type(thing) is dict:
                thing=cm.msgDict(thing)
            if type(thing) is list:
                out=''
                for item in thing:
                    out+=str(item)+"\n"
                thing=out
            thing=str(thing) #lol stringthing
            thing="### %s ###\n"%os.path.basename(fname)+thing

            # putting it in a textbox is obnoxious. put it in the source instead.
            #html+='<br><br><textarea rows="%d" cols="70">%s</textarea>'%(str(thing).count("\n")+5,thing)

            html+="(view source for %s) <!--\n\n%s\n\n-->"%(os.path.basename(fname),thing)

    return html

def htmlABF(ID,group,d,folder,overwrite=False):
    """given an ID and the dict of files, generate a static html for that abf."""
    fname=folder+"/swhlab4/%s_index.html"%ID
    if overwrite is False and os.path.exists(fname):
        return
    html=TEMPLATES['abf']
    html=html.replace("~ID~",ID)
    html=html.replace("~CONTENT~",htmlABFcontent(ID,group,d))
    print(" <- writing [%s]"%os.path.basename(fname))
    with open(fname,'w') as f:
        f.write(html)
    return

#def htmlIndexMenu(files,groups,folder):
#    #exp=experimentLookup(folder)
#    html=""
#    html+="""
#    <script>
#    function setClicked(id) {
#        elems = document.getElementsByClassName('abflink');
#        for (i = 0; i < elems.length; i++) {
#            elems[i].style.fontWeight="normal";
#            if (elems[i].id==id) {
#                elems[i].style.fontWeight="bold";
#            }
#        }
#        elems = document.getElementsByClassName('abftick');
#        for (i = 0; i < elems.length; i++) {
#            elems[i].style.visibility="hidden";
#            if (elems[i].id==id) {
#                elems[i].style.visibility="visible";
#            }
#        }
#    }
#    </script>
#    """
#    for ID in sorted(groups.keys()):
#        html+='<span class="abftick" id="%s" style="visibility: hidden;">&raquo;</span>'%(ID)
#        html+='<span class="abflink" id="%s">'%(ID)
#        html+='<a href="%s" target="main" onclick="setClicked(%s);">%s</a>'%("%s_index.html"%ID,ID,ID)
#        html+=' (%d)'%(len(groups[ID]))
#        html+='</span><br>'
#    #html+="<br>".join(d.keys())
#    html=TEMPLATES['menu'].replace("~CONTENT~",html)
#    print(" <- writing [menu.html]")
#    with open(folder+"/swhlab4/menu.html",'w') as f:
#        f.write(html)
#    return

#def htmlIndexSplash(d,groups,folder):
#    html="<h1>SWHLab4 Automatic Index</h1>"
#    html+="<h3>%d abfs (%d cells)</h3>"%(len(d),len(groups))
#    html+="<code>"
#    for group in groups:
#        html+="<br><b>%s</b><br>"%(group)
#        for abfID in groups[group]:
#            html+=" - %s<br>"%(group)
#    html+="</code>"
#    html=TEMPLATES['splash'].replace("~CONTENT~",html)
#    print(" <- writing [splash.html]")
#    with open(folder+"/swhlab4/splash.html",'w') as f:
#        f.write(html)
#    return

def htmlFrames(d,folder):
    html=TEMPLATES['frames']
    print(" <- writing [index.html]")
    with open(folder+"/index.html",'w') as f:
        f.write(html)
    return

def expMenu(groups,folder):
    """read experiment.txt and return a dict with [firstOfNewExp, color, star, comments]."""
    ### GENERATE THE MENU DATA BASED ON EXPERIMENT FILE
    orphans = sorted(list(groups.keys()))
    menu=[]
    if os.path.exists(folder+'/experiment.txt'):
        with open(folder+'/experiment.txt') as f:
            raw=f.read()
    else:
        raw=""
    for line in raw.split("\n"):
        item={}
        if len(line)==0:
            continue
        if line.startswith("~"):
            line=line[1:].split(" ",2)
            item["ID"]=line[0]
            item["symbol"]=''
            if len(line)>1:
                item["color"]=line[1]
            else:
                item["color"]="white"
            if len(line)>2 and len(line[2]):
                item["comment"]=line[2]
                if item["comment"][0]=="*":
                    item["symbol"]='*'
            else:
                item["comment"]=''
            if item["ID"] in orphans:
                orphans.remove(item["ID"])
        elif line.startswith("###"):
            line=line[3:].strip().split(" ",1)
            item["title"]=line[0]
            item["comment"]=''
            if len(line)>1:
                if line[1].startswith("- "):
                    line[1]=line[1][2:]
                item["comment"]=line[1]
        else:
            item["unknown"]=line
        menu.append(item)
    menu.append({"title":"orphans","comment":""})
    for ophan in orphans:
        menu.append({"orphan":ophan,"ID":ophan,"color":'',"symbol":'',"comment":''})
    return menu

def getLinkFor(item):
    html=""
    html+='<span class="abftick" id="%s" style="visibility: hidden;">&raquo;</span>'%(item["ID"])
    html+='<a href="%s_index.html" target="main" onclick="setClicked(%s);">'%(item["ID"],item["ID"])
    html+='<span class="link_%s" id="%s">%s</span></a>%s'%(item["color"],item["ID"],item["ID"],item["symbol"])
    return html

def makeMenu(menu,folder,hideGray=True):
    html="<code>"
    for item in menu:
        if "title" in item.keys(): #EXP TITLE
            html+="<br><b>%s</b><br>"%(item["title"])
        elif "ID" in item.keys(): #ABF
            if hideGray and item["color"]=="gray":
                continue
            html+=getLinkFor(item)+"<br>"
        elif "orphan" in item.keys():
            #html+="~%s<br>"%item["orphan"]
            html+=getLinkFor(item["orphan"])+"<br>"
    html+="</code>"

    html=TEMPLATES['menu'].replace("~CONTENT~",html)
    print(" <- writing [menu.html]")
    with open(folder+"/swhlab4/menu.html",'w') as f:
        f.write(html)

def makeSplash(menu,folder):
    html="<code>"
    for item in menu:
        if "title" in item.keys(): #EXP TITLE
            html+="<br><b>### %s ###</b> <i>%s</i><br><br>"%(item["title"],item["comment"])
        elif "ID" in item.keys(): #ABF
            #html+="%s%s <i>%s</i><br>"%(item["ID"],item["symbol"],item["comment"])
            html+=getLinkFor(item)
            html+=' - <i>%s</i>'%item["comment"]
            html+="<br>"
        elif "unknown" in item.keys():
            html+=">>> %s<br>"%item["unknown"]
        elif "orphan" in item.keys():
            html+="~%s<br>"%item["orphan"]
        else:
            html+="??? %s<br>"%str(item)
    html+="</code>"

    html=TEMPLATES['splash'].replace("~CONTENT~",html)
    print(" <- writing [splash.html]")
    with open(folder+"/swhlab4/splash.html",'w') as f:
        f.write(html)

def genIndex(folder,forceIDs=[]):
    """expects a folder of ABFs."""
    if not os.path.exists(folder+"/swhlab4/"):
        print(" !! cannot index if no /swhlab4/")
        return
    timestart=cm.timethis()
    files=glob.glob(folder+"/*.*") #ABF folder
    files.extend(glob.glob(folder+"/swhlab4/*.*"))
    print(" -- indexing glob took %.02f ms"%(cm.timethis(timestart)*1000))
    files.extend(genPNGs(folder,files))
    files=sorted(files)
    timestart=cm.timethis()
    d=cm.getIDfileDict(files) #TODO: this is really slow
    print(" -- filedict length:",len(d))
    print(" -- generating ID dict took %.02f ms"%(cm.timethis(timestart)*1000))
    groups=cm.getABFgroups(files)
    print(" -- groups length:",len(groups))
    for ID in sorted(list(groups.keys())):
        overwrite=False
        for abfID in groups[ID]:
            if abfID in forceIDs:
                overwrite=True
        try:
            htmlABF(ID,groups[ID],d,folder,overwrite)
        except:
            print("~~ HTML GENERATION FAILED!!!")
    menu=expMenu(groups,folder)
    makeSplash(menu,folder)
    makeMenu(menu,folder)
    htmlFrames(d,folder)
    makeMenu(menu,folder)
    makeSplash(menu,folder)

if __name__=="__main__":
    genIndex(r'X:\Data\2P01\2016\2016-07-11 PIR TR IHC')
    #experimentLookup(r'C:\Users\scott\Desktop\limited')
    print("DONE")