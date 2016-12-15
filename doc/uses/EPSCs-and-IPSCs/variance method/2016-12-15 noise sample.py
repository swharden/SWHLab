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
import pickle

POINTS_PER_SEC=20000
POINTS_PER_MS=int(POINTS_PER_SEC/1000)
CHUNK_POINTS=POINTS_PER_MS*10 # size of Y pieces to calculate variance from
PERCENT_STEP=10 # percentile steps to display
COLORMAP=plt.get_cmap('jet') # which color scheme do we want to use?
#COLORMAP=plt.get_cmap('winter') # which color scheme do we want to use?

def plot_shaded_data(X,Y,variances,varianceX):
    """plot X and Y data, then shade its variance according to the colormap."""
    plt.plot(X,Y,color='k',lw=2)
    nChunks=int(len(Y)/CHUNK_POINTS)
    for i in range(0,100,PERCENT_STEP):
        varLimitLow=np.percentile(variances,i)
        varLimitHigh=np.percentile(variances,i+PERCENT_STEP)
        varianceIsAboveMin=np.where(variances>=varLimitLow)[0]
        varianceIsBelowMax=np.where(variances<=varLimitHigh)[0]
        varianceIsRange=[chunkNumber for chunkNumber in range(nChunks) \
                         if chunkNumber in varianceIsAboveMin \
                         and chunkNumber in varianceIsBelowMax]
        for chunkNumber in varianceIsRange:
            t1=chunkNumber*CHUNK_POINTS/POINTS_PER_SEC
            t2=t1+CHUNK_POINTS/POINTS_PER_SEC
            plt.axvspan(t1,t2,alpha=.3,color=COLORMAP(i/100),lw=0)

def show_variances(Y,variances,varianceX,logScale=False):
    """create some fancy graphs to show color-coded variances."""
    varSorted=sorted(variances)
        
    plt.figure(1,figsize=(10,7))
    plt.figure(2,figsize=(10,7))
    plt.figure(1)
    plt.subplot(211)
    plt.grid()
    plt.title("chronological variance")
    plt.ylabel("original data")
    plot_shaded_data(X,Y,variances,varianceX)
    plt.margins(0,.1)   
    plt.subplot(212)
    plt.ylabel("variance (pA) (log%s)"%str(logScale))
    plt.xlabel("time in sweep (sec)")
    plt.plot(varianceX,variances,'k-',lw=2)
    
    plt.figure(2)
    plt.ylabel("variance (pA) (log%s)"%str(logScale))
    plt.xlabel("chunk number")
    plt.title("sorted variance")
    plt.plot(varSorted,'k-',lw=2)
    
    for i in range(0,100,PERCENT_STEP):
        varLimitLow=np.percentile(variances,i)
        varLimitHigh=np.percentile(variances,i+PERCENT_STEP)
        label="%2d-%d percentile"%(i,i++PERCENT_STEP)
        color=COLORMAP(i/100)
        print("%s: variance = %.02f - %.02f"%(label,varLimitLow,varLimitHigh))
        plt.figure(1)
        plt.axhspan(varLimitLow,varLimitHigh,alpha=.5,lw=0,color=color,label=label)
        plt.figure(2)
        chunkLow=np.where(varSorted>=varLimitLow)[0][0]
        chunkHigh=np.where(varSorted>=varLimitHigh)[0][0]
        plt.axvspan(chunkLow,chunkHigh,alpha=.5,lw=0,color=color,label=label)
        
    for fignum in [1,2]:
        plt.figure(fignum)
        if logScale:
            plt.semilogy()
        plt.margins(0,0)
        plt.grid()
        if fignum is 2:
            plt.legend(fontsize=10,loc='upper left',shadow=True)
        plt.tight_layout()
        plt.savefig('2016-12-15-variance-%d-log%s.png'%(fignum,str(logScale)))
    plt.show()


    
    
if __name__=="__main__":

    # obtain X/Y data (abf.sweepY and abf.sweepX2)
    Y=np.load("sweepdata.npy")
    X=np.arange(len(Y))/POINTS_PER_SEC
    
    # determine how many pieces we will break out data into
    nChunks=int(len(Y)/CHUNK_POINTS)
    
    # reshape the 1d data into a 2d array with each chunk in a row
    chunks=np.reshape(Y[:nChunks*CHUNK_POINTS],(nChunks,CHUNK_POINTS))
        
    # calculate variances for each row
    variances=np.var(chunks,axis=1)
    varianceX=np.arange(len(variances))*CHUNK_POINTS/POINTS_PER_SEC
    
    # make graphs showing the variance distribution (regular and log)
    show_variances(Y,variances,varianceX)
    show_variances(Y,variances,varianceX,logScale=True)

    
    print("DONE")