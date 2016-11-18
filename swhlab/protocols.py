"""scripts to help automated analysis of basic protocols."""

from abf import ABF
from plot import ABFplot
import os
import glob
import index
from ap import AP
import matplotlib.pyplot as plt

def proto_unknown(theABF):
    """protocol: unknown."""
    abf=ABF(theABF)
    abf.log.info("analyzing as an unknown protocol")

def proto_0111(theABF):
    """protocol: IC ramp for AP shape analysis."""
    abf=ABF(theABF)
    abf.log.info("analyzing as an IC ramp")
    
    # AP detection
    ap=AP(abf) 
    ap.detect()
    firstAP=ap.APs[0]["T"]
    
    # also calculate derivative for each sweep
    abf.derivative=True 
    
    # create the multi-plot figure
    plt.figure(figsize=(8,8))
    ax1=plt.subplot(221)
    plt.ylabel(abf.units2)
    ax2=plt.subplot(222)
    ax3=plt.subplot(223)
    plt.ylabel(abf.unitsD2)
    ax4=plt.subplot(224)  

    # put data in each subplot    
    for sweep in range(abf.sweeps):
        abf.setsweep(sweep)
        ax1.plot(abf.sweepX,abf.sweepY,color='b')  
        ax2.plot(abf.sweepX,abf.sweepY,color='b')  
        ax3.plot(abf.sweepX,abf.sweepD,color='r')   
        ax4.plot(abf.sweepX,abf.sweepD,color='r')   

    # modify axis
    for ax in [ax1,ax2,ax3,ax4]: # everything
        ax.grid(alpha=.5)        
    for ax in [ax1,ax2]: # only raw APs
        ax.axis([None,None,-100,100])
    for ax in [ax3,ax4]: # only derivative APs
        ax.axis([None,None,-300,500])    
        ax.axhline(-100,color='r',alpha=.5,ls="--",lw=2)
    for ax in [ax2,ax4]: # only zoomed in APs
        ax.get_yaxis().set_visible(False)
    ax2.axis([firstAP-.25,firstAP+.25,None,None])
    ax4.axis([firstAP-.01,firstAP+.01,None,None])

    # show message from first AP
#    firstAP=ap.APs[0]
#    msg="\n".join(["%s = %s"%(x,str(firstAP[x])) for x in firstAP.keys() if not "I" in x[-2:]])               
#    props = dict(boxstyle='round', facecolor='wheat', alpha=0.2)    
#    plt.gca().text(0.05, 0.95, msg, transform= plt.gca().transAxes, 
#            fontsize=11, verticalalignment='top', bbox=props)
            
    #plot.save("APramp")
    #plt.tight_layout()
    plt.show()
    return

def analyze(fname):
    """given a filename or ABF object, try to analyze it."""
    abf=ABF(fname) # ensure it's a class
    print("CHEKCING","proto_"+abf.protocomment)
    runFunction="proto_unknown"
    if "proto_"+abf.protocomment in globals():
        runFunction="proto_"+abf.protocomment
    abf.log.debug("running %s()"%(runFunction))
    plt.close('all') # get ready
    globals()[runFunction](abf) # run that function

if __name__=="__main__":
#    for fname in glob.glob(r"C:\Users\swharden\Desktop\limited\*.abf")[:5]:
#        analyze(fname)
    analyze(r"C:\Users\swharden\Desktop\limited\16923038.abf")
    print("DONE")