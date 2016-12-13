"""Same as 01.py, but reports speed"""

import os
import sys
if not os.path.abspath('../../../') in sys.path:
    sys.path.append('../../../')
import swhlab
import matplotlib.pyplot as plt
import numpy as np
import time

if __name__=="__main__":
    abfFile=R"X:\Data\DIC1\2013\08-2013\08-16-2013-DP\13816004.abf"
    abf=swhlab.ABF(abfFile) # defaults to sweep 0
    print("analyzing %d sweeps (%.02f sec each)"%(abf.sweeps,abf.sweepLength))
    times=[]
    for sweep in abf.setsweeps():
        t1=time.clock()
        baseFrequency=60 # frequency (Hz) to silence
        FFT=np.fft.fft(abf.sweepY) # frequency data (i/j vectors starting at 0Hz)
        for i in range(50): # first 50 odd harmonics
            I=int(baseFrequency*i+baseFrequency*len(abf.sweepY)/abf.pointsPerSec)
            FFT[I],FFT[-I]=0,0 # remember to silence from both ends of the FFT
        Ys2=np.fft.ifft(FFT) # all done
        times.append(time.clock()-t1)
    times=np.array(times)*1000 # now in ms
    print("analysis took %.02f +/- %.02f ms per sweep"%(np.average(times),np.std(times)))

# analyzing 60 sweeps (5.00 sec each)
# analysis took 6.47 +/- 1.71 ms per sweep