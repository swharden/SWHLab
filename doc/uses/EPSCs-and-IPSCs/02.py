"""
MOST OF THIS CODE IS NOT USED
ITS COPY/PASTED AND LEFT HERE FOR CONVENIENCE
"""

import os
import sys

# in case our module isn't installed (running from this folder)
thisPath=os.path.abspath('../../../')
print(thisPath)
if not thisPath in sys.path:
    sys.path.append(thisPath)

import swhlab
import matplotlib.pyplot as plt
import numpy as np

def kernel_gaussian(size=100, sigma=None, forwardOnly=False):
    """
    return a 1d gassuan array of a given size and sigma.
    If sigma isn't given, it will be 1/10 of the size, which is usually good.
    """
    if sigma is None:sigma=size/10
    points=np.exp(-np.power(np.arange(size)-size/2,2)/(2*np.power(sigma,2)))
    if forwardOnly:
        points[:int(len(points)/2)]=0
    return points/sum(points)

def inspectKernel(abf,Kmb):
    plt.figure(figsize=(5,5))
    plt.plot(np.arange(len(Kmb))/abf.pointsPerMs,Kmb)
    plt.xlabel("time (ms)")
    plt.grid()
    plt.title("kernel")
    plt.margins(0,.1)
    plt.show()

def inspectMovingBaseline(abf,X,Y,Ymb):
    plt.figure(figsize=(10,5))
    ax1=plt.subplot(211)
    plt.grid()
    plt.plot(X,Y,alpha=.5)
    plt.plot(X,Ymb,color='k',alpha=1)
    plt.subplot(212,sharex=ax1)
    plt.grid()
    plt.axhline(0,color='k')
    plt.plot(X,Y-Ymb,color='r',alpha=.5)
    plt.margins(0,.1)
    plt.axis([.70,1,None,None])
    plt.tight_layout()
    plt.show()

def inspectFirstDeriv(abf,X,Y,dTms=1):

    dT=int(dTms*abf.pointsPerMs)
    dY=Y[dT:]-Y[:-dT]
    plt.figure(figsize=(10,5))
    plt.grid()
    plt.margins(0,.1)
    plt.plot(X[:len(dY)],dY)
    plt.axis([.70,1,None,None])
    plt.tight_layout()
    plt.show()
    return

def inspectLPF(abf,X,Y,Ylpf):
    plt.figure(figsize=(10,5))
    ax1=plt.subplot(211)
    plt.ylabel("original data")
    plt.grid()
    plt.plot(X,Y,alpha=.5)
    plt.subplot(212,sharex=ax1)
    plt.ylabel("lowpass filtered")
    plt.grid()
    plt.plot(X,Ylpf,color='b',alpha=.5)
    plt.margins(0,.1)
    plt.axis([.70,1,None,None])
    plt.tight_layout()
    plt.show()

def inspectTrace(abf,X,Y):
    plt.figure(figsize=(10,5))
    plt.grid()
    plt.plot(X,Y,color='b',alpha=.5)
    plt.margins(0,.1)
    plt.axis([.70,1,None,None])
    plt.tight_layout()
    plt.show()

def inspectTraces(abf,X,Y1,Y2):
    plt.figure(figsize=(10,5))
    ax1=plt.subplot(211)
    plt.grid()
    plt.plot(X,Y1,color='b',alpha=.5)
    plt.subplot(212,sharex=ax1)
    plt.grid()
    plt.plot(X,Y2,color='b',alpha=.5)
    plt.margins(0,.1)
    plt.axis([.70,1,None,None])
    plt.tight_layout()
    plt.show()

def linear_gaussian(Y, sigmaSize,forwardOnly=False):
    pad=np.ones(sigmaSize)
    Y=np.concatenate((pad*Y[0],Y,pad*Y[-1]))
    Klpf=kernel_gaussian(size=sigmaSize,forwardOnly=forwardOnly)
    return np.convolve(Y,Klpf,mode='same')[len(pad):-len(pad)]

def indexPics(folder):
    pics=[x for x in os.listdir(folder) if x.endswith(".png") or x.endswith(".jpg")]
    pics=['<a href="%s"><img src="%s"></a>'%(x,x) for x in sorted(pics)]
    with open(folder+"/index.html",'w') as f:
        f.write("<html><body>"+"<br><br><br><br>".join(pics)+"</body></html>")

def analyzeABF(abf):
    abf=swhlab.ABF(abf)
    data=[]
    Xs=np.arange(abf.sweeps)*float(abf.sweepLength)/60.0
    for sweep in range(abf.sweeps):
        print("analyzing sweep %d of %d"%(sweep+1,abf.sweeps))
        data.append(analyzeSweep(abf,sweep=sweep,m1=.3))
    plt.figure(figsize=(10,5))
    plt.grid()
    plt.plot(Xs[:len(data)],data,'.',alpha=.5,ms=10)
    plt.axhline(0,color='k',lw=1,ls='--')
    for t in abf.comment_times:
        plt.axvline(t/60,color='k',lw=2,ls='--',alpha=.5)
    plt.margins(0,.1)
    plt.xlabel("time (minutes)")
    plt.ylabel("excitatory balance")
    plt.show()

    indexPics(r'C:\Users\swharden\Documents\temp')

def analyzeSweep(abf,sweep,m1=None,m2=None,plotToo=False):
    """
    m1 and m2, if given, are in seconds.
    returns [# EPSCs, # IPSCs]
    """
    abf.setsweep(sweep)
    if m1 is None: m1=0
    else: m1=m1*abf.pointsPerSec
    if m2 is None: m2=-1
    else: m2=m2*abf.pointsPerSec

    # obtain X and Y
    Yorig=abf.sweepY[int(m1):int(m2)]
    X=np.arange(len(Yorig))/abf.pointsPerSec

    Ylpf=linear_gaussian(Yorig,sigmaSize=abf.pointsPerMs*300,forwardOnly=False)
    Yflat=Yorig-Ylpf

    EPSCs,IPSCs=[],[]

    if plotToo:
        plt.figure(figsize=(15,6))
        ax1=plt.subplot(211)
        plt.title("%s sweep %d"%(abf.ID,sweep))
        plt.grid()
        plt.plot(X,Yorig,alpha=.5)
        plt.plot(X,Ylpf,'k',alpha=.5,lw=2)
        plt.margins(0,.2)

        plt.subplot(212,sharex=ax1)
        plt.title("gaussian baseline subtraction")
        plt.grid()
        plt.plot(X,Yflat,alpha=.5)
        plt.axhline(0,color='k',lw=2,alpha=.5)

        plt.tight_layout()
        plt.show()

    # TEST GAUSS
    hist, bin_edges = np.histogram(Yflat, density=True, bins=200)
    peakPa=bin_edges[np.where(hist==max(hist))[0][0]+1]

    if plotToo:
        plt.figure()
        plt.grid()
        plt.plot(bin_edges[1:],hist,alpha=.5)
        plt.axvline(0,color='k')
        plt.axvline(peakPa,color='r',ls='--',lw=2,alpha=.5)
        plt.semilogy()
        plt.title("sweep data distribution")
        plt.ylabel("power")
        plt.xlabel("pA deviation")
        plt.show()

    return peakPa


if __name__=="__main__":
    #analyzeABF(r"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d07022.abf")
    abf=swhlab.ABF(r"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d07022.abf")
    analyzeSweep(abf,sweep=174,m1=.3,plotToo=True)
    analyzeSweep(abf,sweep=199,m1=.3,plotToo=True)
    print("DONE")
