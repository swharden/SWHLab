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
    print(histBins)
    
    plt.figure(figsize=(10,10))
    plt.grid()
    for percentile in [10,20,50,75,100]:
        
        # determine the histogram / distribution curve
        data=quietParts(Y,percentile)
        hist,bins=np.histogram(data,bins=histBins,range=histRange,density=False)
        hist=hist.astype(np.float) # histogram of data values
        curve=ndist(data,bins[:-1]) # normal distribution curve
        hist[hist == 0] = np.nan
        histValidIs=np.where(~np.isnan(hist))
        histX,histY=bins[:-1][histValidIs],hist[histValidIs] # remove nans
        normalizeBy=np.max(curve)
        
        # plot the stuff
        color=COLORMAP(percentile/100)
        label="%2d percentile"%percentile
        plt.plot(histX,histY/normalizeBy,'.',color=color,alpha=.5,ms=10)
        plt.plot(bins[:-1],curve/normalizeBy,color=color,label=label,lw=3,alpha=.5)
        
    plt.legend(loc='upper left',shadow=True)
    plt.ylabel("normalized distribution")
    plt.xlabel("histogram data points (pA)")
    plt.title("normal distribution curves for data points in chunks with variance by percentile")
    plt.savefig("2016-12-15-percentile-fit3.png")
    plt.axis([histCenter-20,histCenter+20,0,2])
    plt.show()
    
    print("DONE")