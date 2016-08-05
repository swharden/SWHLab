"""
Event detection routines related to whole-cell action potentials.

The sequence is generally:
    1. detect() - analyzeAP is called automatically
    2. check_sweep() - optionally

Assigns the following to the ABF class:
    abf.APs[sweep]=[{},{},{},{}] # each sweep has a list of dicts (1 per AP)
    abf.SAP[sweep]={} # each sweep 1 dict for sweep AP stats

Example usage:
    abf=swhlab.ABF('../abfs/aps.abf') #load the ABF
    swhlab.ap.detect(abf) #this creates abf.APs (list of list of dicts)
    swhlab.ap.check_sweep(abf)
    downslopes=cm.dictVals(cm.dictFlat(abf.APs),"downslope")
    print("Found %d APs."%len(downslopes))
    print("Avg downslope: %.02f V/S"%np.average(downslopes))
    pylab.show()
"""

import os
import sys
import pylab
import time
import numpy as np
import traceback

import swhlab
import swhlab.core.common as cm
exampleABF=swhlab.ABF()


#TODO: this dictionary thing isn't a good idea long term. Can we make it NPY?

def detect(abf,sweep=None,threshold_upslope=50,dT=.1,saveToo=True):
    """
    An AP will be detected by a upslope that exceeds 50V/s. Analyzed too.
        if type(sweep) is int, graph int(sweep)
        if sweep==None, process all sweeps sweep.
    """
    if type(sweep) is int:
        sweeps=[sweep]
    else:
        sweeps=list(range(abf.sweeps))
    timeStart=time.clock()
    abf.APs=[None]*abf.sweeps
    abf.SAP=[None]*abf.sweeps
    for sweep in sweeps:
        abf.setSweep(sweep)
        Y=abf.dataY
        dI = int(dT/1000*abf.rate) #dI is dT/rate
        dY = (Y[dI:]-Y[:-dI])*(abf.rate/1000/dI) #now in V/S
        Is = cm.where_cross(dY,threshold_upslope) #found every putative AP (I units)
        abf.APs[sweep]=[]
        for i in range(len(Is)): #for each putative AP
            try:
                AP=analyzeAP(Y,dY,Is[i],abf.rate) #try to characterize it
                if AP:
                    AP["sweep"]=sweep
                    AP["expI"]=sweep*abf.sweepInterval*abf.rate*+AP["sweepI"]
                    AP["expT"]=sweep*abf.sweepInterval+AP["sweepT"]
                    AP["freq"]=np.nan #default
                    if len(abf.APs[sweep]):
                        AP["freq"]=1/(AP["expT"]-abf.APs[sweep][-1]["expT"])
                    if AP["freq"] is np.nan or AP["freq"]<500: #at 500Hz, assume you have a duplicate AP
                        abf.APs[sweep].append(AP)
            except:
                print(" -- AP %d of %d excluded from analysis..."%(i+1,len(Is)))
                #print("!!! AP CRASH !!!")
                #print(traceback.format_exc())
        analyzeAPgroup(abf) #now that APs are known, get grouping stats
    abf.APs=cm.matrixfromDicts(abf.APs)
    abf.SAP=cm.matrixfromDicts(abf.SAP)
    print(" -- analyzed %d APs in %.02f ms"%(len(cm.dictFlat(abf.APs)),(time.clock()-timeStart)*1000))
    if saveToo:
        abf.saveThing(abf.APs,"APs")
        abf.saveThing(abf.SAP,"SAP")

def analyzeAPgroup(abf=exampleABF,T1=None,T2=None,plotToo=False):
    """
    On the current (setSweep()) sweep, calculate things like accomodation.
    Only call directly just for demonstrating how it works by making a graph.
    Or call this if you want really custom T1 and T2 (multiple per sweep)
      This is called by default with default T1 and T2.
      Manually call it again for custom.
    """
    if T1 is None or T2 is None:
        if len(abf.protoSeqX)>2:
            T1=abf.protoSeqX[1]/abf.rate
            T2=abf.protoSeqX[2]/abf.rate
        else:
            T1=0
            T2=abf.sweepLength
    s={} #sweep dictionary to contain our stas
    s["sweep"]=abf.currentSweep
    s["commandI"]=abf.protoSeqY[1]

    APs=[]

    for key in ['freqAvg','freqBin']:
        s[key]=0

    for AP in abf.APs[abf.currentSweep]:
        if T1<AP["sweepT"]<T2:
            APs.append(AP)
    s["nAPs"]=len(APs) #number of APs in the bin period (T1-T2)
    apTimes=cm.dictVals(APs,'sweepT')
    if len(APs)>1: #some measurements require multiple APs, like accomodation
        s["centerBinTime"]=np.average(apTimes)-T1 #average time of APs in the bin
        s["centerBinFrac"]=s["centerBinTime"]/(T2-T1)*100 #fractional average of APs in bin (steady = .5)
        s["centerTime"]=np.average(apTimes)-APs[0]["sweepT"] #time of average AP WRT first AP (not bin)
        s["centerFrac"]=s["centerTime"]/(APs[-1]["sweepT"]-APs[0]["sweepT"])*100 #WRT first/last AP
        s["msToFirst"]=(APs[0]["sweepT"]-T1)*1000 #ms to first AP (from T1)
        s["freqFirst1"]=APs[1]['freq'] #inst frequency of first AP
        s["freqFirst5"]=cm.dictAvg(APs[1:6],'freq')[0] #inst frequency of first AP
        s["freqLast"]=APs[-1]['freq'] #inst frequency of last AP
        s["freqAvg"]=cm.dictAvg(APs,'freq')[0] #average inst frequency of all aps
        s["freqBin"]=len(APs)/(T2-T1) #frequency of APs in the bin (T1-T2)
        s["freqSteady25"]=cm.dictAvg(APs[-int(len(APs)*.25):],'freq')[0] # average freq of the last 25% of APs
        s["accom1Avg"]=s["freqFirst1"]/s["freqAvg"] #accomodation (first II / average)
        s["accom1Steady25"]=s["freqFirst1"]/s["freqSteady25"] #accomodation (first II / steady state)
        s["accom5Avg"]=s["freqFirst5"]/s["freqAvg"] #accomodation from average 5 first
        s["accom5Steady25"]=s["freqFirst5"]/s["freqSteady25"] #accomodation from average 5 first
        s["freqCV"]=cm.dictAvg(APs,'freq')[1]/cm.dictAvg(APs,'freq')[0] #coefficient of variation (Hz)
        s["T1"]=T1
        s["T2"]=T2
    abf.SAP[abf.currentSweep]=s

def check_AP_group(abf=exampleABF,sweep=0):
    """
    after running detect() and abf.SAP is populated, this checks it.
    """
    abf.setSweep(sweep)
    swhlab.plot.new(abf,title="sweep %d (%d pA)"%(abf.currentSweep,abf.protoSeqY[1]))
    swhlab.plot.sweep(abf)
    SAP=cm.matrixToDicts(abf.SAP[sweep])
    if "T1" in SAP.keys():
        T1=SAP["T1"]
        T2=SAP["T2"]
        pylab.axvspan(T1/abf.rate,T2/abf.rate,color='r',alpha=.1)
    else:
        T1=0
        T2=abf.sweepLength
    swhlab.plot.annotate(abf)
    pylab.tight_layout()
    pylab.subplots_adjust(right=0.6)
    pylab.annotate(cm.msgDict(SAP),(.71,.95),ha='left',va='top',
                   weight='bold',family='monospace',
                   xycoords='figure fraction',size=12,color='g')
    pylab.axis([T1-.05,T2+.05,None,None])

def analyzeAP(Y,dY,I,rate,verbose=False):
    """
    given a sweep and a time point, return the AP array for that AP.
    APs will be centered in time by their maximum upslope.
    """
    Ims = int(rate/1000) #Is per MS
    IsToLook=5*Ims #TODO: clarify this, ms until downslope is over
    upslope=np.max(dY[I:I+IsToLook]) #maximum rise velocity
    upslopeI=np.where(dY[I:I+IsToLook]==upslope)[0][0]+I
    I=upslopeI #center sweep at the upslope
    downslope=np.min(dY[I:I+IsToLook]) #maximum fall velocity
    downslopeI=np.where(dY[I:I+IsToLook]==downslope)[0][0]+I
    peak=np.max(Y[I:I+IsToLook]) #find peak value (mV)
    peakI=np.where(Y[I:I+IsToLook]==peak)[0][0]+I #find peak I
    thresholdI=I-np.where(dY[I:I+IsToLook:--1]<10)[0] #detect <10V/S
    if not len(thresholdI):
        return False
    thresholdI=thresholdI[0]
    threshold=Y[thresholdI] # mV where >10mV/S
    height=peak-threshold # height (mV) from threshold to peak
    halfwidthPoint=np.average((threshold,peak))
    halfwidth=np.where(Y[I-IsToLook:I+IsToLook]>halfwidthPoint)[0]
    if not len(halfwidth):
        return False #doesn't look like a real AP
    halfwidthI1=halfwidth[0]+I-IsToLook
    halfwidthI2=halfwidth[-1]+I-IsToLook
    if Y[halfwidthI1-1]>halfwidthPoint or Y[halfwidthI2+1]>halfwidthPoint:
        return False #doesn't look like a real AP
    halfwidth=len(halfwidth)/rate*1000 #now in MS
    riseTime=(peakI-thresholdI)*1000/rate # time (ms) from threshold to peak

    IsToLook=100*Ims #TODO: max prediction until AHP reaches nadir
    AHPchunk=np.diff(Y[downslopeI:downslopeI+IsToLook]) #first inflection
    AHPI=np.where(AHPchunk>0)[0]
    if len(AHPI)==0:
        AHPI=np.nan
    else:
        AHPI=AHPI[0]+downslopeI
        AHPchunk=Y[AHPI:AHPI+IsToLook]
        if max(AHPchunk)>threshold: #if another AP is coming, cut it out
            AHPchunk=AHPchunk[:np.where(AHPchunk>threshold)[0][0]]
        if len(AHPchunk):
            AHP=np.nanmin(AHPchunk)
            AHPI=np.where(AHPchunk==AHP)[0][0]+AHPI
            AHPheight=threshold-AHP # AHP magnitude from threshold (mV)
            IsToLook=500*Ims #TODO: max prediction until AHP reaches threshold
            AHPreturn=np.average((AHP,threshold)) #half of threshold
            AHPreturnI=np.where(Y[AHPI:AHPI+IsToLook]>AHPreturn)[0]
            if len(AHPreturnI): #not having a clean decay won't cause AP to crash
                AHPreturnI=AHPreturnI[0]+AHPI
                AHPrisetime=(AHPreturnI-AHPI)*2/rate*1000 #predicted return time (ms)
                AHPupslope=AHPheight/AHPrisetime #mV/ms = V/S
                AHPreturnFullI=(AHPreturnI-AHPI)*2+AHPI
            else: #make them nan so you can do averages later
                AHPreturnI,AHPrisetime,AHPupslope=np.nan,np.nan,np.nan
                downslope=np.nan

    #fasttime (10V/S to 10V/S) #TODO:
    #dpp (deriv peak to peak) #TODO:

    sweepI,sweepT=I,I/rate # clean up variable names
    del IsToLook,I, Y, dY, Ims, AHPchunk, verbose #delete what we don't need
    return locals() #this is a beautiful dictionary of our AP stats

def check_sweep(abf,sweep=None,dT=.1):
    """Plotting for an eyeball check of AP detection in the given sweep."""
    if abf.APs is None:
        APs=[]
    else:
        APs=cm.matrixToDicts(abf.APs)

    if sweep is None or len(sweep)==0: #find the first sweep with >5APs in it
        for sweepNum in range(abf.sweeps):
            foundInThisSweep=0
            for AP in APs:
                if AP["sweep"]==sweepNum:
                    foundInThisSweep+=1
                if foundInThisSweep>=5:
                    break
        sweep=sweepNum
    abf.setSweep(sweep)
    Y=abf.dataY

    dI = int(dT/1000*abf.rate) #dI is dT/rate
    dY = (Y[dI:]-Y[:-dI])*(abf.rate/1000/dI) #now in V/S

    pylab.figure(figsize=(12,6))
    ax=pylab.subplot(211)
    pylab.title("sweep %d"%abf.currentSweep)
    pylab.ylabel("membrane potential (mV)")
    pylab.plot(Y,'-',alpha=.8)
    for AP in APs:
        if not AP["sweep"]==sweep:
            continue
        pylab.axvline(AP["sweepI"],alpha=.2,color='r')
        pylab.plot(AP["peakI"],AP["peak"],'.',alpha=.5,ms=20,color='r')
        pylab.plot(AP["thresholdI"],AP["threshold"],'.',alpha=.5,ms=20,color='c')
        pylab.plot([AP["AHPI"],AP["AHPreturnI"]],
                    [AP["AHP"],AP["AHPreturn"]],
                    '-',alpha=.2,ms=20,color='b',lw=7)
        pylab.plot([AP["halfwidthI1"],AP["halfwidthI2"]],
                   [AP["halfwidthPoint"],AP["halfwidthPoint"]],
                   '-',lw=5,alpha=.5,color='g')

    pylab.subplot(212,sharex=ax)
    pylab.ylabel("velocity (V/S)")
    pylab.xlabel("data points (%.02f kHz)"%(abf.rate/1000))
    pylab.plot(dY,'-',alpha=.8)
    pylab.margins(0,.1)
    for AP in APs:
        if not AP["sweep"]==sweep:
            continue
        pylab.axvline(AP["sweepI"],alpha=.2,color='r')
        pylab.plot(AP["upslopeI"],AP["upslope"],'.',alpha=.5,ms=20,color='g')
        pylab.plot(AP["downslopeI"],AP["downslope"],'.',alpha=.5,ms=20,color='g')
        pylab.axis([APs[0]["sweepI"]-1000,APs[-1]["sweepI"]+1000,None,None])

def get_AP_timepoints(abf):
    """return list of time points (sec) of all AP events in experiment."""
    col=abf.APs.dtype.names.index("expT")
    timePoints=[]
    for i in range(len(abf.APs)):
        timePoints.append(abf.APs[i][col])
    return timePoints

def check_AP_raw(abf,n=10):
    """X"""
    timePoints=get_AP_timepoints(abf)[:n] #first 10
    if len(timePoints)==0:
        return
    swhlab.plot.new(abf,True,title="AP shape (n=%d)"%n,xlabel="ms")
    Ys=abf.get_data_around(timePoints,padding=.2)
    Xs=(np.arange(len(Ys[0]))-len(Ys[0])/2)*1000/abf.rate
    for i in range(1,len(Ys)):
        pylab.plot(Xs,Ys[i],alpha=.2,color='b')
    pylab.plot(Xs,Ys[0],alpha=.4,color='r',lw=2)
    pylab.margins(0,.1)
    msg=cm.msgDict(cm.dictFlat(abf.APs)[0],cantEndWith="I")
    pylab.subplots_adjust(right=0.7)
    pylab.annotate(msg,(.71,.95),ha='left',va='top',
                   xycoords='figure fraction',family='monospace',size=10)

def check_AP_deriv(abf,n=10):
    """X"""
    timePoints=get_AP_timepoints(abf)[:10] #first 10
    if len(timePoints)==0:
        return
    swhlab.plot.new(abf,True,title="AP velocity (n=%d)"%n,xlabel="ms",ylabel="V/S")
    pylab.axhline(-50,color='r',lw=2,ls="--",alpha=.2)
    pylab.axhline(-100,color='r',lw=2,ls="--",alpha=.2)
    Ys=abf.get_data_around(timePoints,msDeriv=.1,padding=.005)
    Xs=(np.arange(len(Ys[0]))-len(Ys[0])/2)*1000/abf.rate
    for i in range(1,len(Ys)):
        pylab.plot(Xs,Ys[i],alpha=.2,color='b')
    pylab.plot(Xs,Ys[0],alpha=.4,color='r',lw=2)
    pylab.margins(0,.1)

def check_AP_phase(abf,n=10):
    """X"""
    timePoints=get_AP_timepoints(abf)[:10] #first 10
    if len(timePoints)==0:
        return
    swhlab.plot.new(abf,True,title="AP phase (n=%d)"%n,xlabel="mV",ylabel="V/S")
    Ys=abf.get_data_around(timePoints,msDeriv=.1,padding=.005)
    Xs=abf.get_data_around(timePoints,padding=.005)
    for i in range(1,len(Ys)):
        pylab.plot(Xs[i],Ys[i],alpha=.2,color='b')
    pylab.plot(Xs[0],Ys[0],alpha=.4,color='r',lw=1)
    pylab.margins(.1,.1)

def stats_first(abf):
    """provide all stats on the first AP."""
    msg=""
    for sweep in range(abf.sweeps):
        for AP in abf.APs[sweep]:
            for key in sorted(AP.keys()):
                if key[-1] is "I" or key[-2:] in ["I1","I2"]:
                    continue
                msg+="%s = %s\n"%(key,AP[key])
            return msg

def get_values(abf,key="freq",continuous=False):
    """returns Xs, Ys (the key), and sweep #s for every AP found."""
    Xs,Ys,Ss=[],[],[]
    for sweep in range(abf.sweeps):
        for AP in cm.matrixToDicts(abf.APs):
            if not AP["sweep"]==sweep:
                continue
            Ys.append(AP[key])
            Ss.append(AP["sweep"])
            if continuous:
                Xs.append(AP["expT"])
            else:
                Xs.append(AP["sweepT"])

    return np.array(Xs),np.array(Ys),np.array(Ss) #None->nan

def plot_values(abf,key="freq",continuous=False):
    Xs,Ys,Ss=get_values(abf,key=key,continuous=continuous)
    swhlab.plot.new(abf,True)
    ax=pylab.subplot(211)
    pylab.ylabel(key)
    for i in range(len(Xs)):
        pylab.plot(Xs[i],Ys[i],'.',alpha=.5,ms=10,color=abf.cm(Ss[i]/abf.sweeps))
    pylab.subplot(212,sharex=ax)
    pylab.ylabel("membrane potential")
    swhlab.plot.sweep(abf,'all',continuous=continuous)
    swhlab.plot.comments(abf)
    swhlab.plot.annotate(abf)

def getAvgBySweep(abf,feature,T0=None,T1=None):
    """return average of a feature divided by sweep."""
    if T1 is None:
        T1=abf.sweepLength
    if T0 is None:
        T0=0
    data = [np.empty((0))]*abf.sweeps
    for AP in cm.dictFlat(cm.matrixToDicts(abf.APs)):
        if T0<AP['sweepT']<T1:
            val=AP[feature]
            data[int(AP['sweep'])]=np.concatenate((data[int(AP['sweep'])],[val]))
    for sweep in range(abf.sweeps):
        if len(data[sweep])>1 and np.any(data[sweep]):
            data[sweep]=np.nanmean(data[sweep])
        elif len(data[sweep])==1:
            data[sweep]=data[sweep][0]
        else:
            data[sweep]=np.nan
    return data

def test():
    abf=swhlab.ABF(r'C:\Apps\pythonModules\abfs\16711016.abf')
    swhlab.ap.detect(abf)
    swhlab.ap.check_AP_phase(abf)
    Xs=swhlab.common.matrixValues(abf.APs,"expT")
    Ys=swhlab.common.matrixValues(abf.APs,"downslope")
    cm.show(True)
    pylab.plot(Xs,Ys,'.')
    cm.show(True)

if __name__=="__main__":
    test()
    print("DONT RUN ME DIRECTLY")