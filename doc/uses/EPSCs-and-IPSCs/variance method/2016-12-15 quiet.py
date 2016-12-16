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

POINTS_PER_SEC=20000
POINTS_PER_MS=int(POINTS_PER_SEC/1000)
CHUNK_POINTS=POINTS_PER_MS*10 # size of Y pieces to calculate variance from
PERCENT_STEP=10 # percentile steps to display
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
    
if __name__=="__main__":
    Y=np.load("sweepdata.npy")
    
    # predict what our histogram will look like
    histCenter=int(np.average(Y))
    histRange=(histCenter-20,histCenter+20)
    histStep=.1 #1 pA bins
    histBins=int(abs(histRange[0]-histRange[1])/histStep)
    
    plt.figure(figsize=(10,10))
    plt.grid()
    for percentile in [5,25,50,75,100]:
        data=quietParts(Y,percentile)
        hist,bins=np.histogram(data,bins=histBins,range=histRange,density=False)
        hist=hist.astype(np.float)
        hist[hist == 0] = np.nan
        histValidIs=np.where(~np.isnan(hist))
        histX,histY=bins[:-1][histValidIs],hist[histValidIs] # remove breaks
        histY=histY/max(histY) # normalize to 1
        plt.plot(histX,histY,'.-',color=COLORMAP(percentile/100),
                 label="%2d percentile"%percentile,lw=2,alpha=.7)
    plt.legend(loc='upper left',shadow=True)
    plt.ylabel("normalized fraction")
    plt.xlabel("values (pA)")
    plt.title("histograms from data with variance below a percentile")
    plt.savefig("2016-12-15-percentile-histogram.png")
    plt.show()
    
    print("DONE")