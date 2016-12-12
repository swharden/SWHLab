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

if __name__=="__main__":

    # first let's load our X,Y data
    abfFile=R"X:\Data\DIC1\2013\08-2013\08-16-2013-DP\13816004.abf"
    abf=swhlab.ABF(abfFile) # defaults to sweep 0
    Xs,Ys=abf.sweepX,abf.sweepY

    # move time domain data into the frequency domain
    FFT=np.fft.fft(Ys) # these are i/j vectors starting at 0Hz
    baseFrequency=60 # frequency (Hz) to silence

    for i in range(50): # first 50 harmonics
        I=int(baseFrequency*i+baseFrequency*len(Ys)/abf.pointsPerSec)
        FFT[I],FFT[-I]=0+0j,0+0j # silence real and imaginary


    # move frequency domain data back into the time domain
    Ys2=np.fft.ifft(FFT)

    # plot the original / improved trace
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

    print("DONE")
