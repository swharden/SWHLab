"""Example how to reduce 60 Hz "hum" in electrophysiological recordings"""

import os
import sys
if not os.path.abspath('../../../') in sys.path: # in case our module isn't installed (running from this folder)
    sys.path.append('../../../') # helps spyder get docs
import swhlab
import matplotlib.pyplot as plt
import numpy as np

if __name__=="__main__":
    abfFile=R"X:\Data\DIC1\2013\08-2013\08-16-2013-DP\13816004.abf"
    abf=swhlab.ABF(abfFile) # defaults to sweep 0
    Xs,Ys=abf.sweepX,abf.sweepY # we have X,Y data to work with
    baseFrequency=60 # frequency (Hz) to silence

    ### convert to frequency domain, silence harmonics, then back to time domain
    FFT=np.fft.fft(Ys) # frequency data (i/j vectors starting at 0Hz)
    for i in range(50): # first 50 odd harmonics
        I=int(baseFrequency*i+baseFrequency*len(Ys)/abf.pointsPerSec)
        FFT[I],FFT[-I]=0,0 # remember to silence from both ends of the FFT
    Ys2=np.fft.ifft(FFT) # all done

    ### plot the original and new data in X/Y-linked subplots
    plt.figure(figsize=(15,10))
    ax1=plt.subplot(211)
    plt.grid()
    plt.title("Original Data")
    plt.plot(Xs,Ys,alpha=.75)
    plt.margins(0,.1)
    plt.subplot(212,sharex=ax1,sharey=ax1)
    plt.grid()
    plt.title("Harmonic Suppression")
    plt.plot(Xs,Ys2,alpha=.75)
    plt.margins(0,.1)
    plt.tight_layout()
    plt.show()
