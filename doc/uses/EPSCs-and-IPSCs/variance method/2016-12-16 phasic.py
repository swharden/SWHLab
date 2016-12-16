import os
import swhlab
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy as np

class ABF2(swhlab.ABF):
    def phasicTonic(self,m1=None,m2=None,chunkMs=10,
                    quietPercentile=10,histResolution=.1,
                    plotToo=False):
        """ 
        IMPORTANT: do this first!!
        self.kernel=self.kernel_gaussian(250)
        """
        # prepare our trimmed area of interest
        m1=0 if m1 is None else m1*self.pointsPerSec
        m2=len(abf.sweepY) if m2 is None else m2*self.pointsPerSec
        m1,m2=int(m1),int(m2)
        
        # obtain lowpassed data
        self.kernel=self.kernel_gaussian(250)
        Y=self.sweepYsmartbase()
        
        # calculate all histogram
        padding=50 # pA or mV of maximum expected deviation
        chunkPoints=int(chunkMs*self.pointsPerMs)
        nChunks=int(len(Y)/chunkPoints)
        histBins=int((padding*2)/histResolution)
        hist,bins=np.histogram(Y,bins=histBins,range=(-padding,padding))
        hist=hist.astype(np.float)

        # get baseline data from chunks with smallest variance
        chunks=np.reshape(Y[:nChunks*chunkPoints],(nChunks,chunkPoints))
        variances=np.var(chunks,axis=1)
        percentiles=np.empty(len(variances))
        for i,variance in enumerate(variances):
            percentiles[i]=sorted(variances).index(variance)/len(variances)*100
        blData=chunks[np.where(percentiles<=quietPercentile)[0]].flatten()
        
        # generate standard curve
        sigma=np.sqrt(np.var(blData))
        center=np.average(blData)
        blCurve=mlab.normpdf(bins[:-1],center,sigma)
        
        # pull the baseline curve up to the height of the histogram
        blCurve=blCurve/max(blCurve)
        #blCurve=blCurve*np.percentile(hist,98)
        blCurve=blCurve*max(hist)
        
        # blank out the center points (sigma on each side of the mean)
        blankPoints=int(2*sigma/histResolution)
        centerI=int(len(hist)/2)
        for i in range(blankPoints):
            hist[centerI-i]=np.nan
            hist[centerI+i]=np.nan
        
        #print("sigma:",sigma)
        
        # determine this sweep's negative, positive, and total phasic current
        diff=hist-blCurve
        #diff=np.abs(bins[:-1]*diff)
               
        if plotToo:
            plt.figure(figsize=(7,7))
            plt.subplot(211)
            plt.title(abf.ID+" phasic analysis")
            plt.ylabel("bin counts")
            plt.plot(bins[:-1],hist,'.',alpha=.3)
            plt.plot(bins[:-1],blCurve,lw=3,alpha=.5,color='r')
            plt.margins(0,.1)
            plt.subplot(212)
            plt.title("baseline subtracted")
            plt.ylabel("bin counts")
            plt.xlabel("data points (%s)"%abf.units)
            plt.plot(bins[:-1],diff,'.',alpha=.5,color='b')
            #plt.plot(bins[:-1],swhlab.common.lowpass(diff),color='b',alpha=.5,lw=3)
            plt.axhline(0,lw=3,alpha=.5,color='r')
            plt.axvline(0,lw=3,alpha=.5,color='r')
            plt.margins(0,.1)
            plt.tight_layout()
            plt.show()
    

if __name__=="__main__":
    abfPath=r"X:\Data\2P01\2016\2016-09-01 PIR TGOT"
    if False:
        abf=ABF2(os.path.join(abfPath,"16d16005.abf"))
    else:
        abf=ABF2(os.path.join(abfPath,"16d16007.abf"))
        abf.setsweep(266)    
    
    abf.phasicTonic(m1=.5,plotToo=True)
    
    #plt.figure(figsize=(15,5))
    #plt.plot(phasicTonic(abf,m1=.5))
    #plt.show()
    
    print("DONE")