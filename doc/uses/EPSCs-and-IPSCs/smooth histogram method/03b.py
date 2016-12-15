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

def kernel_gaussian(size=100, sigma=None):
    sigma=size/10 if sigma is None else int(sigma)
    points=np.exp(-np.power(np.arange(size)-size/2,2)/(2*np.power(sigma,2)))
    return points/sum(points)

def analyzeSweep(abf,plotColor=None):    
    
    Y=abf.sweepYsmartbase()
    Y=Y[abf.pointsPerSec*.5:]

    # create a 1 Kbin histogram with bins centered around 3x the SD from the mean
    AV,SD=np.average(Y),np.std(Y)
    B1,B2=AV-SD*3,AV+SD*3
    nBins=1000
    hist, bin_edges = np.histogram(Y, density=True, bins=nBins, range=(B1,B2))
    histSmooth=np.convolve(hist,kernel_gaussian(nBins/2),mode='same')
        
    if plotColor:
        plt.plot(bin_edges[:-1],histSmooth,'-',alpha=.3,color=plotColor,lw=2)
    
    return
    
if __name__=="__main__":
    abfFile=R"C:\Users\scott\Documents\important\demodata\abfs\16d07022.abf"
    abf=swhlab.ABF(abfFile)
    abf.kernel=abf.kernel_gaussian(sizeMS=500) # needed for smart base
    
    plt.figure(figsize=(10,10))
    plt.grid()
    plt.title("10 sweeps baseline (blue), in drug (blue), and washout (yellow)")
    plt.ylabel("power")
    plt.xlabel(abf.units2)
    plt.axhline(0,color='k')
    
    for sweep in [(5*60/abf.sweepLength)+x for x in range(10)]:
        print("plotting sweep",sweep)
        abf.setsweep(sweep)
        analyzeSweep(abf,plotColor='b')
        
    for sweep in [(6.5*60/abf.sweepLength)+x for x in range(10)]:
        print("plotting sweep",sweep)
        abf.setsweep(sweep)
        analyzeSweep(abf,plotColor='r')
       
    for sweep in [(12*60/abf.sweepLength)+x for x in range(12)]:
        print("plotting sweep",sweep)
        abf.setsweep(sweep)
        analyzeSweep(abf,plotColor='y')
        
    plt.show()
    print("DONE")
