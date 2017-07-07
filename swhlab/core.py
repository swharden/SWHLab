"""
This module contains the core SWHLab class which provides ABF file access.
NeoIO provides ABF file access, the ABF class here simplifies it.
Plotting is strictly kept out of this module.
Analysis (event detection, etc) is also kept out of this module.
"""

# start out this way so tests will import the local swhlab module
import sys
import os
importPath=os.path.abspath('../')
if not importPath in sys.path and os.path.isdir(importPath+"/swhlab/"):
    sys.path.insert(0,importPath)
import swhlab

# now import things regularly
import logging
import webinspect
from neo import io
import glob
import pprint
import webbrowser
import numpy as np

def abfIDfromFname(fname):
    """given a filename, return the ABFs ID string."""
    fname=os.path.abspath(fname)
    basename=os.path.basename(fname)
    return os.path.splitext(basename)[0]

def abfProtocol(fname):
    """
    determine the comment cooked in the protocol.
    This is done by reading the binary contents of the header.
    """
    f=open(fname,'rb')
    raw=f.read(20*1000) #it should be in the first 20k of the file
    f.close()
    protoComment="unknown"
    raw=raw.replace(b"SWHLab4[",b"SWH[")
    raw=raw.replace(b"SWHLab5[",b"SWH[")
    raw=raw.replace(b"SWHLab[",b"SWH[")
    if b"SWH[" in raw:
        protoComment=raw.split(b"SWH[")[1].split(b"]",1)[0]
    else:
        protoComment="?"
    if not type(protoComment) is str:
        protoComment=protoComment.decode("utf-8")
    return protoComment

def headerHTML(header,fname):
        """given the bytestring ABF header, make and launch HTML."""
        html="<html><body><code>"
        html+="<h2>%s</h2>"%(fname)
        html+=pprint.pformat(header, indent=1)
        html=html.replace("\n",'<br>').replace(" ","&nbsp;")
        html=html.replace(r"\x00","")
        html+="</code></body></html>"
        print("saving header file:",fname)
        f=open(fname,'w')
        f.write(html)
        f.close()
        webbrowser.open(fname)

class ABF:

    def __init__(self, fname, createFolder=False):
        """
        Load an ABF and makes its stats and sweeps easily available.

        Arguments:
            fname - filename of an ABF object
            createFolder - if True, the ./swhlab/ folder will be created
        """
        logging.basicConfig(format=swhlab.logFormat, datefmt=swhlab.logDateFormat, level=swhlab.loglevel)
        self.log = logging.getLogger("swhlab ABF")
        self.log.setLevel(swhlab.loglevel)
        if "ABF object" in str(fname):
            self.log.debug("reusing same ABF object")
            for item in sorted(dir(fname)):
                try:
                    setattr(self,item,getattr(fname,item))
                except:
                    pass
            return
        self.log.debug("_"*60)
        self.log.info("SWHLab (%s) loading ABF [%s]",swhlab.__version__,str(fname))
        if not os.path.exists(str(fname)):
            self.log.error("path doesn't exist!")
            return

        # load the ABF and populate properties
        self.ABFreader = io.AxonIO(filename=fname)
        self.ABFblock = self.ABFreader.read_block(lazy=False, cascade=True)
        self.header=self.ABFreader.read_header()
        self.protocomment=abfProtocol(fname) # get ABF file comment
        self.ID=abfIDfromFname(fname) # filename without extension
        self.filename=os.path.abspath(fname) # full path to file on disk
        self.fileID=os.path.abspath(os.path.splitext(self.filename)[0]) # no extension
        self.outFolder=os.path.abspath(os.path.dirname(fname)+"/swhlab/") # save stuff here
        self.outPre=os.path.join(self.outFolder,self.ID)+'_' # save files prefixed this
        self.sweeps=self.ABFblock.size["segments"] # number of sweeps in ABF
        self.timestamp=self.ABFblock.rec_datetime # when the ABF recording started

        # these I still have to read directly out of the header
        self.holding = self.header['listDACInfo'][0]['fDACHoldingLevel'] #clamp current or voltage

        # we've pulled what we can out of the header, now proceed with advanced stuff
        self.derivative=False # whether or not to use the first derivative
        self.setsweep() # run setsweep to populate sweep properties
        self.comments_load() # populate comments
        self.kernel=None # variable which may be set for convolution
        if createFolder:
            self.output_touch() # make sure output folder exists
        #TODO: detect if invalid or corrupted ABF
        self.log.debug("ABF loaded. (protocol: %s)"%self.protocomment)

    def setsweep(self, sweep=0, channel=0):
        """set the sweep and channel of an ABF. Both start at 0."""
        try:
            sweep=int(sweep)
        except:
            self.log.error("trying to set sweep to [%s]",sweep)
            return
        if sweep<0:
            sweep=self.sweeps-1-sweep # if negative, start from the end
        sweep=max(0,min(sweep,self.sweeps-1)) # correct for out of range sweeps
        if 'sweep' in dir(self) and self.sweep == sweep and self.derivative is False:
            self.log.debug("sweep %d already set",sweep)
            return
        #self.log.debug("loading sweep %d (Ch%d)",sweep,channel)
        self.channels=self.ABFblock.segments[sweep].size["analogsignals"]
        if self.channels>1 and sweep==0:
            self.log.info("WARNING: multichannel not yet supported!") #TODO:
        self.trace = self.ABFblock.segments[sweep].analogsignals[channel]
        self.sweep=sweep # currently selected sweep
        self.channel=channel # currently selected channel

        # sweep information
        self.rate = int(self.trace.sampling_rate) # Hz
        self.period = float(1/self.rate) # seconds (inverse of sample rate)
        self.pointsPerSec = int(self.rate) # for easy access
        self.pointsPerMs = int(self.rate/1000.0) # for easy access
        self.sweepSize = len(self.trace) # number of data points per sweep
        self.sweepInterval = self.trace.duration.magnitude # sweep interval (seconds)
        self.sweepLength = float(self.trace.t_stop-self.trace.t_start) # in seconds
        self.length = self.sweepLength*self.sweeps # length (sec) of total recording
        self.lengthMinutes = self.length/60.0 # length (minutes) of total recording

        if str(self.trace.dimensionality) == 'pA':
            self.units,self.units2="pA","clamp current (pA)"
            self.unitsD,self.unitsD2="pA/ms","current velocity (pA/ms)"
            self.protoUnits,self.protoUnits2="mV","command voltage (mV)"
        elif str(self.trace.dimensionality) == 'mV':
            self.units,self.units2="mV","membrane potential (mV)"
            self.unitsD,self.unitsD2="V/s","potential velocity (V/s)"
            self.protoUnits,self.protoUnits2="pA","command current (pA)"
        else:
            self.units,self.units2="?","unknown units"
            self.unitsD,self.unitsD2="?","unknown units"

        # sweep data
        self.sweepY = self.trace.magnitude # sweep data (mV or pA)
        self.sweepT = self.trace.times.magnitude # actual sweep times (sec)
        self.sweepStart = float(self.trace.t_start) # time start of sweep (sec)
        self.sweepX2 = self.sweepT-self.trace.t_start.magnitude # sweeps overlap
        self.sweepX = self.sweepX2+sweep*self.sweepInterval # assume no gaps
        if self.derivative:
            self.log.debug("taking derivative")
            #self.sweepD=np.diff(self.sweepY) # take derivative
            self.sweepD=self.sweepY[1:]-self.sweepY[:-1] # better?
            self.sweepD=np.insert(self.sweepD,0,self.sweepD[0]) # add a point
            self.sweepD/=(self.period*1000) # correct for sample rate
        else:
            self.sweepD=[0] # derivative is forced to be empty

        # generate the protocol too
        self.generate_protocol()

    def sweepList(self):
        """return a list of sweep numbers."""
        return range(self.sweeps)

    def setsweeps(self):
        """iterate over every sweep"""
        for sweep in range(self.sweeps):
            self.setsweep(sweep)
            yield self.sweep

    def comments_load(self):
        """read the header and populate self with information about comments"""
        self.comment_times,self.comment_sweeps,self.comment_tags=[],[],[]
        self.comments=0 # will be >0 if comments exist
        self.comment_text=""

        try:
            # this used to work
            self.comment_tags = list(self.ABFblock.segments[0].eventarrays[0].annotations['comments'])
            self.comment_times = list(self.ABFblock.segments[0].eventarrays[0].times/self.trace.itemsize)
            self.comment_sweeps = list(self.comment_times)
        except:
            # now this notation seems to work
            for events in self.ABFblock.segments[0].events: # this should only happen once actually
                self.comment_tags = events.annotations['comments'].tolist()
                self.comment_times = np.array(events.times.magnitude/self.trace.itemsize)
                self.comment_sweeps = self.comment_times/self.sweepInterval

        for i,c in enumerate(self.comment_tags):
            self.comment_tags[i]=c.decode("utf-8")

    def generate_protocol(self):
        """
        Recreate the command stimulus (protocol) for the current sweep.
        It's not stored point by point (that's a waste of time and memory!)
        Instead it's stored as a few (x,y) points which can be easily graphed.

        TODO: THIS
        for segment in abf.ABFreader.read_protocol():
            for analogsignal in segment.analogsignals:
                print(analogsignal)
                plt.plot(analogsignal)
                plt.show()
                plt.close('all')

        """
        # TODO: elegantly read the protocol like this:
            #abf.ABFreader.read_protocol()[0].analogsignals()[sigNum]



        # TODO: right now this works only for the first channel

        # correct for weird recording/protocol misalignment
        #what is magic here? 64-bit data points? #1,000,000/64 = 15625 btw
        self.offsetX = int(self.sweepSize/64)

        # if there's not a header, get out of here!
        if not len(self.header['dictEpochInfoPerDAC']):
            self.log.debug("no protocol defined, so I'll make one")
            self.protoX,self.protoY=[0,self.sweepX[-1]],[self.holding,self.holding]
            self.protoSeqX,self.protoSeqY=[0],[self.holding]
            return

        # load our protocol from the header
        proto=self.header['dictEpochInfoPerDAC'][self.channel]

        # prepare our (x,y) pair arrays
        self.protoX,self.protoY=[] ,[]

        # assume our zero time point is the "holding" value
        self.protoX.append(0)
        self.protoY.append(self.holding) #TODO: what is this???

        # now add x,y points for each change in the protocol
        for step in proto:
            dX = proto[step]['lEpochInitDuration']
            Y = proto[step]['fEpochInitLevel']+proto[step]['fEpochLevelInc']*self.sweep
            # we have a new Y value, so add it to the last time point
            self.protoX.append(self.protoX[-1])
            self.protoY.append(Y)
            # now add the same Y point after "dX" amount of time
            self.protoX.append(self.protoX[-1]+dX)
            self.protoY.append(Y)
            # TODO: detect ramps and warn what's up

        # The last point is probably holding current
        finalVal=self.holding #regular holding
        # although if it's set to "use last value", maybe that should be the last one
        if self.header['listDACInfo'][0]['nInterEpisodeLevel']:
            finalVal=self.protoY[-1]

        # add the shift to the final value to the list
        self.protoX.append(self.protoX[-1])
        self.protoY.append(finalVal)
        # and again as the very last time point
        self.protoX.append(self.sweepSize)
        self.protoY.append(finalVal)

        # update the sequence of protocols now (eliminate duplicate entries)
        for i in range(1,len(self.protoX)-1): #correct for weird ABF offset issue.
            self.protoX[i]=self.protoX[i]+self.offsetX
        self.protoSeqY=[self.protoY[0]]
        self.protoSeqX=[self.protoX[0]]
        for i in range(1,len(self.protoY)):
            if not self.protoY[i]==self.protoY[i-1]:
                self.protoSeqY.append(self.protoY[i])
                self.protoSeqX.append(self.protoX[i])
        if self.protoY[0]!=self.protoY[1]:
            self.protoY.insert(1,self.protoY[0])
            self.protoX.insert(1,self.protoX[1])
            self.protoY.insert(1,self.protoY[0])
            self.protoX.insert(1,self.protoX[0]+self.offsetX/2)
        self.protoSeqY.append(finalVal)
        self.protoSeqX.append(self.sweepSize)

        # convert lists to numpy arrays and do any final conversions
        self.protoX=np.array(self.protoX)/self.pointsPerSec
        self.protoY=np.array(self.protoY)

    def get_protocol(self,sweep):
        """
        given a sweep, return the protocol as [Xs,Ys].
        This is good for plotting/recreating the protocol trace.
        There may be duplicate numbers.
        """
        self.setsweep(sweep)
        return list(self.protoX),list(self.protoY)

    def get_protocol_sequence(self,sweep):
        """
        given a sweep, return the protocol as condensed sequence.
        This is better for comparing similarities and determining steps.
        There should be no duplicate numbers.
        """
        self.setsweep(sweep)
        return list(self.protoSeqX),list(self.protoSeqY)

    def clamp_values(self,timePoint=0):
        """
        return an array of command values at a time point (in sec).
        Useful for things like generating I/V curves.
        """
        print("proto_clamp_at_time NOT YET IMPLIMENTED") #TODO:
        return 0

    def epochTimes(self,nEpoch=2):
        """
        alternative to the existing abf protocol stuff
        return the start/stop time of an epoch.
        Epoch start at zero.
        A=0, B=1, C=2, D=3, ...
        """
        times=[]
        durations=[]
        for epoch in self.header['dictEpochInfoPerDAC'][self.channel].values():
            print(epoch['lEpochInitDuration']/self.pointsPerSec)
            times.append(sum(durations))
            durations.append(epoch['lEpochInitDuration']/self.pointsPerSec)
        times.append(sum(durations))
        times=np.array(times)+self.offsetX/self.pointsPerSec # WHY?!?
        if nEpoch:
            return times[nEpoch],times[nEpoch+1]
        else:
            return times

    ### advanced data access

    def average(self,t1=0,t2=None,setsweep=False):
        """return the average of part of the current sweep."""
        if setsweep:
            self.setsweep(setsweep)
        if t2 is None or t2>self.sweepLength:
            t2=self.sweepLength
            self.log.debug("resetting t2 to [%f]",t2)
        t1=max(t1,0)
        if t1>t2:
            self.log.error("t1 cannot be larger than t2")
            return False
        I1,I2=int(t1*self.pointsPerSec),int(t2*self.pointsPerSec)
        if I1==I2:
            return np.nan
        return np.average(self.sweepY[I1:I2])

    def averageSweep(self,sweepFirst=0,sweepLast=None):
        """
        Return a sweep which is the average of multiple sweeps.
        For now, standard deviation is lost.
        """
        if sweepLast is None:
            sweepLast=self.sweeps-1
        nSweeps=sweepLast-sweepFirst+1
        runningSum=np.zeros(len(self.sweepY))
        self.log.debug("averaging sweep %d to %d",sweepFirst,sweepLast)
        for sweep in np.arange(nSweeps)+sweepFirst:
            self.setsweep(sweep)
            runningSum+=self.sweepY.flatten()
        average=runningSum/nSweeps
        #TODO: standard deviation?
        return average

    def kernel_gaussian(self, sizeMS, sigmaMS=None, forwardOnly=False):
        """create kernel based on this ABF info."""
        sigmaMS=sizeMS/10 if sigmaMS is None else sigmaMS
        size,sigma=sizeMS*self.pointsPerMs,sigmaMS*self.pointsPerMs
        self.kernel=swhlab.common.kernel_gaussian(size,sigma,forwardOnly)
        return self.kernel

    def sweepYfiltered(self):
        """
        Get the filtered sweepY of the current sweep.
        Only works if self.kernel has been generated.
        """
        assert self.kernel is not None
        return swhlab.common.convolve(self.sweepY,self.kernel)

    def sweepYsmartbase(self):
        """return the sweep with sweepYfiltered subtracted from it."""
        return self.sweepY-self.sweepYfiltered()

    def phasicNet(self,biggestEvent=50,m1=.5,m2=None):
        """
        Calculates the net difference between positive/negative phasic events
        Returns return the phasic difference value of the current sweep.

        Arguments:
            biggestEvent (int): the size of the largest event anticipated
            m1 (int, optional): the time (sec) to start analyzing
            m2 (int, optional): the time (sec) to end analyzing

        Example:
            abf=swhlab.ABF(abfFile)
            abf.kernel=abf.kernel_gaussian(sizeMS=500) # kernel for smart baseline
            diff=[]
            for sweep in abf.setsweeps():
                print("Sweep",sweep)
                diff.append(analyzeSweep(abf,plot=True,label="sweep %d"%sweep))
            print(diff)
        """

        # determine marks (between which we will analyze)
        m1=0 if m1 is None else self.pointsPerSec*m1
        m2=-1 if m2 is None else self.pointsPerSec*m2

        # acquire the baseline-subtracted sweep
        Y=self.sweepYsmartbase()[int(m1):int(m2)]

        # create the histogram
        nBins=1000
        hist,bins=np.histogram(Y,bins=nBins,range=[-biggestEvent,biggestEvent],density=True)
        histSmooth=swhlab.common.lowpass(hist)

        # normalize height to 1
        #TODO: should it be normalized first or not?
        #YES if reporting the ratio of the up/down area, NO if reporting the up-down difference
        #hist,histSmooth=hist/max(histSmooth),histSmooth/max(histSmooth)

        # center the peak at 0 pA
        peakI=np.where(histSmooth==max(histSmooth))[0][0]
        hist=np.roll(hist,int(nBins/2-peakI))
        histSmooth=np.roll(histSmooth,int(nBins/2-peakI))

        # calculate our mirrored difference
        downward,upward=np.split(histSmooth,2)
        downward=downward[::-1]
        diff=np.sum(upward-downward)

        # convert our "pA/time" to "pA/sec"
        diff=diff/(len(Y)/self.pointsPerSec)

        return diff

    ### file organization

    def output_touch(self):
        """ensure the ./swhlab/ folder exists."""
        if not os.path.exists(self.outFolder):
            self.log.debug("creating %s",self.outFolder)
            os.mkdir(self.outFolder)

    def output_clean(self):
        """delete all ./swhlab/ data related to this ABF."""
        for fname in glob.glob(self.outPre+"*"):
            print("PRETENDING TO DELETE",fname)
        pass

    ### developer assistance

    def inspect(self):
        """
        Generate HTML containing information about NeoIO objects.
        This is useful when trying to figure out how to extract data from ABFs.
        """
#        webinspect.blacklist=[] # clears the blacklist
#        webinspect.launch(self.ABFblock.segments[0].eventarrays[0],'self.ABFblock.segments[0].eventarrays[0]')
#        webinspect.blacklist=['parents'] # prevents parents() from being executed
#        webinspect.launch(self.ABFblock.segments[0].analogsignals[0],'self.ABFblock.segments[0].analogsignals[0]')
#        webinspect.blacklist=['t_start','t_stop'] # prevents t_start() and t_stop() from beeing executed
#        webinspect.launch(self.ABFblock.segments[0],'self.ABFblock.segments[0]')
#        webinspect.blacklist=[] # clears the blacklist
#        webinspect.launch(self.ABFblock,'self.ABFblock')
#        webinspect.blacklist=[] # clears the blacklist
#        webinspect.launch(self.ABFreader,'self.ABFreader')
        headerFile=r"C:\Users\swharden\Documents\temp\header.html"
        headerHTML(self.header,headerFile)



if __name__=="__main__":
    import matplotlib.pyplot as plt
    abfFile=r"\\SPIKE\X_DRIVE\Data\SCOTT\2017-05-15 LHA TGOT\17622011.abf"
    abf=ABF(abfFile)
    print(abf.protocomment)
    print("DONE")
#    #abf.kernel_gaussian(1)
#    plt.subplot(211)
#    plt.plot(abf.sweepX,abf.sweepY)
#    plt.plot(abf.sweepX,abf.sweepYfiltered())
#    plt.margins(0,.1)
#    plt.subplot(212)
#    plt.plot(abf.protoX,abf.protoY,color='r')
#    plt.margins(0,.1)
