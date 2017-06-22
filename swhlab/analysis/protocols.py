"""
scripts to help automated analysis of basic protocols.

All output data should be named:
    * 12345678_experiment_thing.jpg (time course experiment, maybe with drug)
    * 12345678_intrinsic_thing.jpg (any intrinsic property)
    * 12345678_micro_thing.jpg (anything copied, likely a micrograph)
    * 12345678_data_aps.npy (data stored in a numpy array)
    * 12345678_data_IVfast.npy (data stored in a numpy array)


INFORMAL GOAL: make all figures SQUARESIZE in height. Width is variable.
"""

import os
import sys
sys.path.append(r"C:\Users\swharden\Documents\GitHub\SWHLab") # for local run
if not os.path.abspath('../../') in sys.path:
    sys.path.append('../../')
import glob
import matplotlib.pyplot as plt
import numpy as np

import swhlab
from swhlab import ABF
from swhlab.plotting import ABFplot
from swhlab.plotting.core import frameAndSave
from swhlab.analysis.ap import AP
import swhlab.plotting.core
import swhlab.common as cm
import swhlab.indexing.imaging as imaging

#from swhlab.swh_abf import ABF
#import swhlab.swh_index as index
#from swhlab.swh_ap import AP
#import swhlab.swh_plot
#from swhlab.swh_plot import ABFplot
#from swhlab.swh_plot import frameAndSave
#import swhlab.common as cm

SQUARESIZE=8

def proto_unknown(theABF):
    """protocol: unknown."""
    abf=ABF(theABF)
    abf.log.info("analyzing as an unknown protocol")
    plot=ABFplot(abf)
    plot.rainbow=False
    plot.title=None
    plot.figure_height,plot.figure_width=SQUARESIZE,SQUARESIZE
    plot.kwargs["lw"]=.5
    plot.figure_chronological()
    plt.gca().set_axis_bgcolor('#AAAAAA') # different background if unknown protocol
    frameAndSave(abf,"UNKNOWN")

def proto_0101(theABF):
    abf=ABF(theABF)
    abf.log.info("analyzing as an IC tau")
    #plot=ABFplot(abf)

    plt.figure(figsize=(SQUARESIZE/2,SQUARESIZE/2))
    plt.grid()
    plt.ylabel("relative potential (mV)")
    plt.xlabel("time (sec)")
    m1,m2=[.05,.1]
    for sweep in range(abf.sweeps):
        abf.setsweep(sweep)
        plt.plot(abf.sweepX2,abf.sweepY-abf.average(m1,m2),alpha=.2,color='#AAAAFF')
    average=abf.averageSweep()
    average-=np.average(average[int(m1**abf.pointsPerSec):int(m2*abf.pointsPerSec)])
    plt.plot(abf.sweepX2,average,color='b',lw=2,alpha=.5)
    plt.axvspan(m1,m2,color='r',ec=None,alpha=.1)
    plt.axhline(0,color='r',ls="--",alpha=.5,lw=2)
    plt.margins(0,.1)

    # save it
    plt.tight_layout()
    frameAndSave(abf,"IC tau")
    plt.close('all')


def proto_0111(theABF):
    """protocol: IC ramp for AP shape analysis."""
    abf=ABF(theABF)
    abf.log.info("analyzing as an IC ramp")

    # AP detection
    ap=AP(abf)
    ap.detect()
    if not len(ap.APs):
        print("NO APS DETECTED")
        return
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
    frameAndSave(abf,"AP shape")
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
    frameAndSave(abf,"AP Gain %d_%d"%(startAt,stepSize))
    plt.close('all')

def proto_0112(theABF):
    proto_gain(theABF,10,-50)

def proto_0113(theABF):
    proto_gain(theABF,25)

def proto_0114(theABF):
    proto_gain(theABF,100)

def proto_0201(theABF):
    """protocol: membrane test."""
    abf=ABF(theABF)
    abf.log.info("analyzing as a membrane test")
    plot=ABFplot(abf)
    plot.figure_height,plot.figure_width=SQUARESIZE/2,SQUARESIZE/2
    plot.figure_sweeps()

    # save it
    plt.tight_layout()
    frameAndSave(abf,"membrane test")
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
    frameAndSave(abf,"MTIV")
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
    frameAndSave(abf,"fast IV")
    plt.close('all')

def proto_0401(theABF):
    proto_avgRange(theABF,.5,2.0)

def proto_0402(theABF):
    proto_avgRange(theABF,.5,2.0)

def proto_0404(theABF):
    proto_avgRange(theABF,1.0,1.1)

def proto_0405(theABF):
    proto_avgRange(theABF,1.0,None)

def proto_0501(theABF):
    BLS_average_stack(theABF)
def proto_0502(theABF):
    BLS_average_stack(theABF)

def BLS_average_stack(theABF):
    abf=ABF(theABF)
    T1,T2=abf.epochTimes(2)
    padding=.1
    if abf.units=="mV":
        padding=.25
    Tdiff=max([T2-T1,padding])
    Tdiff=min([T1,padding])
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
        if abf.units=='pA':
            plt.plot(Xs,chunks[sweep]+100*(abf.sweeps-sweep),alpha=.5,color='b',lw=2) # if VC, focus on BLS
        else:
            plt.plot(abf.sweepX2,abf.sweepY+100*(abf.sweeps-sweep),alpha=.5,color='b',lw=2) # if IC, show full sweep

    plt.subplot(211)
    plt.plot(Xs,np.average(chunks,axis=0),alpha=.5,lw=2)
    plt.title("%s.abf - BLS - average of %d sweeps"%(abf.ID,abf.sweeps))
    plt.ylabel(abf.units2)
    plt.axvspan(T1,T2,alpha=.2,color='y',lw=0)
    plt.margins(0,.1)

    plt.subplot(212)
    plt.xlabel("time (sec)")
    plt.ylabel("stacked sweeps")
    plt.axvspan(T1,T2,alpha=.2,color='y',lw=0)
    if abf.units=='mV':
        plt.axvline(T1,color='r',alpha=.2,lw=3)
#        plt.axvline(T2,color='r',alpha=.2,lw=3)
    plt.margins(0,.1)

    plt.tight_layout()
    frameAndSave(abf,"BLS","experiment")
    plt.close('all')


def proto_avgRange(theABF,m1=None,m2=None):
    """experiment: generic VC time course experiment."""

    abf=ABF(theABF)
    abf.log.info("analyzing as a fast IV")
    if m1 is None:
        m1=abf.sweepLength
    if m2 is None:
        m2=abf.sweepLength

    I1=int(abf.pointsPerSec*m1)
    I2=int(abf.pointsPerSec*m2)

    Ts=np.arange(abf.sweeps)*abf.sweepInterval
    Yav=np.empty(abf.sweeps)*np.nan # average
    Ysd=np.empty(abf.sweeps)*np.nan # standard deviation
    #Yar=np.empty(abf.sweeps)*np.nan # area

    for sweep in abf.setsweeps():
        Yav[sweep]=np.average(abf.sweepY[I1:I2])
        Ysd[sweep]=np.std(abf.sweepY[I1:I2])
        #Yar[sweep]=np.sum(abf.sweepY[I1:I2])/(I2*I1)-Yav[sweep]

    plot=ABFplot(abf)
    plt.figure(figsize=(SQUARESIZE*2,SQUARESIZE/2))

    plt.subplot(131)
    plot.title="first sweep"
    plot.figure_sweep(0)
    plt.title("First Sweep\n(shaded measurement range)")
    plt.axvspan(m1,m2,color='r',ec=None,alpha=.1)

    plt.subplot(132)
    plt.grid(alpha=.5)
    for i,t in enumerate(abf.comment_times):
        plt.axvline(t/60,color='r',alpha=.5,lw=2,ls='--')
    plt.plot(Ts/60,Yav,'.',alpha=.75)
    plt.title("Range Average\nTAGS: %s"%(", ".join(abf.comment_tags)))
    plt.ylabel(abf.units2)
    plt.xlabel("minutes")
    plt.margins(0,.1)

    plt.subplot(133)
    plt.grid(alpha=.5)
    for i,t in enumerate(abf.comment_times):
        plt.axvline(t/60,color='r',alpha=.5,lw=2,ls='--')
    plt.plot(Ts/60,Ysd,'.',alpha=.5,color='g',ms=15,mew=0)
    #plt.fill_between(Ts/60,Ysd*0,Ysd,lw=0,alpha=.5,color='g')
    plt.title("Range Standard Deviation\nTAGS: %s"%(", ".join(abf.comment_tags)))
    plt.ylabel(abf.units2)
    plt.xlabel("minutes")
    plt.margins(0,.1)
    plt.axis([None,None,0,np.percentile(Ysd,99)*1.25])

    plt.tight_layout()
    frameAndSave(abf,"sweep vs average","experiment")
    plt.close('all')

def analyze(fname=False,save=True,show=None):
    """given a filename or ABF object, try to analyze it."""
    swhlab.plotting.core.IMAGE_SAVE=save
    if show is None:
        if cm.isIpython():
            swhlab.plotting.core.IMAGE_SHOW=True
        else:
            swhlab.plotting.core.IMAGE_SHOW=False
    #swhlab.plotting.core.IMAGE_SHOW=show
    abf=ABF(fname) # ensure it's a class
    print(">>>>> PROTOCOL >>>>>",abf.protocomment)
    runFunction="proto_unknown"
    if "proto_"+abf.protocomment in globals():
        runFunction="proto_"+abf.protocomment
    abf.log.debug("running %s()"%(runFunction))
    plt.close('all') # get ready
    globals()[runFunction](abf) # run that function
    try:
        globals()[runFunction](abf) # run that function
    except:
        abf.log.error("EXCEPTION DURING PROTOCOL FUNCTION")
        abf.log.error(sys.exc_info()[0])
        return "ERROR"
    plt.close('all') # clean up
    return "SUCCESS"

def analyzeFolder(folder, convertTifs=True):
    for fname in sorted(glob.glob(folder+"/*.abf")):
        analyze(fname)
    if convertTifs:
        imaging.TIF_to_jpg_all(folder)
    if not os.path.exists(folder+"/swhlab"):
        os.mkdir(folder+"/swhlab")
    for fname in glob.glob(folder+"/*.tif.jpg"):
        path1=os.path.abspath(fname)
        path2=os.path.abspath(folder+"/swhlab/"+os.path.basename(fname))
        os.rename(path1,path2)



if __name__=="__main__":

    if len(sys.argv)==1:
        analyze(r"\\SPIKE\X_DRIVE\Data\SCOTT\2017-06-21 NAC GLU\17621046.abf")
        #analyzeFolder(r"X:\Data\SCOTT\2017-05-10 GCaMP6f\2017-05-10 GCaMP6f PFC OXTR cre\2017-06-02 cell1\ephys")
        print("DONE")

    if len(sys.argv)==2:
        print("protocols.py is getting a path...")
        abfPath=os.path.abspath(sys.argv[1])
        if not os.path.exists(abfPath):
            print(abfPath,"does not exist")
        elif not abfPath.endswith(".abf"):
            print(abfPath,"needs to be an ABF file")
        else:
            try:
                print(analyze(abfPath))
            except:
                print("something went wrong.")


    #print("DONT RUN THIS DIRECTLY. Call analyze() externally.")
    #fname=r"X:\Data\SCOTT\2017-01-09 AT1 NTS\17503052.abf"
    #analyze(fname)
