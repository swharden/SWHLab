"""scripts to help automated analysis of basic protocols."""
import logging
from abf import ABF
from plot import ABFplot
import plot as plotmodule
import os
import glob
import index
from ap import AP
import matplotlib.pyplot as plt
import version
import numpy as np

SQUARESIZE=8

def proto_unknown(theABF):
    """protocol: unknown."""
    abf=ABF(theABF)
    abf.log.info("analyzing as an unknown protocol")
    plot=ABFplot(abf)
    plot.rainbow=False
    plot.title=None
    plot.figure_height,plot.figure_width=SQUARESIZE,SQUARESIZE
    plot.traceColor='m' # magenta if unknown protocol
    plot.kwargs["lw"]=.5
    plot.figure_chronological()
    plotmodule.frameAndSave(abf,"UNKNOWN")
        
def proto_0101(theABF):
    abf=ABF(theABF)
    abf.log.info("analyzing as an IC tau")
    #plot=ABFplot(abf)

    plt.figure(figsize=(SQUARESIZE,SQUARESIZE))
    plt.grid()
    plt.ylabel("relative potential (mV)")
    plt.xlabel("time (sec)")
    m1,m2=[.05,.1]
    for sweep in range(abf.sweeps):
        abf.setsweep(sweep)
        plt.plot(abf.sweepX2,abf.sweepY-abf.average(m1,m2),alpha=.2,color='#AAAAFF')
    average=abf.averageSweep()
    average-=np.average(average[m1**abf.pointsPerSec:m2*abf.pointsPerSec])
    plt.plot(abf.sweepX2,average,color='b',lw=2,alpha=.5)
    plt.axvspan(m1,m2,color='r',ec=None,alpha=.1)
    plt.axhline(0,color='r',ls="--",alpha=.5,lw=2)
    plt.margins(0,.1)
    
    # save it
    plt.tight_layout()
    plotmodule.frameAndSave(abf,"IC tau")
    plt.close('all')
    

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
    plt.figure(figsize=(SQUARESIZE,SQUARESIZE))
    ax1=plt.subplot(221)
    plt.ylabel(abf.units2)
    ax2=plt.subplot(222,sharey=ax1)
    ax3=plt.subplot(223)
    plt.ylabel(abf.unitsD2)
    ax4=plt.subplot(224,sharey=ax3)  

    # put data in each subplot    
    for sweep in range(abf.sweeps):
        abf.setsweep(sweep)
        ax1.plot(abf.sweepX,abf.sweepY,color='b',lw=.25)
        ax2.plot(abf.sweepX,abf.sweepY,color='b')  
        ax3.plot(abf.sweepX,abf.sweepD,color='r',lw=.25)   
        ax4.plot(abf.sweepX,abf.sweepD,color='r')   

    # modify axis
    for ax in [ax1,ax2,ax3,ax4]: # everything
        ax.margins(0,.1)
        ax.grid(alpha=.5)        
    for ax in [ax3,ax4]: # only derivative APs
        ax.axhline(-100,color='r',alpha=.5,ls="--",lw=2)
    for ax in [ax2,ax4]: # only zoomed in APs
        ax.get_yaxis().set_visible(False)
    ax2.axis([firstAP-.25,firstAP+.25,None,None])
    ax4.axis([firstAP-.01,firstAP+.01,None,None])

    # show message from first AP
    firstAP=ap.APs[0]
    msg="\n".join(["%s = %s"%(x,str(firstAP[x])) for x in sorted(firstAP.keys()) if not "I" in x[-2:]])               
    plt.subplot(221)
    plt.gca().text(0.02, 0.98, msg, transform= plt.gca().transAxes, fontsize=10, verticalalignment='top', family='monospace')
    
    # save it
    plt.tight_layout()
    plotmodule.frameAndSave(abf,"AP shape")
    plt.close('all')

def proto_gain(theABF,stepSize=25,startAt=-100):
    """protocol: gain function of some sort. step size and start at are pA."""
    abf=ABF(theABF)
    abf.log.info("analyzing as an IC ramp")
    plot=ABFplot(abf)
    plot.kwargs["lw"]=.5
    plot.title=""
    currents=np.arange(abf.sweeps)*stepSize-startAt
    
    # AP detection
    ap=AP(abf) 
    ap.detect_time1=.1
    ap.detect_time2=.7
    ap.detect()
       
    # stacked plot
    plt.figure(figsize=(SQUARESIZE,SQUARESIZE))
    
    ax1=plt.subplot(221)
    plot.figure_sweeps()
    
    ax2=plt.subplot(222)
    ax2.get_yaxis().set_visible(False)
    plot.figure_sweeps(offsetY=150)   
    
    # add vertical marks to graphs:
    for ax in [ax1,ax2]:
        for limit in [ap.detect_time1,ap.detect_time2]:
            ax.axvline(limit,color='r',ls='--',alpha=.5,lw=2)
    
    # make stacked gain function
    ax4=plt.subplot(223)
    plt.ylabel("frequency (Hz)")
    plt.ylabel("seconds")
    plt.grid(alpha=.5)
    freqs=ap.get_bySweep("freqs")
    times=ap.get_bySweep("times")
    for i in range(abf.sweeps):
        if len(freqs[i]):
            plt.plot(times[i][:-1],freqs[i],'-',alpha=.5,lw=2,
                     color=plot.getColor(i/abf.sweeps))
                
    # make gain function graph
    ax4=plt.subplot(224)
    ax4.grid(alpha=.5)
    plt.plot(currents,ap.get_bySweep("median"),'b.-',label="median")
    plt.plot(currents,ap.get_bySweep("firsts"),'g.-',label="first")
    plt.xlabel("applied current (pA)")
    plt.legend(loc=2,fontsize=10)
    plt.axhline(40,color='r',alpha=.5,ls="--",lw=2)
    plt.margins(.02,.1)
    
    # save it
    plt.tight_layout()
    plotmodule.frameAndSave(abf,"AP Gain (start %d, step %d)"%(startAt,stepSize))
    plt.close('all')
    
def proto_0113(theABF):
    proto_gain(theABF,25)
    
def proto_0114(theABF):
    proto_gain(theABF,100)
    
def proto_0201(theABF):
    """protocol: membrane test."""
    abf=ABF(theABF)
    abf.log.info("analyzing as a membrane test")
    plot=ABFplot(abf)
    plot.figure_height,plot.figure_width=SQUARESIZE,SQUARESIZE
    plot.figure_sweeps()
        
    # save it
    plt.tight_layout()
    plotmodule.frameAndSave(abf,"membrane test")
    plt.close('all')
                
def proto_0202(theABF):
    """protocol: MTIV."""
    abf=ABF(theABF)
    abf.log.info("analyzing as MTIV")
    plot=ABFplot(abf)
    plot.figure_height,plot.figure_width=SQUARESIZE,SQUARESIZE
    plot.title=""
    plot.kwargs["alpha"]=.6
    plot.figure_sweeps()
    
    # frame to uppwer/lower bounds, ignoring peaks from capacitive transients
    abf.setsweep(0)
    plt.axis([None,None,abf.average(.9,1)-100,None])
    abf.setsweep(-1)
    plt.axis([None,None,None,abf.average(.9,1)+100])
    
    # save it
    plt.tight_layout()
    plotmodule.frameAndSave(abf,"MTIV")
    plt.close('all')
    
def proto_0203(theABF):
    """protocol: vast IV."""
    abf=ABF(theABF)
    abf.log.info("analyzing as a fast IV")
    plot=ABFplot(abf)
    plot.title=""
    m1,m2=.7,1
    plt.figure(figsize=(SQUARESIZE,SQUARESIZE/2))

    plt.subplot(121)
    plot.figure_sweeps()
    plt.axvspan(m1,m2,color='r',ec=None,alpha=.1)

    plt.subplot(122)
    plt.grid(alpha=.5)
    Xs=np.arange(abf.sweeps)*5-110
    Ys=[]
    for sweep in range(abf.sweeps):
        abf.setsweep(sweep)
        Ys.append(abf.average(m1,m2))
    plt.plot(Xs,Ys,'.-',ms=10)
    plt.axvline(-70,color='r',ls='--',lw=2,alpha=.5)
    plt.axhline(0,color='r',ls='--',lw=2,alpha=.5)
    plt.margins(.1,.1)
    plt.xlabel("membrane potential (mV)")
        
    # save it
    plt.tight_layout()
    plotmodule.frameAndSave(abf,"fast IV")
    plt.close('all')
    
def proto_0404(theABF):
    proto_avgRange(theABF,1.0,1.1)
    
def proto_avgRange(theABF,m1=1.0,m2=1.1):
    """experiment: VC ramp."""
    abf=ABF(theABF)
    abf.log.info("analyzing as a fast IV")
    plot=ABFplot(abf)
        
    # define range to average
    m1=1.0
    m2=1.1
    
    plt.figure(figsize=(SQUARESIZE,SQUARESIZE))
    
    plt.subplot(211)
    plot.title="first sweep"
    plot.figure_sweep()
    plt.axvspan(m1,m2,color='r',ec=None,alpha=.1)
    
    plt.subplot(212)
    plt.grid(alpha=.5)
    Ts=np.arange(abf.sweeps)*abf.sweepInterval
    Ys=np.empty(abf.sweeps)*np.nan
    for sweep in range(abf.sweeps):
        Ys[sweep]=abf.average(m1,m2,setsweep=sweep)
    for i,t in enumerate(abf.comment_times):
        plt.axvline(t/60,color='r',alpha=.5,lw=2,ls='--')
    plt.plot(Ts/60,Ys,'.')
    plt.title(str(abf.comment_tags))
    plt.ylabel(abf.units2)
    plt.xlabel("minutes")
        
    plt.tight_layout()
    plotmodule.frameAndSave(abf,"sweep vs average")
    plt.close('all')
    
    
    
def analyze(fname):
    """given a filename or ABF object, try to analyze it."""
    abf=ABF(fname) # ensure it's a class
    runFunction="proto_unknown"
    if "proto_"+abf.protocomment in globals():
        runFunction="proto_"+abf.protocomment
    abf.log.debug("running %s()"%(runFunction))
    plt.close('all') # get ready
    globals()[runFunction](abf) # run that function

if __name__=="__main__":
    folder=r"C:\Users\scott\Documents\important\abfs"
    analyze(os.path.join(folder,'16o14025'+'.abf'))
    print("DONE")