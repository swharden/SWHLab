"""Show some sweeps around the last 2 comments."""

import os
import sys
if not os.path.abspath('../../../') in sys.path:
    sys.path.append('../../../')
import swhlab
import matplotlib.pyplot as plt
import numpy as np
import warnings
import time

def tagInspect(abf,saveToo=False): #TODO: put in ABF class?
    if len(abf.comment_tags)<2:
        warnings.warn("no tags in ABF!")
        return
    S1,S2=abf.comment_sweeps[-2],abf.comment_sweeps[-1]

    nSweeps = 20
    vertOffset = 50

    plt.close('all')
    plt.figure(figsize=(15,10))
    for i in range(nSweeps):

        abf.setsweep(int(S1-i))
        Y=swhlab.common.lowpass(abf.sweepY,abf.pointsPerMs*5)
        Y=Y-np.nanmean(Y)+i*vertOffset
        Y[:int(.5*abf.pointsPerSec)]=np.nan
        plt.plot(abf.sweepX2,Y,color='b',alpha=.5)
        plt.text(abf.sweepX2[.5*abf.pointsPerSec],i*vertOffset,
                 "%s "%str(abf.sweep),ha='right')

        abf.setsweep(int(S1-i+120/abf.sweepLength))
        Y=swhlab.common.lowpass(abf.sweepY,abf.pointsPerMs*5)
        Y=Y-np.nanmean(Y)+i*vertOffset
        Y[:int(.5*abf.pointsPerSec)]=np.nan
        plt.plot(abf.sweepX2+abf.sweepLength,Y,color='g',alpha=.5)
        plt.text(abf.sweepX2[.5*abf.pointsPerSec]+abf.sweepLength,i*vertOffset,
                 "%s "%str(abf.sweep),ha='right')

    plt.margins(0,0)
    plt.axis([None,None,-100,nSweeps*vertOffset])
    plt.axis('off')
    plt.title("[%s] sw %d (%s) - sw %d (%s)"%(abf.ID,S1,abf.comment_tags[-2],S2,abf.comment_tags[-1]))
    plt.tight_layout()
    if saveToo:
        plt.savefig(R"X:\Data Analysis\SCOTT\SWHLab development\phasic\%s.png"%abf.ID)
    plt.show()
    print()
    return

def picpage(path=R"X:\Data Analysis\SCOTT\SWHLab development\phasic"):
    html="<html><body>"
    for fname in [x for x in sorted(os.listdir(path)) if x.endswith(".png") or x.endswith(".jpg")]:
        html+='<a name="%s" href="#%s"><h1>%s</h1></a>'%(fname,fname,fname)
        fname=os.path.abspath(os.path.join(path,fname))
        html+='<a href="%s"><img src="%s"></a>'%(fname,fname)
    html+="</body></html>"
    with open(os.path.join(path,"index.html"),'w') as f:
        f.write(html)

if __name__=="__main__":
    abfs=[]
    abfs.append(R"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d14019.abf")
    abfs.append(R"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d14027.abf")
    abfs.append(R"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d14032.abf")
    abfs.append(R"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d14036.abf")
    abfs.append(R"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d14040.abf")
    abfs.append(R"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d14044.abf")
    abfs.append(R"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d14048.abf")
    abfs.append(R"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d14052.abf")
    abfs.append(R"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d14056.abf")
    abfs.append(R"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d14060.abf")
    abfs.append(R"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d14064.abf")
    abfs.append(R"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d16003.abf")
    abfs.append(R"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d16007.abf")
    abfs.append(R"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d16011.abf")
    abfs.append(R"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d16016.abf")
    abfs.append(R"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d16020.abf")
    abfs.append(R"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d16024.abf")
    abfs.append(R"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d16030.abf")
    abfs.append(R"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d16034.abf")
    abfs.append(R"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d16038.abf")
    abfs.append(R"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d16042.abf")
    abfs.append(R"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d16046.abf")

    for abf in abfs:
        abf=swhlab.ABF(abf)
        tagInspect(abf,saveToo=True)

    picpage()

    print("DONE")