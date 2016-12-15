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

    # start by lowpass filtering (1 direction)
#    Klpf=kernel_gaussian(size=abf.pointsPerMs*10,forwardOnly=True)
#    Ylpf=np.convolve(Yorig,Klpf,mode='same')
#    Y=Ylpf # commit

    Kmb=kernel_gaussian(size=abf.pointsPerMs*10,forwardOnly=True)
    Ymb=np.convolve(Yorig,Kmb,mode='same')
    Y=Yorig-Ymb # commit

    #Y1=np.copy(Y)
    #Y[np.where(Y>0)[0]]=np.power(Y,2)
    #Y[np.where(Y<0)[0]]=-np.power(Y,2)

    # event detection
    thresh=5 # threshold for an event
    hitPos=np.where(Y>thresh)[0] # area above the threshold
    hitNeg=np.where(Y<-thresh)[0] # area below the threshold
    hitPos=np.concatenate((hitPos,[len(Y)-1])) # helps with the diff() coming up
    hitNeg=np.concatenate((hitNeg,[len(Y)-1])) # helps with the diff() coming up
    hitsPos=hitPos[np.where(np.abs(np.diff(hitPos))>10)[0]] # time point of EPSC
    hitsNeg=hitNeg[np.where(np.abs(np.diff(hitNeg))>10)[0]] # time point of IPSC
    hitsNeg=hitsNeg[1:] # often the first one is in error
    #print(hitsNeg[0])

    if plotToo:
        plt.figure(figsize=(10,5))
        ax1=plt.subplot(211)
        plt.title("sweep %d: detected %d IPSCs (red) and %d EPSCs (blue)"%(sweep,len(hitsPos),len(hitsNeg)))
        plt.ylabel("delta pA")
        plt.grid()

        plt.plot(X,Yorig,color='k',alpha=.5)
        for hit in hitsPos:
            plt.plot(X[hit],Yorig[hit]+20,'r.',ms=20,alpha=.5)
        for hit in hitsNeg:
            plt.plot(X[hit],Yorig[hit]-20,'b.',ms=20,alpha=.5)
        plt.margins(0,.1)

        plt.subplot(212,sharex=ax1)
        plt.title("moving gaussian baseline subtraction used for threshold detection")
        plt.ylabel("delta pA")
        plt.grid()
        plt.axhline(thresh,color='r',ls='--',alpha=.5,lw=3)
        plt.axhline(-thresh,color='r',ls='--',alpha=.5,lw=3)
        plt.plot(X,Y,color='b',alpha=.5)

        plt.axis([X[0],X[-1],-thresh*1.5,thresh*1.5])
        plt.tight_layout()
        if type(plotToo) is str and os.path.isdir(plotToo):
            print('saving %s/%05d.jpg'%(plotToo,sweep))
            plt.savefig(plotToo+"/%05d.jpg"%sweep)
        else:
            plt.show()
        plt.close('all')

    return [len(hitsPos),len(hitsNeg)]

def indexPics(folder):
    pics=[x for x in os.listdir(folder) if x.endswith(".png") or x.endswith(".jpg")]
    pics=['<a href="%s"><img src="%s"></a>'%(x,x) for x in sorted(pics)]
    with open(folder+"/index.html",'w') as f:
        f.write("<html><body>"+"<br><br><br><br>".join(pics)+"</body></html>")

def analyzeABF(abf):
    abf=swhlab.ABF(abf)
    EPSCs=[]
    IPSCs=[]
    Xs=np.arange(abf.sweeps)*float(abf.sweepLength)/60.0
    for sweep in range(abf.sweeps):
        print("analyzing sweep %d of %d"%(sweep+1,abf.sweeps))
        plotToo=False
        if 0<Xs[sweep]<120:
            plotToo=r'C:\Users\swharden\Documents\temp'
        [hitsPos,hitsNeg]=analyzeSweep(abf,sweep=sweep,m1=.3,plotToo=plotToo)
        EPSCs.append(hitsPos/(float(abf.sweepLength)-.3))
        IPSCs.append(hitsNeg/(float(abf.sweepLength)-.3))
    EPSCsmooth=np.convolve(EPSCs,kernel_gaussian(20),mode='same')
    IPSCsmooth=np.convolve(IPSCs,kernel_gaussian(20),mode='same')
    plt.figure(figsize=(10,5))
    plt.grid()
    plt.plot(Xs,EPSCsmooth,'.',color='r',label="EPSCs",ms=10,alpha=.5)
    plt.plot(Xs,IPSCsmooth,'.',color='b',label="IPSCs",ms=10,alpha=.5)
    plt.axhline(0,color='k',lw=2)
    plt.legend()
    for t in abf.comment_times:
        plt.axvline(t/60,color='k',lw=2,ls='--',alpha=.5)
    plt.margins(0,.1)
    plt.ylabel("event frequency (Hz)")
    plt.xlabel("time (minutes)")
    plt.show()

    indexPics(r'C:\Users\swharden\Documents\temp')

if __name__=="__main__":
    analyzeABF(r"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d07022.abf")
    print("DONE")
