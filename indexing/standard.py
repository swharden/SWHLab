"""
This module is somewhat experiment specific.
The idea is to match protocols (defined by comments) to analysis routines.
This is specific to Scott's current set of experiments.
Probably this doesn't belong in the module at all...
"""
import os
import sys
import glob
import pylab
import numpy as np
import traceback

import swhlab
from swhlab.core import common as cm #shorthand
from swhlab.indexing.indexing import genIndex
exampleABF=swhlab.ABF(None) #this helps for IDE recommendations

def standard_inspect(abf=exampleABF):
    cm.inspectABF(abf,justPlot=True)
    swhlab.plot.save(abf,tag="00-inspect")

def standard_overlayWithAverage(abf=exampleABF):
    swhlab.plot.sweep(abf,'all',alpha=.1)
    Xs,Av,Es=abf.average_sweep()
    pylab.plot(Xs,Av,'k')
    pylab.title("average (n=%d)"%abf.sweeps)
    swhlab.plot.save(abf,tag='overlay')

def standard_groupingForInj(abf,target=200):
    for i in range(abf.sweeps):
        abf.setSweep(i)
        if abf.protoSeqY[1]==target: #first step is target pA injection
            swhlab.ap.check_AP_group(abf,i)
            swhlab.plot.save(abf,tag='05-grouping',resize=False)

### --- SWHLab4 protocols ---

def proto_00_01_gf(abf=exampleABF):
    """gap free recording"""
    standard_inspect(abf)

def proto_00_02_egf(abf=exampleABF):
    """episodic with no epochs (virtually gap free)"""
    standard_inspect(abf)

def proto_01_01_HP010(abf=exampleABF):
    """hyperpolarization step. Use to calculate tau and stuff."""
    swhlab.memtest.memtest(abf) #knows how to do IC memtest
    swhlab.memtest.checkSweep(abf) #lets you eyeball check how it did
    swhlab.plot.save(abf,tag="tau")

def proto_01_11_rampStep(abf=exampleABF):
    """each sweep is a ramp (of set size) which builds on the last sweep.
    Used for detection of AP properties from first few APs."""
    standard_inspect(abf)
    swhlab.ap.detect(abf)
    swhlab.ap.check_sweep(abf) #eyeball how well event detection worked
    swhlab.plot.save(abf,tag="check")
    swhlab.ap.check_AP_raw(abf) #show overlayed first few APs
    swhlab.plot.save(abf,tag="raw",resize=False)
    swhlab.ap.check_AP_deriv(abf) #show overlayed first few APs
    swhlab.plot.save(abf,tag="deriv")
    swhlab.ap.check_AP_phase(abf) #show overlayed first few APs
    swhlab.plot.save(abf,tag="phase")
    for feature in ['downslope','freq']:
        swhlab.ap.plot_values(abf,feature,continuous=True) #plot AP info
        swhlab.plot.save(abf,tag=feature)

def proto_01_12_steps025(abf=exampleABF):
    """IC steps. Use to determine gain function."""
    swhlab.ap.detect(abf)
    standard_groupingForInj(abf,200)

    for feature in ['freq','downslope']:
        swhlab.ap.plot_values(abf,feature,continuous=False) #plot AP info
        swhlab.plot.save(abf,tag='A_'+feature)

    swhlab.plot.gain(abf) #easy way to do a gain function!
    swhlab.plot.save(abf,tag='05-gain')


def proto_01_13_steps100dual(abf=exampleABF):
    proto_01_13_steps025dual(abf)

def proto_01_13_steps025dual(abf=exampleABF):
    """IC steps. See how hyperpol. step affects things."""
    swhlab.ap.detect(abf)
    standard_groupingForInj(abf,200)

    for feature in ['freq','downslope']:
        swhlab.ap.plot_values(abf,feature,continuous=False) #plot AP info
        swhlab.plot.save(abf,tag='A_'+feature)

    f1=swhlab.ap.getAvgBySweep(abf,'freq',None,1)
    f2=swhlab.ap.getAvgBySweep(abf,'freq',1,None)
    f1=np.nan_to_num(f1)
    f2=np.nan_to_num(f2)
    Xs=abf.clampValues(abf.dataX[int(abf.protoSeqX[1]+.01)])
    swhlab.plot.new(abf,title="gain function",xlabel="command current (pA)",
                    ylabel="average inst. freq. (Hz)")
    pylab.plot(Xs,f1,'.-',ms=20,alpha=.5,label="step 1",color='b')
    pylab.plot(Xs,f2,'.-',ms=20,alpha=.5,label="step 2",color='r')
    pylab.legend(loc='upper left')
    pylab.axis([Xs[0],Xs[-1],None,None])
    swhlab.plot.save(abf,tag='gain')


def proto_02_01_MT70(abf=exampleABF):
    """repeated membrane tests."""
    standard_overlayWithAverage(abf)
    swhlab.memtest.memtest(abf)
    swhlab.memtest.checkSweep(abf)
    swhlab.plot.save(abf,tag='check',resize=False)

def proto_02_02_IVdual(abf=exampleABF):
    """dual I/V steps in VC mode, one from -70 and one -50."""

    av1,sd1=swhlab.plot.IV(abf,.7,1,True,'b')
    swhlab.plot.save(abf,tag='iv1')
    a2v,sd2=swhlab.plot.IV(abf,2.2,2.5,True,'r')
    swhlab.plot.save(abf,tag='iv2')

    swhlab.plot.sweep(abf,'all')
    pylab.axis([None,None,min(av1)-50,max(av1)+50])
    swhlab.plot.save(abf,tag='overlay')

def proto_02_03_IVfast(abf=exampleABF):
    """fast sweeps, 1 step per sweep, for clean IV without fast currents."""
    av1,sd1=swhlab.plot.IV(abf,.6,.9,True)
    swhlab.plot.save(abf,tag='iv1')
    Xs=abf.clampValues(.6) #generate IV clamp values
    abf.saveThing([Xs,av1],'iv') #save the IV values

def proto_03_01_0s2(abf=exampleABF):
    """repeated membrane tests, likely with drug added. Maybe IPSCs."""
    standard_inspect(abf) #saves too

def proto_04_01_MTmon70s2(abf=exampleABF):
    """repeated membrane tests, likely with drug added. Maybe IPSCs."""
    standard_inspect(abf)
    swhlab.memtest.memtest(abf)
    swhlab.memtest.checkSweep(abf)
    swhlab.plot.save(abf,tag='check',resize=False)
    swhlab.memtest.plot_standard4(abf)
    swhlab.plot.save(abf,tag='memtests')

### --- SWHLab3 protocols ---

#def proto_SHIV4(abf=exampleABF):
#    return

def proto_VC_50_MT_IV(abf=exampleABF):
    """combination of membrane test and IV steps."""
    swhlab.memtest.memtest(abf) #do membrane test on every sweep
    swhlab.memtest.checkSweep(abf) #see all MT values
    swhlab.plot.save(abf,tag='02-check',resize=False)

    av1,sd1=swhlab.plot.IV(abf,1.2,1.4,True,'b')
    swhlab.plot.save(abf,tag='iv')
    Xs=abf.clampValues(1.2) #generate IV clamp values
    abf.saveThing([Xs,av1],'01_iv') #save the IV values

def proto_IC_ramp_gain(abf=exampleABF):
    """increasing ramps in (?) pA steps."""
    standard_inspect(abf)
    swhlab.ap.detect(abf)

    swhlab.ap.check_AP_raw(abf) #show overlayed first few APs
    swhlab.plot.save(abf,tag="01-raw",resize=False)
    swhlab.ap.check_AP_deriv(abf) #show overlayed first few APs
    swhlab.plot.save(abf,tag="02-deriv")
    swhlab.ap.check_AP_phase(abf) #show overlayed first few APs
    swhlab.plot.save(abf,tag="03-phase")

    swhlab.ap.plot_values(abf,'freq',continuous=True) #plot AP info
    pylab.subplot(211)
    pylab.axhline(40,color='r',lw=2,ls="--",alpha=.2)
    swhlab.plot.save(abf,tag='04-freq')

    swhlab.ap.plot_values(abf,'downslope',continuous=True) #plot AP info
    pylab.subplot(211)
    pylab.axhline(-100,color='r',lw=2,ls="--",alpha=.2)
    swhlab.plot.save(abf,tag='04-downslope')

def proto_SHIV4(abf=exampleABF):
    """increasing ramps in (?) pA steps."""
    standard_inspect(abf)
    swhlab.ap.detect(abf)
    standard_groupingForInj(abf,200)

    swhlab.ap.check_AP_raw(abf) #show overlayed first few APs
    swhlab.plot.save(abf,tag="01-raw",resize=False)
    swhlab.ap.check_AP_deriv(abf) #show overlayed first few APs
    swhlab.plot.save(abf,tag="02-deriv")
    swhlab.ap.check_AP_phase(abf) #show overlayed first few APs
    swhlab.plot.save(abf,tag="03-phase")

    swhlab.ap.plot_values(abf,'freq',continuous=True) #plot AP info
    pylab.subplot(211)
    pylab.axhline(40,color='r',lw=2,ls="--",alpha=.2)
    swhlab.plot.save(abf,tag='04-freq')

    swhlab.ap.plot_values(abf,'freq',continuous=False) #plot AP info
    pylab.subplot(211)
    pylab.axhline(40,color='r',lw=2,ls="--",alpha=.2)
    swhlab.plot.save(abf,tag='04-freq2')

    swhlab.plot.gain(abf) #easy way to do a gain function!
    swhlab.plot.save(abf,tag='05-gain')

def proto_sputter(abf=exampleABF):
    """increasing ramps in (?) pA steps."""
    standard_inspect(abf)
    swhlab.ap.detect(abf)

    swhlab.ap.check_AP_raw(abf) #show overlayed first few APs
    swhlab.plot.save(abf,tag="01-raw",resize=False)
    swhlab.ap.check_AP_deriv(abf) #show overlayed first few APs
    swhlab.plot.save(abf,tag="02-deriv")
    swhlab.ap.check_AP_phase(abf) #show overlayed first few APs
    swhlab.plot.save(abf,tag="03-phase")

    swhlab.ap.plot_values(abf,'downslope',continuous=True) #plot AP info
    pylab.subplot(211)
    pylab.axhline(-50,color='r',lw=2,ls="--",alpha=.2)
    pylab.axhline(-100,color='r',lw=2,ls="--",alpha=.2)
    swhlab.plot.save(abf,tag='04-downslope')

def proto_MTmon3(abf=exampleABF):
    swhlab.memtest.memtest(abf) #do membrane test on every sweep
    swhlab.memtest.checkSweep(abf) #see all MT values
    swhlab.plot.save(abf,tag='02-check',resize=False)
    swhlab.memtest.plot_standard4(abf)
    swhlab.plot.save(abf,tag='03-memtest',resize=False)


def proto_loose(abf=exampleABF):
    standard_inspect(abf)
    swhlab.ap.detect(abf)

    swhlab.ap.plot_values(abf,'freq',continuous=True) #plot AP info
    swhlab.plot.save(abf,tag='04-freq')

### --- generic protocols ---#

def proto_unknown(abf=exampleABF):
    cm.inspectABF(abf,justPlot=True)
    swhlab.plot.save(abf,tag="simple",facecolor='#FFDDDD')
    if abf.units=="pA":
        #TRY MEMTEST STUFF
        swhlab.memtest.memtest(abf)
        swhlab.memtest.checkSweep(abf)
        swhlab.plot.save(abf,tag='check',resize=False)
        swhlab.memtest.plot_standard4(abf)
        swhlab.plot.save(abf,tag='memtests')
    else:
        #TRY AP STUFF
        standard_inspect(abf)
        swhlab.ap.detect(abf)
        swhlab.ap.plot_values(abf,'freq') #plot AP info
        pylab.subplot(211)
        pylab.axhline(40,color='r',lw=2,ls="--",alpha=.2)
        swhlab.plot.save(abf,tag='04-freq')

        swhlab.ap.plot_values(abf,'halfwidth') #plot AP info
        pylab.subplot(211)
        pylab.axhline(40,color='r',lw=2,ls="--",alpha=.2)
        pylab.axis([None,None,0,6])
        swhlab.plot.save(abf,tag='04-halfwidth')


        swhlab.ap.check_AP_deriv(abf)
        swhlab.plot.save(abf,tag='05')
        swhlab.ap.check_AP_raw(abf)
        swhlab.plot.save(abf,tag='06')
        swhlab.ap.check_AP_phase(abf)
        swhlab.plot.save(abf,tag='07')
        swhlab.ap.check_sweep(abf)
        swhlab.plot.save(abf,tag='08')


def indexImages(folder,fname="index.html"):
    """OBSOLETE WAY TO INDEX A FOLDER.""" #TODO: REMOVE
    html="<html><body>"
    for item in glob.glob(folder+"/*.*"):
        if item.split(".")[-1] in ['jpg','png']:
            html+="<h3>%s</h3>"%os.path.basename(item)
            html+='<img src="%s">'%os.path.basename(item)
            html+='<br>'*10
    html+="</html></body>"
    f=open(folder+"/"+fname,'w')
    f.write(html)
    f.close
    print("indexed:")
    print("  ",os.path.abspath(folder+"/"+fname))
    return

def autoABF(fname):
    pylab.close('all') #clean slate for good measure
    abf=swhlab.ABF(fname) #load the ABF
    abf.deleteStuff()
    method=abf.protoComment.replace("-","_")
    method="proto_"+method
    print(" ~~",method+"()")
    try:
        if method in globals():
            globals()[method](abf)
        else:
            print(" ~~","proto_unknown()")
            proto_unknown(abf)
    except:
        print(traceback.format_exc())
        print("~"*50,"CRASHED","~"*50)
    return abf.ID

def autoFolder(folder,startAt=None,limit=None,matching=None):
    fnames=glob.glob(folder+"/*.abf")
    analyzed=[]
    if startAt:
        if type(startAt) == str:
            for i in range(len(fnames)):
                if startAt in fnames[i]:
                    startAt=i
                    break
        fnames=fnames[int(startAt):]
    if limit:
        fnames=fnames[:int(limit)]
    if matching:
        fnames2=[]
        for fname in fnames:
            if matching in fname:
                fnames2.append(fname)
        fnames=fnames2
    for i in range(len(fnames)):
        print("\n### analyzing %d of %d ###"%(i+1,len(fnames)))
        analyzed.append(autoABF(fnames[i]))
    return analyzed

if __name__=="__main__":
    folder=r'C:\Users\swharden\Desktop\2016-07-11 PIR TR IHC'
    analyzed=autoFolder(folder,matching="16711054")
    genIndex(folder)
    print("DONE")