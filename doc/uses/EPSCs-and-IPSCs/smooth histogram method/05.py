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

def analyzeSweep(abf,plotToo=True,color=None,label=None):
    Y=abf.sweepYsmartbase()[abf.pointsPerSec*.5:]
    AV,SD=np.average(Y),np.std(Y)
    dev=5 # number of stdevs from the avg to set the range
    R1,R2=[(AV-SD)*dev,(AV+SD)*dev]
    nBins=1000
    hist,bins=np.histogram(Y,bins=nBins,range=[R1,R2],density=True)
    histSmooth=abf.convolve(hist,cm.kernel_gaussian(nBins/5))

    if plotToo:
        plt.plot(bins[1:],hist,'.',color=color,alpha=.2,ms=10)
        plt.plot(bins[1:],histSmooth,'-',color=color,lw=5,alpha=.5,label=label)

    return

if __name__=="__main__":
    #abfFile=R"C:\Users\scott\Documents\important\demodata\abfs\16d07022.abf"
    abfFile=R"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d07022.abf"
    abf=swhlab.ABF(abfFile)

    # prepare figure
    plt.figure(figsize=(10,10))
    plt.grid()
    plt.title("smart baseline value distribution")
    plt.xlabel(abf.units2)
    plt.ylabel("normalized density")

    # do the analysis
    abf.kernel=abf.kernel_gaussian(sizeMS=500)
    abf.setsweep(175)
    analyzeSweep(abf,color='b',label="baseline")
    abf.setsweep(200)
    analyzeSweep(abf,color='g',label="TGOT")
    abf.setsweep(375)
    analyzeSweep(abf,color='y',label="washout")

    # show figure
    plt.legend()
    plt.margins(0,.1)
    plt.show()

    print("DONE")
