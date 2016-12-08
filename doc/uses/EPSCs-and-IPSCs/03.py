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
import matplotlib.pyplot as plt
import numpy as np

import warnings # suppress VisibleDeprecationWarning warning 
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning) 

def analyzeSweep(abf,plotToo=True):    
    
    #abf.sweepY[:abf.pointsPerSec*.3]=np.nan # silence out the memtest part
    
    Yorig=abf.sweepY
    Y=abf.sweepYsmartbase()
    X=abf.sweepX2
    X[:abf.pointsPerSec*.3]=np.nan # silence out the memtest part
    #Y[:abf.pointsPerSec*.3]=np.nan # silence out the memtest part
    
    if plotToo:
        plt.figure(figsize=(10,5))
        plt.subplot(211)
        plt.grid()
        plt.plot(X,Yorig,alpha=.5)
        plt.plot(X,abf.sweepYfiltered(),alpha=.8,color='k',lw=1)
        plt.margins(0,.1)
        
        plt.subplot(212)
        plt.grid()
        plt.plot(X,abf.sweepYsmartbase(),alpha=.5)
        plt.axhline(0,alpha=.8,color='k')
        plt.margins(0,.1)
        
        plt.tight_layout()
        plt.show()
    
    
#    AV=np.average(Y)
#    SD=np.std(Y)
#        
#    print((AV,AV-SD*5,AV+SD*5))
#    
#    hist, bin_edges = np.histogram(Y, density=True, bins=100)
#    plt.figure(figsize=(5,5))
#    plt.grid()
#    plt.plot(bin_edges[:-1],hist,'.')
#    for x in [AV,AV-SD,AV+SD]:
#        plt.axvline(x,color='r',ls='--',alpha=.5,lw=2)
#    plt.show()
    
    return
    
if __name__=="__main__":
    abfFile=R"C:\Users\scott\Documents\important\demodata\abfs\16d07022.abf"
    abf=swhlab.ABF(abfFile)
    abf.kernel=abf.kernel_gaussian(sizeMS=500) # needed for smart base
    abf.setsweep(200)
    analyzeSweep(abf)
    print("DONE")
