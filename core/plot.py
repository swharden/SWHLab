"""
Things related to plotting with matplotlib.
Replace this class with another class if you prefer gnuplot or something.
swhlab.plot.sweep() is the bread and butter of this module. Read the docs.

Example usage:
    abf=swhlab.ABF('../abfs/aps.abf')
    swhlab.plot.sweep(abf,8,newFigure=True) #single sweep
    swhlab.plot.sweep(abf,'all',newFigure=True) #overlay
    swhlab.plot.sweep(abf,'all',newFigure=True,continuous=True) #continuous
    swhlab.plot.sweep(abf,'all',newFigure=True,offsetY=100) #stacked
"""

import os
import sys
import pylab
import numpy as np
import time
import datetime

import swhlab
import swhlab.core.common as cm

def sweep_and_protocol(abf):
    pylab.figure(figsize=(8,6))

    ax=pylab.subplot(211)
    pylab.ylabel("measurement (%s)"%abf.units)
    pylab.plot(abf.dataY,color='b')
    for I in abf.protoX:
        pylab.axvline(I,color='k',alpha=.5,ls='--')
    pylab.margins(0,.05)

    pylab.subplot(212,sharex=ax)
    pylab.ylabel("command (%s)"%abf.unitsCommand)
    pylab.plot(abf.protoX,abf.protoY,color='r',marker='.',ms=10,alpha=.2)
    pylab.margins(0,.05)
    for px,py,pi in zip(abf.protoX,abf.protoY,range(len(abf.protoY))):
        msg=""
        if pi==3:
            msg+=" (Xc)"
        elif pi==4:
            msg+=" (Xd)"
        pylab.text(px,py,str(pi)+msg,va='top',ha='center')
    pylab.margins(.02,.1)
    pylab.axis([0,4000,-90,-50])

def values_above_sweep(abf,dataI,dataY,ylabel="",useFigure=None):
    """
    To make plots like AP frequency over original trace.
    dataI=[i] #the i of the sweep
    dataY=[1.234] #something like inst freq
    """
    xOffset = abf.currentSweep*abf.sweepInterval
    if not useFigure: #just passing the figure makes it persistant!
        pylab.figure(figsize=(8,6))

    ax=pylab.subplot(221)
    pylab.grid(alpha=.5)
    if len(dataI):
        pylab.plot(abf.dataX[dataI],dataY,'.',ms=10,alpha=.5,
                   color=abf.colormap[abf.currentSweep])
    pylab.margins(0,.1)
    pylab.ylabel(ylabel)

    pylab.subplot(223,sharex=ax)
    pylab.grid(alpha=.5)
    pylab.plot(abf.dataX,abf.dataY,color=abf.colormap[abf.currentSweep],alpha=.5)
    pylab.ylabel("raw data (%s)"%abf.units)

    ax2=pylab.subplot(222)
    pylab.grid(alpha=.5)
    if len(dataI):
        pylab.plot(abf.dataX[dataI]+xOffset,dataY,'.',ms=10,alpha=.5,
                   color=abf.colormap[abf.currentSweep])
    pylab.margins(0,.1)
    pylab.ylabel(ylabel)

    pylab.subplot(224,sharex=ax2)
    pylab.grid(alpha=.5)
    pylab.plot(abf.dataX+xOffset,abf.dataY,color=abf.colormap[abf.currentSweep])
    pylab.ylabel("raw data (%s)"%abf.units)

    pylab.tight_layout()

def gain(abf):
    """easy way to plot a gain function."""
    Ys=np.nan_to_num(swhlab.ap.getAvgBySweep(abf,'freq'))
    Xs=abf.clampValues(abf.dataX[int(abf.protoSeqX[1]+.01)])
    swhlab.plot.new(abf,title="gain function",xlabel="command current (pA)",
                    ylabel="average inst. freq. (Hz)")
    pylab.plot(Xs,Ys,'.-',ms=20,alpha=.5,color='b')
    pylab.axhline(0,alpha=.5,lw=2,color='r',ls="--")
    pylab.margins(.1,.1)

def IV(abf,T1,T2,plotToo=True,color='b'):
    """
    Given two time points (seconds) return IV data.
    Optionally plots a fancy graph (with errorbars)
    Returns [[AV],[SD]] for the given range.
    """
    rangeData=abf.average_data([[T1,T2]]) #get the average data per sweep
    AV,SD=rangeData[:,0,0],rangeData[:,0,1] #separate by average and SD
    Xs=abf.clampValues(T1) #get clamp values at time point T1
    if plotToo:
        new(abf) #do this so it's the right shape and size

        # plot the original sweep
        pylab.subplot(221)
        pylab.title("sweep data")
        pylab.xlabel("time (s)")
        pylab.ylabel("Measurement (%s)"%abf.units)
        sweep(abf,'all',protocol=False)
        pylab.axis([None,None,np.min(rangeData)-50,np.max(rangeData)+50])
        pylab.axvspan(T1,T2,alpha=.1,color=color) #share measurement region
        pylab.margins(0,.1)

        # plot the data zoomed in
        pylab.subplot(223)
        pylab.title("measurement region")
        pylab.xlabel("time (s)")
        pylab.ylabel("Measurement (%s)"%abf.units)
        sweep(abf,'all',protocol=False)
        pylab.axis([T1-.05,T2+.05,np.min(rangeData)-50,np.max(rangeData)+50])
        pylab.axvspan(T1,T2,alpha=.1,color=color) #share measurement region
        pylab.margins(0,.1)

        # plot the protocol
        pylab.subplot(222)
        pylab.title("protocol")
        pylab.xlabel("time (s)")
        pylab.ylabel("Command (%s)"%abf.unitsCommand)
        sweep(abf,'all',protocol=True)
        pylab.axvspan(T1,T2,alpha=.1,color=color) #share measurement region
        pylab.margins(0,.1)

        # plot the I/V
        pylab.subplot(224)
        pylab.grid(alpha=.5)
        pylab.title("command / measure relationship")
        pylab.xlabel("Command (%s)"%abf.unitsCommand)
        pylab.ylabel("Measurement (%s)"%abf.units)
        pylab.errorbar(Xs,AV,SD,capsize=0,marker='.',color=color)
        if abf.units=="pA":
            pylab.axhline(0,alpha=.5,lw=2,color='r',ls="--")
            pylab.axvline(-70,alpha=.5,lw=2,color='r',ls="--")
        else:
            pylab.axhline(-70,alpha=.5,lw=2,color='r',ls="--")
            pylab.axvline(0,alpha=.5,lw=2,color='r',ls="--")
        pylab.margins(.1,.1)
    annotate(abf)
    return AV,SD

def comments(abf,minutes=False):
    """draw vertical lines at comment points. Defaults to seconds."""
    if not len(abf.commentTimes):
        return
    for i in range(len(abf.commentTimes)):
        t,c = abf.commentTimes[i],abf.commentTags[i]
        if minutes:
            t=t/60
        pylab.axvline(t,lw=1,color='r',ls="--",alpha=.5)
        X1,X2,Y1,Y2=pylab.axis()
        Y2=Y2-abs(Y2-Y1)*.02
        pylab.text(t,Y2,c,size=8,color='r',rotation='vertical',
                   ha='right',va='top',weight='bold',alpha=.5)
        if minutes:
            pylab.xlabel("minutes")
        else:
            pylab.xlabel("seconds")

#def continuous(abf):
#    """plot all sweeps (like gap free)."""
#    sweep(abf,'all',continuous=True)


#def plot_continuous(abf):
#    """plot all data continuously. Looks like gap free."""
#    #TODO: ELIMINATE THIS!
#    plot_new(abf)
#    for i in range(abf.sweeps):
#        ABF.setSweep(abf,i)
#        pylab.plot(abf.dataX+abf.dataStart,abf.dataY,'b-')
#    pylab.axis([0,abf.sweeps*abf.sweepInterval,None,None])

#def stacked(abf,offset=100):
#    """plot every sweep stacked on top of itself (not an overlay)."""
#    #TODO: eliminate, make vertical offset with setsweep()
#    new(abf)
#    for i in range(abf.sweeps):
#        abf.setSweep(abf,i)
#        pylab.plot(abf.dataX,abf.dataY+i*offset,'b-')
#    pylab.gca().get_yaxis().set_visible(False)
#    pylab.margins(0,.02) #give a little padding to the data

def dual(ABF):
    """Plot two channels of current sweep (top/bottom)."""
    new(ABF)
    pylab.subplot(211)
    pylab.title("Input A (channel 0)")
    ABF.channel=0
    sweep(ABF)
    pylab.subplot(212)
    pylab.title("Input B (channel 1)")
    ABF.channel=1
    sweep(ABF)


def sweep(ABF,sweep=None,rainbow=True,alpha=None,protocol=False,color='b',
               continuous=False,offsetX=0,offsetY=0,minutes=False,
               decimate=None,newFigure=False):
    """
    Load a particular sweep then plot it.
    If sweep is None or False, just plot current dataX/dataY.
    If rainbow, it'll make it color coded prettily.
    """
    if len(pylab.get_fignums())==0 or newFigure:
        new(ABF,True)
    if offsetY>0:
        pylab.grid(None)

    # figure which sweeps to plot
    if sweep is None:
        sweeps=[ABF.currentSweep]
        if not ABF.currentSweep:
            sweeps=[0]
    elif sweep=="all":
        sweeps=range(0,ABF.sweeps)
    elif type(sweep) in [int,float]:
        sweeps=[int(sweep)]
    elif type(sweep) is list:
        sweeps=sweep
    else:
        print("DONT KNOW WHAT TO DO WITH THIS SWEEPS!!!\n",type(sweep),sweep)

    #figure out offsets:
    if continuous:
        offsetX=ABF.sweepInterval

    # determine the colors to use
    colors=[color]*len(sweeps) #detault to blue
    if rainbow and len(sweeps)>1:
        for i in range(len(sweeps)):
            colors[i]=ABF.colormap[i]
    if alpha is None and len(sweeps)==1:
        alpha=1
    if rainbow and alpha is None:
        alpha=.5

    # correct for alpha
    if alpha is None:
        alpha=1

    # conversion to minutes?
    if minutes == False:
        minutes=1
    else:
        minutes=60
        pylab.xlabel("minutes")

    ABF.decimateMethod=decimate
    # do the plotting of each sweep
    for i in range(len(sweeps)):
        ABF.setSweep(sweeps[i])
        if protocol:
            pylab.plot((np.array(ABF.protoX)/ABF.rate+offsetX*i)/minutes,
                       ABF.protoY+offsetY*i,
                       alpha=alpha,color=colors[i])
        else:
            pylab.plot((ABF.dataX+offsetX*i)/minutes,
                       ABF.dataY+offsetY*i,alpha=alpha,color=colors[i])
    ABF.decimateMethod=None
    pylab.margins(0,.02)

def annotate(abf):
    """stamp the bottom with file info."""
    msg="SWHLab %s "%str(swhlab.VERSION)
    msg+="ID:%s "%abf.ID
    msg+="CH:%d "%abf.channel
    msg+="PROTOCOL:%s "%abf.protoComment
    msg+="COMMAND: %d%s "%(abf.holding,abf.units)
    msg+="GENERATED:%s "%'{0:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
    pylab.annotate(msg,(.001,.001),xycoords='figure fraction',ha='left',
                   va='bottom',color='#999999',family='monospace',size=8,
                   weight='bold')
    if abf.nADC>1:
        msg="Ch %d/%d"%(abf.channel+1,abf.nADC)
        pylab.annotate(msg,(.01,.99),xycoords='figure fraction',ha='left',
                       va='top',color='#FF0000',family='monospace',size=12,
                       weight='bold')

def new(ABF,forceNewFigure=False,title=None,xlabel=None,ylabel=None):
    """
    makes a new matplotlib figure with default dims and DPI.
    Also labels it with pA or mV depending on ABF.
    """
    if len(pylab.get_fignums()) and forceNewFigure==False:
        #print("adding to existing figure")
        return
    pylab.figure(figsize=(8,6))
    pylab.grid(alpha=.5)
    pylab.title(ABF.ID)
    pylab.ylabel(ABF.units)
    pylab.xlabel("seconds")
    if xlabel:
        pylab.xlabel(xlabel)
    if ylabel:
        pylab.ylabel(ylabel)
    if title:
        pylab.title(title)
    annotate(ABF)

def show(abf):
    """showing is the same as saving without a filename."""
    save(abf)

def save(abf,fname=None,tag=None,width=700,close=True,facecolor='w',
              resize=True):
    """
    Save the pylab figure somewhere.
    If fname==False, show it instead.
    Height force > dpi force
    if a tag is given instead of a filename, save it alongside the ABF
    """
    if len(pylab.gca().get_lines())==0:
        print("can't save, no figure!")
        return
    if resize:
        pylab.tight_layout()
        pylab.subplots_adjust(bottom=.1)
    annotate(abf)
    if tag:
        fname = abf.outpath+abf.ID+"_"+tag+".png"
    inchesX,inchesY = pylab.gcf().get_size_inches()
    dpi=width/inchesX
    if fname:
        if not os.path.exists(abf.outpath):
            os.mkdir(abf.outpath)
        print(" <- saving [%s] at %d DPI (%dx%d)"%(os.path.basename(fname),dpi,inchesX*dpi,inchesY*dpi))
        pylab.savefig(fname,dpi=dpi,facecolor=facecolor)
    else:
        pylab.show()
    if close:
        pylab.close()

def test():
    abf=swhlab.ABF('../abfs/aps.abf')
    swhlab.plot.sweep(abf,8,newFigure=True) #single sweep
    swhlab.plot.sweep(abf,'all',newFigure=True) #overlay
    swhlab.plot.sweep(abf,'all',newFigure=True,continuous=True) #continuous
    swhlab.plot.sweep(abf,'all',newFigure=True,offsetY=100) #stacked


if __name__=="__main__":
    test()
    print("DONE")