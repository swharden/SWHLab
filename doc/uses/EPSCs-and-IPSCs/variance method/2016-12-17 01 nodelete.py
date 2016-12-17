import os
import sys
sys.path.append("../../../../")
import swhlab
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy as np

class ABF2(swhlab.ABF):
    def phasicTonic(self,m1=None,m2=None,chunkMs=50,quietPercentile=10,
                    histResolution=1,plotToo=False):
        """ 
        let's keep the chunkMs as high as we reasonably can. 50ms is good.
        Things get flakey at lower numbers like 10ms.
        
        IMPORTANT! for this to work, prevent 0s from averaging in, so keep
        bin sizes well above the data resolution.
        """
        # prepare sectioning values to be used later
        m1=0 if m1 is None else m1*self.pointsPerSec
        m2=len(abf.sweepY) if m2 is None else m2*self.pointsPerSec
        m1,m2=int(m1),int(m2)
        
        # prepare histogram values to be used later
        padding=50 # pA or mV of maximum expected deviation
        chunkPoints=int(chunkMs*self.pointsPerMs)
        histBins=int((padding*2)/histResolution)
        
        # center the data at 0 using peak histogram, not the mean
        Y=self.sweepY[m1:m2]
        hist,bins=np.histogram(Y,bins=2*padding)
        Yoffset=bins[np.where(hist==max(hist))[0][0]]
        Y=Y-Yoffset # we don't have to, but PDF math is easier
        
        # calculate all histogram
        nChunks=int(len(Y)/chunkPoints)
        hist,bins=np.histogram(Y,bins=histBins,range=(-padding,padding))
        Xs=bins[1:]

        # get baseline data from chunks with smallest variance
        chunks=np.reshape(Y[:nChunks*chunkPoints],(nChunks,chunkPoints))
        variances=np.var(chunks,axis=1)
        percentiles=np.empty(len(variances))
        for i,variance in enumerate(variances):
            percentiles[i]=sorted(variances).index(variance)/len(variances)*100
        blData=chunks[np.where(percentiles<=quietPercentile)[0]].flatten()
        
        # generate the standard curve and pull it to the histogram height
        sigma=np.sqrt(np.var(blData))
        center=np.average(blData)
        blCurve=mlab.normpdf(Xs,center,sigma)
        blCurve=blCurve*max(hist)/max(blCurve)
                
        # determine this sweep's negative, positive, and total phasic current
        diff=hist-blCurve
        diffLPF=swhlab.common.lowpass(diff)
               
        if plotToo:
            plt.figure(figsize=(15,5))
            plt.plot(Y)
            
            plt.figure(figsize=(7,7))
            plt.subplot(211)
            plt.title(abf.ID+" phasic analysis")
            plt.ylabel("bin counts")
            plt.plot(Xs,hist,'.',alpha=.3)
            plt.plot(Xs,blCurve,lw=3,alpha=.5,color='r')
            plt.margins(0,.1)
            plt.subplot(212)
            plt.title("baseline subtracted")
            plt.ylabel("bin counts")
            plt.xlabel("data points (%s)"%abf.units)
            plt.plot(Xs,diff,'.',alpha=.5,color='.5')
            plt.plot(Xs,diffLPF,color='b',alpha=.8,lw=2)
            plt.axhline(0,lw=3,alpha=.5,color='r')
            plt.axvline(0,lw=3,alpha=.5,color='k')
            plt.margins(0,.1)
            plt.tight_layout()
            plt.show()
            
        return [Xs,diffLPF]

if __name__=="__main__":
    #abfPath=r"X:\Data\2P01\2016\2016-09-01 PIR TGOT"
    abfPath=r"C:\Users\scott\Documents\important\demodata"   
    abf=ABF2(os.path.join(abfPath,"16d16007.abf"))
    #abf=ABF2(os.path.join(abfPath,"abfs/16o14024.abf"))
    
#    print(abf.comment_tags)
#    print(abf.comment_sweeps)
    
    abf.setsweep(266)
    plt.plot(abf.sweepX2[.5*abf.pointsPerSec:],abf.sweepY[.5*abf.pointsPerSec:])
    abf.phasicTonic(m1=.5,plotToo=True)
    
#            
#    plt.figure(figsize=(10,5))
#    plt.title("excitation / inhibition")
#    plt.axhline(0,color='k')
#    plt.axvline(0,color='k')
#    plt.grid()
#    for sweep,label in [[200,"baseline"],[220,"drug"],[350,"wash"]]:
#        abf.setsweep(sweep)        
#        Xs,Ys=abf.phasicTonic(m1=.5)
#        plt.plot(Xs,Ys,alpha=.5,lw=3,label="sw%d (%s)"%(sweep,label))
#    plt.legend(fontsize=10,loc='upper left',shadow=True)
#    plt.margins(0,.1)
#    plt.show()
    
    print("DONE")