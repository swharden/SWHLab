import matplotlib.pyplot as plt
import numpy as np
import matplotlib.mlab as mlab






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
    
def ndist(data,histX,histY,color=None,normalize=True,plotToo=True,centerHistMax=False,label=None):
    sigma=np.sqrt(np.var(data))
    if centerHistMax:
        center=histX[np.where(histY==max(histY))[0][0]] # histogram
    else:
        center=np.average(data)
    x = np.linspace(center-20,center+20,100)
    curve=mlab.normpdf(x,center,sigma)
    curve*=len(data)*HIST_RESOLUTION
    if normalize:
        histY/=max(curve)
        curve/=max(curve)
    if plotToo:
        plt.plot(histX,histY,'.',alpha=.5,color=color,ms=10)    
        plt.plot(x,curve,'-',alpha=.5,color=color,lw=3,label=label)

if __name__=="__main__":
    Y=np.load("sweepdata.npy")
    
    # predict what our histogram will look like
    histCenter=int(np.average(Y))
    histRange=(histCenter-50,histCenter+50)
    histBins=int(abs(histRange[0]-histRange[1])/HIST_RESOLUTION)
    
    plt.figure(figsize=(10,10))
    plt.grid()
    #for percentile in [5,25,50,75,100]:
    for percentile in range(100):
        data=quietParts(Y,percentile)
        hist,bins=np.histogram(data,bins=histBins,range=histRange,density=False)
        hist=hist.astype(np.float)
        hist[hist == 0] = np.nan
        histValidIs=np.where(~np.isnan(hist))
        histX,histY=bins[:-1][histValidIs],hist[histValidIs] # remove breaks
        #ndist(data,histX,histY,color=COLORMAP(percentile/100),label="%d percentile"%percentile)
        plt.plot(percentile,np.sqrt(np.var(data)),'.',ms=20)
    plt.legend(loc='upper left',shadow=True)
    plt.margins(0,0)
    plt.ylabel("sigma")
    plt.xlabel("percentile")
    plt.title("checking out sigma")
    plt.savefig("2016-12-15-percentile-fit2.png")
    plt.show()
    
    print("DONE")