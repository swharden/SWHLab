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
    def sweepYfilteredHisto(self):
        pad=abf.pointsPerMs*20 # 10ms on each side
        smooth=np.empty(len(self.sweepY))
        smooth[:]=np.nan
        for i in range(pad,len(self.sweepY)):
            #smooth[i]=np.mean(self.sweepY[i-pad:i])
            smooth[i]=np.median(self.sweepY[i-pad:i])
        return smooth

if __name__=="__main__":
    #abfPath=r"X:\Data\2P01\2016\2016-09-01 PIR TGOT"
    abfPath=r"C:\Users\scott\Documents\important\demodata"   
    #abf=swhlab.ABF(os.path.join(abfPath,"16d14036.abf"))      
    abf=ABF2(os.path.join(abfPath,"16d14036.abf"))      
    #abf=ABF2(os.path.join(abfPath,"16d16007.abf"))

    abf.setsweep(266)
    abf.sweepY[:abf.pointsPerSec*.5]=np.nan
    abf.kernel=abf.kernel_gaussian(100)
    
    #Y=abf.sweepY[.5*abf.pointsPerSec:]
    #X=abf.sweepX2[:-.5*abf.pointsPerSec]
    
    plt.figure(figsize=(15,10))
    
    ax1=plt.subplot(311)
    plt.plot(abf.sweepX2,abf.sweepY,color='.5',alpha=.5)
    plt.plot(abf.sweepX2,abf.sweepYfiltered(),color='b',alpha=.5,lw=3)
    plt.plot(abf.sweepX2,abf.sweepYfilteredHisto(),color='r',alpha=.5,lw=3)
    plt.margins(0,.1)
    
    plt.subplot(312,sharex=ax1)
    plt.plot(abf.sweepX2,abf.sweepY-abf.sweepYfiltered(),color='.5',alpha=.5)
    plt.axhline(0,color='b',alpha=.5,lw=3)
    plt.margins(0,.1)
    
    plt.subplot(313,sharex=ax1)
    plt.plot(abf.sweepX2,abf.sweepY-abf.sweepYfilteredHisto(),color='.5',alpha=.5)
    plt.axhline(0,color='r',alpha=.5,lw=3)
    plt.margins(0,.1)
    
    plt.axis([.5,None,None,None])
    plt.show()
    
    print("DONE")
    
    
    
    