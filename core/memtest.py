"""
Membrane test routines for voltage clamp experiments.
creates abf.MTs[sweep]={} #with keys like Ih, Ra, Rm, etc

Example usage:
    abf=swhlab.ABF('../abfs/group/16701010.abf')
    swhlab.memtest.memtest(abf) #performs memtest on all sweeps
    swhlab.memtest.checkSweep(abf) #lets you eyeball check how it did
    pylab.show()
"""

import os
import sys
import pylab
import numpy as np
import time

import swhlab
import swhlab.core.common as cm
exampleABF=swhlab.ABF()

def memtestSweepVC(abf=exampleABF):
    """
    perform memtest on current sweep in VC mode. Return Ih, Ra, Rm, etc.
    All variable names are explained in /swhlab/docs/memtest.ppt
    """
    if abf.protoSeqY[1]>abf.protoSeqY[0] or len(abf.protoSeqY)<3:
        return "protocol doesn't step down and back up"
    TA,TB=int(abf.protoSeqX[1]),int(abf.protoSeqX[2])
    dT=int(TB-TA)
    T1A=int(TA+.5*dT)
    T1B=int(TA+.9*dT)
    T2A=T1A+dT
    T2B=T1B+dT
    P1=np.average(abf.dataY[T1A:T1B])
    P2=np.average(abf.dataY[T2A:T2B])
    dI=P2-P1
    dV=abf.protoSeqY[2]-abf.protoSeqY[1]
    PP=np.max(abf.dataY[TB:TB+100])# peak found within first 100 points
    TP=np.where(abf.dataY[TB:TB+150]==PP)[0][0]+TB
    dP=PP-P1
    dTC=PP-P2
    PCA=P2+.9*dTC # upper fraction for Cm detection
    PCB=P2+.1*dTC # upper fraction for Cm detection
    PCtau=P2+.37*dTC # crossing point of theoretical tau
    TCA=np.where(abf.dataY[TP:T2A]<PCA)[0][0]+TP
    TCB=np.where(abf.dataY[TP:T2A]<PCB)[0][0]+TP
    dTCT=TCB-TCA #number of points available for fitting
    Ih=P2
    Ra=(dV*10**3)/(PP-P2) #MOhm=uV/pA
    Rm=(dV*10**3)/(P2-P1) #MOhm=uV/pA
    fitM,fitT,fitB,fitTau=cm.fit_exp(abf.dataY[TCA:TCB]) #same units as given
    fitTau=fitTau*1000/abf.rate #time constant convert to ms units
    Tv=fitTau #time constant of extrinsic voltage clamp
    Cm=Tv/Ra*1000 #us/MOhm is pF
    Tm=Rm*Cm/1000 #time constant of cell membrane (intrinsic voltage clamp)
    del abf
    return locals()

def memtestIC(abf=exampleABF):
    """
    IC memtest is different. Make an average sweep, then curve fit it.
    This only RETURNS the memtest, it does not assign it.
    """
    if abf.protoSeqY[1]>abf.protoSeqY[0] or len(abf.protoSeqY)<3:
        return "protocol doesn't step down and back up"
    abf.baseline=[abf.protoSeqX[1]/abf.rate*.75,abf.protoSeqX[1]/abf.rate]
    T1A,T1B=np.array(abf.baseline)*abf.rate
    Xs,Ys,Er=abf.average_sweep()
    T2A=abf.protoSeqX[2]-abf.protoSeqX[1]
    T2B=abf.protoSeqX[2]
    M2=np.average(Ys[T2A:T2B])
    MCA=.1*M2 # set 90% here
    MCB=.9*M2 # set 10% here
    TCA=np.where(Ys<MCA)[0][0]
    TCB=np.where(Ys<MCB)[0][0]
    m,t,b,tc=cm.fit_exp(Ys[TCA:TCB]) #do the fit!
    dI=abs(abf.protoSeqY[2]-abf.protoSeqY[1]) #pA
    dV=abs(M2) #mV
    Rm=dV/dI*1000 #uV/pA = MOhm
    Cm=tc/Rm #ms/MOhm
    del abf,Ys,Xs,Er
    return locals() #convert to structured array

def memtest(abf=exampleABF,firstSweepOnly=False,plotToo=False,saveToo=True):
    """perform memtest on all sweeps."""
    timeStart=time.clock()
    if abf.units=="mV":
        abf.MTs = memtestIC(abf)
    else:
        abf.MTs=[None]*abf.sweeps
        for sweep in range(abf.sweeps):
            abf.setSweep(sweep)
            result=memtestSweepVC(abf)
            if type(result) is dict:
                abf.MTs[abf.currentSweep]=result
            else:
                print("MEMTEST FAILED - sweep %d -"%sweep,result)
            if firstSweepOnly:
                return
    abf.MTs = cm.matrixfromDicts(abf.MTs) #convert to structured array
    took=time.clock()-timeStart
    print(" -- memtest performed on %d sweeps in %.02f ms"%(abf.sweeps,took*1000))
    if saveToo:
        abf.saveThing(abf.MTs,"MTs")

def plot_standard4(abf=exampleABF):
    """make a standard memtest plot showing Ih, Ra, etc. with time."""
    if abf.sweeps<2:
        return
    swhlab.plot.new(abf)
    Xs=np.arange(abf.sweeps)*abf.sweepInterval/60
    subplots=[221,222,223,224]
    features=['Ih','Ra','Rm','Cm']
    units=['pA','MOhm','MOhm','pF']
    for subplot,feature,unit in zip(subplots,features,units):
        pylab.subplot(subplot)
        pylab.grid(alpha=.5)
        #pylab.title(feature)
        pylab.plot(Xs,cm.dictVals(abf.MTs,feature),'.-',alpha=.5)
        pylab.xlabel(None)
        pylab.ylabel("%s (%s)"%(feature,unit))
        swhlab.plot.comments(abf,True)
        pylab.margins(0,.1)

def checkSweepIC(abf=exampleABF,sweep=0):
    """Produce an eyeball-ready indication how the MT was calculated in IC."""
    _keys = abf.MTs.dtype.names
    for key in _keys:
        globals()[key]=abf.MTs[key] # only global for this module, that's fine
    fitted=cm.algo_exp(np.arange(TCB-TCA),m,t,b)
    swhlab.plot.new(abf,forceNewFigure=True)
    Xs,Ys,Er=abf.average_sweep()
    for subplot in [121,122]:
        pylab.subplot(subplot)
        pylab.axhline(0,color='b',lw=2,alpha=.5,ls="--")
        pylab.axhline(M2,color='b',lw=2,alpha=.5,ls="--")
        swhlab.plot.sweep(abf,'all',rainbow=False,color='#CCCCCC',alpha=.5)
        pylab.plot(Xs,Ys,color='k',alpha=.5)
        pylab.plot(Xs[T1A:T1B],Ys[T1A:T1B],color='b',lw=2)
        pylab.plot(Xs[T2A:T2B],Ys[T2A:T2B],color='b',lw=2)
        pylab.plot(abf.dataX[TCA:TCB],fitted,color='r',lw=2,ls='--')
    pylab.axis([(TCA-100)/abf.rate,(TCB+100)/abf.rate,None,None])
    pylab.tight_layout()
    msg="tau: %.02f ms\n"%(tc/abf.rate*1000)
    msg+="Rm: %.02f MOhm\n"%(Rm)
    msg+="Cm: %.02f pF"%(Cm)
    pylab.annotate(msg,(.75,.95),ha='left',va='top',weight='bold',family='monospace',
                   xycoords='figure fraction',size=12,color='g')
    swhlab.plot.annotate(abf)
    return

def checkSweep(abf=exampleABF,sweep=0):
    """Produce an eyeball-ready indication how the MT was calculated in VC."""
    if abf.units=="mV":
        return checkSweepIC(abf,sweep)
    if abf.MTs[sweep] is None:
        return False #no memtest data even found
    _keys = abf.MTs[sweep].dtype.names
    for key in _keys:
        globals()[key]=abf.MTs[sweep][key] # only global for this module, that's fine.
    _msg2="Average (n=%d)\n"%abf.sweeps
    _msg=""
    for i in range(len(_keys)):
        _msg+="%s=%s\n"%(_keys[i],abf.MTs[sweep][i])
        if _keys[i] in ['Ih','Ra','Rm','Cm','Tv','Tm']:
            _msg2+="%s=%.02f\n"%(_keys[i],abf.MTs[sweep][i])
    fitted=cm.algo_exp(np.arange(TCB-TCA),fitM,fitT,fitB)
    pylab.figure(figsize=(8,8))
    for subplot in [211,212]:
        pylab.subplot(subplot)
        #pylab.plot(abf.dataX,abf.dataY,alpha=.2,color='k',lw=2)
        pylab.plot(abf.dataX[:TCA],abf.dataY[:TCA],alpha=.2,color='k',lw=2)
        pylab.plot(abf.dataX[TCB:],abf.dataY[TCB:],alpha=.2,color='k',lw=2)
        pylab.plot(abf.dataX[TCA:TCB],abf.dataY[TCA:TCB],'o',alpha=.5,lw=4,mfc='none',mec='r')
        pylab.plot(abf.dataX[T1A:T1B],abf.dataY[T1A:T1B],alpha=.4,color='b')
        pylab.plot(abf.dataX[T2A:T2B],abf.dataY[T2A:T2B],alpha=.4,color='b')
        pylab.plot(abf.dataX[TCA:TCB],fitted,color='k',lw=2,ls="--")
        for i in [TA, TB]:
            pylab.axvline(i/abf.rate,color='k',ls='--',alpha=.4)
        for i in [P1,P2]:
            pylab.axhline(i,color='b',ls="--",alpha=.5)
        for i in [PCA,PCB,PP]:
            pylab.axhline(i,color='g',ls="--",alpha=.5)
    pylab.tight_layout()
    pylab.subplots_adjust(right=0.75)
    pylab.annotate(_msg,(.8,.75),ha='left',va='top',alpha=.5,
                   xycoords='figure fraction',family='monospace',size=10)
    pylab.annotate(_msg2,(.8,.95),ha='left',va='top',weight='bold',family='monospace',
                   xycoords='figure fraction',size=12,color='g')
    pylab.subplot(211)
    pylab.axis([None,abf.dataX[T2B]+.05,None,None])
    pylab.subplot(212)
    pylab.axis([(TB-20)/abf.rate,(TCB+20)/abf.rate,P1-20,PP+20])
    swhlab.plot.annotate(abf)
    for key in _keys:
        del key #be clean about screwing with globals()
    return

def test():
    """voltage clamp MT."""
    abf=swhlab.ABF(r'C:\Apps\pythonModules\abfs\16701010.abf')
    swhlab.memtest.memtest(abf) #performs memtest on all sweeps
    swhlab.memtest.checkSweep(abf) #lets you eyeball check how it did
    pylab.show()

def test2():
    """current clamp MT."""
    abf=swhlab.ABF(r'C:\Apps\pythonModules\abfs\16701006.abf')
    swhlab.memtest.memtest(abf) #performs memtest on all sweeps
    swhlab.memtest.checkSweep(abf) #lets you eyeball check how it did
    pylab.show()

if __name__=="__main__":
    #test()
    #test2()
    test3()
    print("DONE")