"""
Plot some sweeps where optogenetic blue light stimulation (BLS)
was applied by a digital output.
"""

import os
import sys
if not os.path.abspath('../../../') in sys.path:
    sys.path.append('../../../')
import matplotlib.pyplot as plt
import numpy as np
import swhlab
import webinspect
import glob

def BLS_average(abf):
    T1,T2=epochTimes(abf)
    Tdiff=max([T2-T1,.1])
    X1,X2=T1-Tdiff,T2+Tdiff
    I1,I2=X1*abf.pointsPerSec,X2*abf.pointsPerSec

    plt.figure(figsize=(10,10))
    chunks=np.empty((abf.sweeps,I2-I1))
    Xs=np.array(abf.sweepX2[I1:I2])
    for sweep in abf.setsweeps():
        chunks[sweep]=abf.sweepY[I1:I2]
        plt.subplot(211)
        plt.plot(Xs,chunks[sweep],alpha=.2,color='.5',lw=2)
        plt.subplot(212)
        plt.plot(Xs,chunks[sweep]+100*sweep,alpha=.5,color='b',lw=2)

    plt.subplot(211)
    plt.plot(Xs,np.average(chunks,axis=0),alpha=.5,lw=2)
    plt.title("%s.abf - BLS - average of %d sweeps"%(abf.ID,abf.sweeps))
    plt.ylabel(abf.units2)
    plt.axvspan(T1,T2,alpha=.1,color='y',lw=0)
    plt.axis([X1,X2,None,None])

    plt.subplot(212)
    plt.xlabel("time (sec)")
    plt.ylabel("stacked sweeps")
    plt.axvspan(T1,T2,alpha=.1,color='y',lw=0)
    plt.axis([X1,X2,None,None])

    plt.tight_layout()
    plt.show()
    plt.close('all')

if __name__=="__main__":

    fname=r"X:\Data\2P01\2016\2017-01-09 AT1\17109009.abf" #0501
#    fname=r"X:\Data\2P01\2016\2017-01-09 AT1\"17109013.abf"#0502
    abf=swhlab.ABF(fname)

    if abf.protocomment in ['0501','0502']:
        BLS_average(abf)





    print("DONE")