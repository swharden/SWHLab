"""
Create a HTML report of the dates of active folders. The dates a folder is active
are determined from the file modified dates of the files it contains.
"""

import os
import time
import datetime

FNAME_OUTPUT="results.csv"
DAYSOFWEEK="Monday Tuesday Wednesday Thursday Friday Saturday Sunday".split(" ")

def fileModifiedTimestamp(fname):
    """return "YYYY-MM-DD" when the file was modified."""
    modifiedTime=os.path.getmtime(fname)
    stamp=time.strftime('%Y-%m-%d', time.localtime(modifiedTime))
    return stamp

def scanFolders(paths):
    if type(paths) is str:
        paths=[paths]
    t1=time.time()
    days=set()
    output=[]
    for path in paths:
        for root, dirs, files in os.walk(path, topdown = False):
            root=os.path.abspath(root)
            progressMsg=print("found %d days (%.02f yr)"%(len(days),len(days)/365))
            if len(output)%50==1: progressMsg
            timestamps=set()
            for fname in files:
                stamp=fileModifiedTimestamp(os.path.join(root,fname))
                timestamps.add(stamp)
                days.add(stamp)
            if len(timestamps)==0:
                continue
            output.append('"%s", %s'%(root,", ".join(sorted(list(timestamps)))))
    with open(FNAME_OUTPUT,'w') as f:
        f.write("\n".join(output))
    print("SCAN COMPLETE\nsaved",os.path.abspath(FNAME_OUTPUT))
    print("scan took %.02f seconds"%(time.time()-t1))
    print("found %d active folders spanning %d days"%(len(output),len(days)))
    return

def loadResults(resultsFile):
    """returns a dict of active folders with days as keys."""
    with open(resultsFile) as f:
        raw=f.read().split("\n")
    foldersByDay={}
    for line in raw:
        folder=line.split('"')[1]+"\\"
        line=[]+line.split('"')[2].split(", ")
        for day in line[1:]:
            if not day in foldersByDay:
                foldersByDay[day]=[]
            foldersByDay[day]=foldersByDay[day]+[folder]
    nActiveDays=len(foldersByDay)
    dayFirst=sorted(foldersByDay.keys())[0]
    dayLast=sorted(foldersByDay.keys())[-1]
    dayFirst=datetime.datetime.strptime(dayFirst, "%Y-%m-%d" )
    dayLast=datetime.datetime.strptime(dayLast, "%Y-%m-%d" )
    nDays = (dayLast - dayFirst).days + 1
    emptyDays=0
    for deltaDays in range(nDays):
        day=dayFirst+datetime.timedelta(days=deltaDays)
        stamp=datetime.datetime.strftime(day, "%Y-%m-%d" )
        if not stamp in foldersByDay:
            foldersByDay[stamp]=[]
            emptyDays+=1
    percActive=nActiveDays/nDays*100
    print("%d of %d days were active (%.02f%%)"%(nActiveDays,nDays,percActive))
    return foldersByDay

HTML_TEMPLATE="""
<html>
<style>
a {text-decoration: none; color: blue;}
a:hover {text-decoration: underline;}
.heading{
    font-size: 200%;
    font-weight: bold;
    text-decoration: underline;
}

.weekend_datecode {
    font-size: 200%;
    font-weight: bold;
    margin: 30 0 0 0px;
    padding: 0 0 0 10px;
    background-color: #AAAAFF;
    }
.weekend_folders {
    font-family: monospace;
    border-left: 20px solid #AAAAFF;
    background-color: #DDDDFF;
    padding: 10px;
}

.weekday_datecode {
    font-size: 200%;
    font-weight: bold;
    margin: 30 0 0 0px;
    padding: 0 0 0 10px;
    background-color: #DDDDDD;
    }
.weekday_folders {
    font-family: monospace;
    border-left: 20px solid #DDDDDD;
    background-color: #EEEEEE;
    padding: 10px;
}

</style>
<head>
<body>
</body>
</html>
"""

def HTML_results(resultsFile):
    """generates HTML report of active folders/days."""
    foldersByDay=loadResults(resultsFile)

    # optionally skip dates before a certain date
#    for day in sorted(list(foldersByDay.keys())):
#        if time.strptime(day,"%Y-%m-%d")<time.strptime("2016-05-01","%Y-%m-%d"):
#            del foldersByDay[day]

    # Create a header
    html="<div class='heading'>Active Folder Report (updated TIMESTAMP)</div>"
    html+="<li>When a file is created (or modified) its parent folder is marked active for that day."
    html+="<li>This page reports all folders which were active in the last several years. "
    html+="<li>A single folder can be active for more than one date."
    html=html.replace("TIMESTAMP",(time.strftime('%Y-%m-%d', time.localtime())))
    html+="<br>"*5


    # create menu at the top of the page
    html+="<div class='heading'>Active Folder Dates</div>"
    html+="<code>"
    lastMonth=""
    lastYear=""
    for day in sorted(list(foldersByDay.keys())):
        month=day[:7]
        year=day[:4]
        if year!=lastYear:
            html+="<br><br><b style='font-size: 200%%;'>%s</b> "%year
            lastYear=year
        if month!=lastMonth:
            html+="<br><b>%s:</b> "%month
            lastMonth=month
        html+="<a href='#%s'>%s</a>, "%(day,day[8:])
    html+="<br>"*5
    html=html.replace(", <br>","<br>")
    html+="</code>"

    # create the full list of folders organized by active date
    html+="<div class='heading'>Active Folders</div>"
    for day in sorted(list(foldersByDay.keys())):
        dt=datetime.datetime.strptime(day, "%Y-%m-%d" )
        classPrefix="weekday"
        if int(dt.weekday())>4:
            classPrefix="weekend"
        html+="<a name='%s' href='#%s' style='color: black;'>"%(day,day)
        title="%s (%s)"%(day,DAYSOFWEEK[dt.weekday()])
        html+="<div class='%s_datecode'>%s</div></a>"%(classPrefix,title)
        html+="<div class='%s_folders'>"%(classPrefix)
        # define folders to skip
        for folder in foldersByDay[day]:
            if "\\References\\" in folder:
                continue
            if "\\MIP\\" in folder:
                continue
            if "LineScan-" and "\\analysis\\" in folder:
                continue
            if "trakem2" in folder:
                continue
            if "SWHlab-" in folder:
                continue
            if "\\swhlab" in folder:
                continue
            html+="%s<br>"%folder
        html+="</div>"
    fnameSave=resultsFile+".html"
    html=html.replace("D:\\X_Drive\\","X:\\")
    with open(fnameSave,'w') as f:
        f.write(HTML_TEMPLATE.replace("<body>","<body>"+html))
    print("saved",fnameSave)

if __name__=="__main__":
    #scanFolders([R"D:\X_Drive\Data",R"D:\X_Drive\Data Analysis"])
    HTML_results(FNAME_OUTPUT)
    print("DONE")
