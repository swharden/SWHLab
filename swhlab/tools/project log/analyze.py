import datetime
import numpy as np
import matplotlib.pyplot as plt

def readLog(fname="workdays.csv",onlyAfter=datetime.datetime(year=2017,month=1,day=1)):
    """return a list of [stamp, project] elements."""
    with open(fname) as f:
        raw=f.read().split("\n")
    efforts=[] #date,nickname
    for line in raw[1:]:
        line=line.strip().split(",")
        date=datetime.datetime.strptime(line[0], "%Y-%m-%d")
        if onlyAfter and date<onlyAfter:
            continue
        if len(line)<3:
            continue
        for project in line[2:]:
            project=project.strip()
            if len(project):
                efforts.append([date,project])
    return efforts

if __name__=="__main__":
    efforts=readLog()

    # create a graph of the yearly projects    
    plt.figure(figsize=(6,4))
    projects=sorted(list(set([x[1] for x in efforts])))
    for projectNumber,project in enumerate(projects):
        projectDates=sorted(list(set([x[0] for x in efforts if x[1]==project])))        
        plt.plot(projectDates,[projectNumber]*len(projectDates),'s',alpha=.8, mew=0)
    plt.grid()
    plt.gcf().autofmt_xdate()
    plt.yticks(np.arange(len(projects)),["%s (%d)"%(x,len([y for y in efforts if y[1]==x])) for x in projects],fontsize=7)
    plt.gca().yaxis.grid(color='k', linewidth=6,alpha=.1)     
    plt.title("Scott's Projects for 2017")
    plt.ylabel("project nickname (number of days)")
    plt.savefig("projects.png",dpi=300)
    plt.show()
    
    print("DONE")