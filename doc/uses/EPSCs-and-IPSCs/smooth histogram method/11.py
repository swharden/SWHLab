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

def analyzeSweep(abf,label=None):
    Y=abf.sweepYsmartbase()[abf.pointsPerSec*.5:]
    #Y=abf.sweepY[abf.pointsPerSec*.5:]

    AV,SD=np.average(Y),np.std(Y)
    dev=5 # number of stdevs from the avg to set the range
    R1,R2=[(AV-SD)*dev,(AV+SD)*dev]
    nBins=1000
    hist,bins=np.histogram(Y,bins=nBins,range=[R1,R2],density=True)
    histSmooth=abf.convolve(hist,cm.kernel_gaussian(nBins/5))

    peakI=np.where(histSmooth==max(histSmooth))[0][0]

    # center the peak at 0 pA
    hist=np.roll(hist,int(nBins/2-peakI))
    histSmooth=np.roll(histSmooth,int(nBins/2-peakI))

    # normalize height to 1
    hist,histSmooth=hist/max(histSmooth),histSmooth/max(histSmooth)

    plt.plot(histSmooth,label=label,lw=3,alpha=.5)

if __name__=="__main__":
    #abfFile=R"C:\Users\scott\Documents\important\demodata\abfs\16d07022.abf"
    abfFile=R"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d07022.abf"
    abf=swhlab.ABF(abfFile)
    abf.kernel=abf.kernel_gaussian(sizeMS=500) # kernel for smart baseline

    plt.figure(figsize=(10,10))

#    for sweep in range(abf.sweeps):
    for sweep in [175,200,375]:
        abf.setsweep(sweep)
        analyzeSweep(abf,label=str(sweep))
        print("Sweep",sweep)

    plt.legend()
    plt.show()

    print("DONE")
