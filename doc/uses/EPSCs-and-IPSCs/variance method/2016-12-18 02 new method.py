"""
let's be simple
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
    
    def simple(self):
        
        # RMS percentile
        perRMS=50
        perPSC=100-perRMS
        percentileUp=100-perPSC/2
        percentileDown=perPSC/2
        
        # get moving window baseline subtracted data
        X,Y=self.sweepX2,self.sweepY
        Y[:.5*self.pointsPerSec]=np.nan
        
        # figure out what our noise floor should be
        noise=np.empty(len(Y))
        noise[:]=np.nan
        noiseUp=np.copy(noise)
        noiseDown=np.copy(noise)
        pad=self.pointsPerMs*50
        for i in range(len(noise)):
            if len(Y[i-pad:i+pad]):
                noiseUp[i]=np.percentile(Y[i-pad:i+pad],percentileUp)
                noiseDown[i]=np.percentile(Y[i-pad:i+pad],percentileDown)
        noiseCenter=np.nanmean([noiseUp,noiseDown],axis=0)
        noiseCenterPoint=np.nanmean(noiseCenter)
        Y=Y-noiseCenter
        
        # create the plot
        plt.figure(figsize=(15,5))
        plt.plot(X,Y,alpha=.5)  
        plt.axhline(0,color='k',lw=2)
        plt.axhline(np.nanmean(noiseUp)-noiseCenterPoint,color='r',lw=2)
        plt.axhline(np.nanmean(noiseDown)-noiseCenterPoint,color='r',lw=2)
        plt.margins(0,.1)
        plt.show()
    
if __name__=="__main__":
    #abfPath=r"X:\Data\2P01\2016\2016-09-01 PIR TGOT"
    abfPath=r"C:\Users\scott\Documents\important\demodata"   
    abf=ABF2(os.path.join(abfPath,"16d14036.abf"))      
    #abf=ABF2(os.path.join(abfPath,"16d16007.abf"))
    
    #abf.setsweep(100)
    abf.setsweep(266)
    abf.simple()
    
    print("DONE")