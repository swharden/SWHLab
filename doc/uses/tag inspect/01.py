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
import webbrowser

OUTPUT_PATH=R"X:\Data Analysis\SCOTT\SWHLab development\phasic2"

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

        abf.setsweep(S1-i*2)
        Y=swhlab.common.lowpass(abf.sweepY,abf.pointsPerMs*5)
        Y=Y-np.nanmean(Y)+i*vertOffset
        Y[:int(.5*abf.pointsPerSec)]=np.nan
        plt.plot(abf.sweepX2,Y,color='b',alpha=.5)
        plt.text(abf.sweepX2[.5*abf.pointsPerSec],i*vertOffset,
                 "%s "%str(abf.sweep),ha='right')

        abf.setsweep(S2-i*2)
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
        plt.savefig(R"X:\Data Analysis\SCOTT\SWHLab development\phasic2\%s.png"%abf.ID)
    plt.show()
    print()
    return

def picpage():
    html="<html><body>"
    for fname in [x for x in sorted(os.listdir(OUTPUT_PATH)) if x.endswith(".png") or x.endswith(".jpg")]:
        html+='<a name="%s" href="#%s"><h1>%s</h1></a>'%(fname,fname,fname)
        fname=os.path.abspath(os.path.join(OUTPUT_PATH,fname))
        html+='<a href="%s"><img src="%s"></a>'%(fname,fname)
    html+="</body></html>"
    htmlFname=os.path.join(OUTPUT_PATH,"index.html")
    with open(htmlFname,'w') as f:
        f.write(html)
    webbrowser.open(htmlFname)

if __name__=="__main__":
    abfPath=R"X:\Data\2P01\2016\2016-09-01 PIR TGOT"
    good=[]
    for fname in sorted(os.listdir(abfPath)):
        if not fname.endswith(".abf"):
            continue
        if fname[:5] in ["16831","16906","16907","16909"]:
            fname=os.path.join(abfPath,fname)
            if os.stat(fname).st_size/10**6>10: # only do files > ~10MB
                abf=swhlab.ABF(fname)
                if len(abf.comment_sweeps)<2:
                    print("SKIP:",fname)
                else:
                    good.append(fname)
                tagInspect(abf,saveToo=True)
    picpage()
    print("\n".join(good))

    print("DONE")