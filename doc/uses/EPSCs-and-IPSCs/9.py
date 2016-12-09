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

def analyzeSweep(abf):
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

    # separate EPSC and IPSC by splitting data at the peak
    EPSC,IPSC=np.split(histSmooth,2)
    return np.sum(EPSC),np.sum(IPSC),np.sum(EPSC)/np.sum(IPSC)

if __name__=="__main__":
    #abfFile=R"C:\Users\scott\Documents\important\demodata\abfs\16d07022.abf"
    abfFile=R"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d07022.abf"
    abf=swhlab.ABF(abfFile)
    abf.kernel=abf.kernel_gaussian(sizeMS=500) # kernel for smart baseline

    Ts,EPSCs,IPSCs,RATIOs=np.load("Ts.npy"),np.load("EPSCs.npy"),np.load("IPSCs.npy"),np.load("RATIOs.npy")

#    # this is slow so do this once
#    Ts,EPSCs,IPSCs,RATIOs=[],[],[],[]
#    for sweep in range(abf.sweeps):
#        abf.setsweep(sweep)
#        EPSC,IPSC,RATIO=analyzeSweep(abf)
#        print("Sweep %d EPSC: %.02f IPSC: %.02f RATIO: %.02f"%(sweep,EPSC,IPSC,RATIO))
#        Ts.append(abf.sweepStart/60.0)
#        EPSCs.append(EPSC)
#        IPSCs.append(IPSC)
#        RATIOs.append(RATIO)
#    np.save("Ts",Ts)
#    np.save("EPSCs",EPSCs)
#    np.save("IPSCs",IPSCs)
#    np.save("RATIOs",RATIOs)

    plt.figure(figsize=(15,7))

    plt.subplot(121)
    plt.title("Raw Density (using sum of normalized)")
    plt.grid()
    plt.xlabel("time (minutes)")
    plt.ylabel("excitation ratio")
    plt.plot(Ts,EPSCs,'r.',ms=20,alpha=.2)
    plt.plot(Ts,cm.lowpass(EPSCs,20),'r-',ms=20,alpha=.7,lw=4,label="EPSCs")
    plt.plot(Ts,IPSCs,'b.',ms=20,alpha=.2)
    plt.plot(Ts,cm.lowpass(IPSCs,20),'b-',ms=20,alpha=.7,lw=4,label="IPSCs")
    plt.legend()
    plt.margins(0,.1)

    plt.subplot(122)
    plt.title("Ratio")
    plt.grid()
    plt.xlabel("time (minutes)")
    plt.ylabel("excitation ratio")
    plt.axhline(1,color='r',alpha=.5,lw=4,ls='--')
    plt.plot(Ts,RATIOs,'.',color='.7',ms=20,alpha=.5)
    plt.plot(Ts,cm.lowpass(RATIOs,20),'g-',ms=20,alpha=.7,lw=4)
    plt.margins(0,.1)


    plt.tight_layout()
    plt.show()



    print("DONE")
