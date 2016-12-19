"""
let's just graph mean and mode with time.
also graph variance with time.

as mode moves around mean, it shows EPSC/IPSC balance.

Could the ratio be multiplied by the variance to return it to original magnitude?

"""

import os
import sys
sys.path.append("../../../../")
import swhlab
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy as np
import time


class ABF2(swhlab.ABF):
    def phasicTonic(self,m1=None,m2=None):
        m1=0 if m1 is None else m1*self.pointsPerSec
        m2=len(abf.sweepY) if m2 is None else m2*self.pointsPerSec
        m1,m2=int(m1),int(m2)
        Y=self.sweepY[m1:m2]
        Y=Y-np.average(Y)
        return [np.average(Y),np.median(Y),np.var(Y),np.std(Y)]

if __name__=="__main__":
    #abfPath=r"X:\Data\2P01\2016\2016-09-01 PIR TGOT"
    abfPath=r"C:\Users\scott\Documents\important\demodata"   
    abf=ABF2(os.path.join(abfPath,"16d14036.abf"))      
    #abf=ABF2(os.path.join(abfPath,"16d16007.abf"))

    Xs=np.arange(abf.sweeps)*abf.sweepLength
    data=np.empty((abf.sweeps,4))
    for sweep in abf.setsweeps():
        data[sweep]=abf.phasicTonic(.5)
    print(data)
    
    plt.figure(figsize=(10,5))
    plt.grid()
    plt.axhline(0,lw=2,color='k')
    plt.plot(Xs,data[:,1],label="median")
#    plt.plot(Xs,data[:,3],label="variance")
    plt.plot(Xs,data[:,1]+data[:,3])
    plt.plot(Xs,data[:,1]-data[:,3])
    for sweep in abf.comment_times:
        plt.axvline(sweep,lw=5,alpha=.5,color='g',ls='--')
    
    plt.margins(0,.1)
    plt.axis([None,None,-15,15])
    plt.legend()
    plt.show()
    
    print("DONE")
    
    