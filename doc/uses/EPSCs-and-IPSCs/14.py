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

    if plot:
        plt.plot(bins[-len(downward):],downward,lw=3,alpha=.5,color='g',ls='--',label='downward')
        plt.plot(bins[-len(downward):],upward,lw=3,alpha=.5,color='g',ls=':',label='upward')
        plt.plot(bins[-len(downward):],upward-downward,lw=3,alpha=.5,color='b',label='difference')

if __name__=="__main__":
    #abfFile=R"C:\Users\scott\Documents\important\demodata\abfs\16d07022.abf"
    abfFile=R"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d07022.abf"
    abf=swhlab.ABF(abfFile)
    abf.kernel=abf.kernel_gaussian(sizeMS=500) # kernel for smart baseline

    for sweep in [175,200,375]:
        print("Sweep",sweep)
        abf.setsweep(sweep)

        plt.figure(figsize=(5,5))
        plt.title("baseline (sweep 175)")
        plt.grid()
        analyzeSweep(abf,plot=True,label="sweep %d"%sweep)
        plt.legend()
        plt.ylabel("histogram bin density")
        plt.xlabel(abf.units2)
        plt.show()

    print("DONE")
