"""
This script investigates how calculating phasic currents from voltage clamp
recordings may benefit from subtracting-out the "noise" determined from a 
subset of the quietest pieces of the recording, rather than using smoothing
or curve fitting to guess a guassian-like RMS noise function.
"""

import os
import swhlab
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.mlab as mlab

POINTS_PER_SEC=20000
POINTS_PER_MS=int(POINTS_PER_SEC/1000)
CHUNK_POINTS=POINTS_PER_MS*10 # size of Y pieces to calculate variance from
PERCENT_STEP=10 # percentile steps to display
HIST_RESOLUTION=.1 # pA per bin
COLORMAP=plt.get_cmap('jet') # which color scheme do we want to use?
#COLORMAP=plt.get_cmap('winter') # which color scheme do we want to use?

def quietParts(data,percentile=10):
    """
    Given some data (Y) break it into chunks and return just the quiet ones.
    Returns data where the variance for its chunk size is below the given percentile.
    CHUNK_POINTS should be adjusted so it's about 10ms of data.
    """
    nChunks=int(len(Y)/CHUNK_POINTS)
    chunks=np.reshape(Y[:nChunks*CHUNK_POINTS],(nChunks,CHUNK_POINTS))
    variances=np.var(chunks,axis=1)
    percentiles=np.empty(len(variances))
    for i,variance in enumerate(variances):
        percentiles[i]=sorted(variances).index(variance)/len(variances)*100
    selected=chunks[np.where(percentiles<=percentile)[0]].flatten()
    return selected
    
def ndist(data,Xs):
    """
    given some data and a list of X posistions, return the normal
    distribution curve as a Y point at each of those Xs.
    """
    sigma=np.sqrt(np.var(data))
    center=np.average(data)
    curve=mlab.normpdf(Xs,center,sigma)
    curve*=len(data)*HIST_RESOLUTION
    return curve

if __name__=="__main__":
    Y=np.load("sweepdata.npy")
    
    # predict what our histogram will look like
    padding=50
    histCenter=int(np.average(Y))
    histRange=(histCenter-padding,histCenter+padding)
    histBins=int(abs(histRange[0]-histRange[1])/HIST_RESOLUTION)    
       
    # FIRST CALCULATE THE 10-PERCENTILE CURVE
    data=quietParts(Y,10) # assume 10% is a good percentile to use
    hist,bins=np.histogram(data,bins=histBins,range=histRange,density=False)
    hist=hist.astype(np.float) # histogram of data values
    curve=ndist(data,bins[:-1]) # normal distribution curve
    hist[hist == 0] = np.nan
    histValidIs=np.where(~np.isnan(hist))
    histX,histY=bins[:-1][histValidIs],hist[histValidIs] # remove nans
    baselineCurve=curve/np.max(curve) # max is good for smooth curve
        
    # THEN CALCULATE THE WHOLE-SWEEP HISTOGRAM
    hist,bins=np.histogram(Y,bins=histBins,range=histRange,density=False)
    hist=hist.astype(np.float) # histogram of data values
    hist[hist == 0] = np.nan
    histValidIs=np.where(~np.isnan(hist))
    histX,histY=bins[:-1][histValidIs],hist[histValidIs] # remove nans
    histY/=np.percentile(histY,98) # percentile is needed for noisy data
    
    # DETERMINE THE DIFFERENCE
    diffX=bins[:-1][histValidIs]
    diffY=histY-baselineCurve[histValidIs]
    diffY[diffY<0]=np.nan
    
    # NOW PLOT THE DIFFERENCE
    plt.figure(figsize=(10,10))
    plt.subplot(211)
    plt.grid()
    plt.plot(histX,histY,'b.',ms=10,alpha=.5,label="data points")
    plt.plot(bins[:-1],baselineCurve,'r-',lw=3,alpha=.5,label="10% distribution")
    plt.legend(loc='upper left',shadow=True)
    plt.ylabel("normalized distribution")
    plt.axis([histCenter-20,histCenter+20,0,1.5])
    
    plt.subplot(212)
    plt.grid()
    plt.plot(diffX,diffY,'.',ms=10,alpha=.5,color='b')
    plt.axvline(histCenter,color='r',lw=3,alpha=.5,ls='--')
    plt.legend(loc='upper left',shadow=True)
    plt.ylabel("difference")
    plt.xlabel("histogram data points (pA)") 
    plt.margins(0,.1)
    plt.axis([histCenter-20,histCenter+20,0,None])
    plt.tight_layout()
    plt.savefig("2016-12-16-tryout.png")
    plt.show()

    
    print("DONE")