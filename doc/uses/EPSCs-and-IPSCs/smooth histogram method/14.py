"""
MOST OF THIS CODE IS NOT USED
ITS COPY/PASTED AND LEFT HERE FOR CONVENIENCE
"""

import os
import sys

# in case our module isn't installed (running from this folder)
if not os.path.abspath('../../../') in sys.path:
    sys.path.append('../../../') # helps spyder get docs

import swhlab
import swhlab.common as cm
import matplotlib.pyplot as plt
import numpy as np

import warnings # suppress VisibleDeprecationWarning warning
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)

def analyzeSweep(abf,label=None,plot=True,biggestEvent=30):
    # acquire the baseline-subtracted sweep
    Y=abf.sweepYsmartbase()[abf.pointsPerSec*.5:]

    # create the histogram
    nBins=1000
    hist,bins=np.histogram(Y,bins=nBins,range=[-biggestEvent,biggestEvent],density=True)
    histSmooth=cm.lowpass(hist,nBins/5)

    # normalize height to 1
    hist,histSmooth=hist/max(histSmooth),histSmooth/max(histSmooth)

    # center the peak at 0 pA
    peakI=np.where(histSmooth==max(histSmooth))[0][0]
    hist=np.roll(hist,int(nBins/2-peakI))
    histSmooth=np.roll(histSmooth,int(nBins/2-peakI))

    downward,upward=np.split(histSmooth,2)
    downward=downward[::-1]
    return(np.sum(upward-downward)) #TODO: should it not be normalized first?

if __name__=="__main__":
    #abfFile=R"C:\Users\scott\Documents\important\demodata\abfs\16d07022.abf"
    abfFile=R"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d07022.abf"
    abf=swhlab.ABF(abfFile)
    abf.kernel=abf.kernel_gaussian(sizeMS=500) # kernel for smart baseline

    if os.path.exists("diffs.npy"):
        diff=np.load("diffs.npy")
    else:
        diff=[]
        for sweep in abf.setsweeps():
            print("Sweep",sweep)
            diff.append(analyzeSweep(abf,plot=True,label="sweep %d"%sweep))
        np.save("diffs",diff)

    Xs=np.arange(abf.sweeps)*abf.sweepLength/60.0
    plt.figure(figsize=(10,10))
    plt.grid()
    plt.axhline(0,color='k',ls='--',lw=2,alpha=.5)
    plt.axvspan(5.26,7.25,color='r',alpha=.1)
    #plt.axvline(7.26,color='r',ls='--',lw=4,alpha=.5)
    plt.plot(Xs,diff,'.',color='.7',alpha=.5,ms=20)
    plt.plot(Xs,cm.lowpass(diff,10),color='b',lw=2,alpha=.7)
    plt.ylabel("net phasic current (pA)")
    plt.margins(0,.1)
    plt.show()


    print("DONE")
