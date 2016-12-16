"""
methods related to detection/reporting of action potentials.
Good for deterining AP frequency and making gain functions.

Currently AP detection is locked into derivative threshold detection.
A new detection method warrants a new module.
The same class method names could be used though.

Detection is optimized for sweeps, not really continuous recordings.
There's a potential that an AP may be lost within a few ms from an edge.
"""

import logging
import numpy as np

import swhlab
from swhlab.core import ABF
import swhlab.common as cm

import sys
import os

ms=.001 # easy access to a millisecond

class AP:
    def __init__(self,abf):
        """
        Load an ABF and get ready to do AP detection.
        After detect(), all AP data is stored as a list of dicts in AP.APs
        """
        self.log = logging.getLogger("swhlab AP")
        self.log.setLevel(swhlab.loglevel)

        if abf in [None,False,'']:
            self.log.error("given invalid abf: [%s]",str(abf))
            return

        # prepare ABF class
        if type(abf) is str:
            self.log.debug("filename given, turning it into an ABF class")
            abf=ABF(abf)
        self.abf=abf

        # detection settings
        self.detect_over = 50 # must be at least this (mV/ms)
        self.detect_time1 = 0 # event detection starts here (sec)
        self.detect_time2 = abf.sweepLength # event detection ends here (sec)

        # data storage
        self.APs=False # becomes [] when detect() is run

    def info(self):
        print("%d APs in memory."%len(self.APs))

    ### DETECTION

    def ensureDetection(self):
        """
        run this before analysis. Checks if event detection occured.
        If not, runs AP detection on all sweeps.
        """
        if self.APs==False:
            self.log.debug("analysis attempted before event detection...")
            self.detect()

    def detect(self):
        """runs AP detection on every sweep."""
        self.log.info("initializing AP detection on all sweeps...")
        t1=cm.timeit()
        for sweep in range(self.abf.sweeps):
            self.detectSweep(sweep)
        self.log.info("AP analysis of %d sweeps found %d APs (completed in %s)",
                      self.abf.sweeps,len(self.APs),cm.timeit(t1))

    def detectSweep(self,sweep=0):
        """perform AP detection on current sweep."""

        if self.APs is False: # indicates detection never happened
            self.APs=[] # now indicates detection occured

        # delete every AP from this sweep from the existing array
        for i,ap in enumerate(self.APs):
            if ap["sweep"]==sweep:
                self.APs[i]=None
        if self.APs.count(None):
            self.log.debug("deleting %d existing APs from memory",self.APs.count(None))
            while None in self.APs:
                self.APs.remove(None)
        self.log.debug("initiating AP detection (%d already in memory)",len(self.APs))

        self.abf.derivative=True
        self.abf.setsweep(sweep)

        # detect potential AP (Is) by a dV/dT threshold crossing
        Is = cm.where_cross(self.abf.sweepD,self.detect_over)
        self.log.debug("initial AP detection: %d APs"%len(Is))

        # eliminate APs where dV/dT doesn't cross below -10 V/S within 2 ms
        for i,I in enumerate(Is):
            if np.min(self.abf.sweepD[I:I+2*self.abf.pointsPerMs])>-10:
                Is[i]=0
        Is=Is[np.nonzero(Is)]
        self.log.debug("after lower threshold checking: %d APs"%len(Is))

        # walk 1ms backwards and find point of +10 V/S threshold crossing
        for i,I in enumerate(Is):
            stepBack=0
            while(self.abf.sweepD[I-stepBack])>10 and stepBack/self.abf.pointsPerMs<1: #2ms max
                stepBack+=1
            Is[i]-=stepBack

        # analyze each AP
        sweepAPs=[]
        for i,I in enumerate(Is):
            try:
                timeInSweep=I/self.abf.pointsPerSec
                if timeInSweep<self.detect_time1 or timeInSweep>self.detect_time2:
                    continue # skip because it's not within the marks
                ap={} # create the AP entry
                ap["sweep"]=sweep # number of the sweep containing this AP
                ap["I"]=I # index sweep point of start of AP (10 mV/ms threshold crossing)
                ap["Tsweep"]=I/self.abf.pointsPerSec # time in the sweep of index crossing (sec)
                ap["T"]=ap["Tsweep"]+self.abf.sweepInterval*sweep # time in the experiment
                ap["Vthreshold"]=self.abf.sweepY[I] # threshold at rate of -10mV/ms

                # determine how many points from the start dV/dt goes below -10 (from a 5ms chunk)
                chunk=self.abf.sweepD[I:I+5*self.abf.pointsPerMs] # give it 5ms to cross once
                I_toNegTen=np.where(chunk<-10)[0][0]
                chunk=self.abf.sweepD[I+I_toNegTen:I+I_toNegTen+10*self.abf.pointsPerMs] # give it 30ms to cross back
                if not max(chunk)>-10:
                    self.log.debug("skipping unreal AP at T=%f"%ap["T"])
                    self.log.error("^^^ can you confirm this is legit?")
                    continue # probably a pre-AP "bump" to be ignored
                I_recover=np.where(chunk>-10)[0][0]+I_toNegTen+I # point where trace returns to above -10 V/S
                ap["dVfastIs"]=[I,I_recover] # span of the fast component of the dV/dt trace
                ap["dVfastMS"]=(I_recover-I)/self.abf.pointsPerMs # time (in ms) of this fast AP component

                # determine derivative min/max from a 2ms chunk which we expect to capture the fast AP
                chunk=self.abf.sweepD[ap["dVfastIs"][0]:ap["dVfastIs"][1]]
                ap["dVmax"]=np.max(chunk)
                ap["dVmaxI"]=np.where(chunk==ap["dVmax"])[0][0]+I
                ap["dVmin"]=np.min(chunk)
                ap["dVminI"]=np.where(chunk==ap["dVmin"])[0][0]+I
                if ap["dVmax"]<10 or ap["dVmin"]>-10:
                    self.log.debug("throwing out AP with low dV/dt to be an AP")
                    self.log.error("^^^ can you confirm this is legit?")
                    continue

                # before determining AP shape stats, see where trace recovers to threshold
                chunkSize=self.abf.pointsPerMs*10 #AP shape may be 10ms
                if len(Is)-1>i and Is[i+1]<(I+chunkSize): # if slow AP runs into next AP
                    chunkSize=Is[i+1]-I # chop it down
                if chunkSize<(self.abf.pointsPerMs*2):
                    continue # next AP is so soon, it's >500 Hz. Can't be real.
                ap["VslowIs"]=[I,I+chunkSize] # time range of slow AP dynamics
                chunk=self.abf.sweepY[I:I+chunkSize]

                # determine AP peak and minimum
                ap["Vmax"]=np.max(chunk)
                ap["VmaxI"]=np.where(chunk==ap["Vmax"])[0][0]+I
                chunkForMin=np.copy(chunk) # so we can destroy it
                chunkForMin[:ap["VmaxI"]-I]=np.inf # minimum won't be before peak now
                ap["Vmin"]=np.min(chunkForMin) # supposedly the minimum is the AHP
                ap["VminI"]=np.where(chunkForMin==ap["Vmin"])[0][0]+I
                if ap["VminI"]<ap["VmaxI"]:
                    self.log.error("-------------------------------")
                    self.log.error("how is the AHP before the peak?") #TODO: start chunk at the peak
                    self.log.error("-------------------------------")
                #print((I+len(chunk))-ap["VminI"],len(chunk))
                if (len(chunk))-((I+len(chunk))-ap["VminI"])<10:
                    self.log.error("-------------------------------")
                    self.log.error("HP too close for comfort!")
                    self.log.error("-------------------------------")

                ap["msRiseTime"]=(ap["VmaxI"]-I)/self.abf.pointsPerMs # time from threshold to peak
                ap["msFallTime"]=(ap["VminI"]-ap["VmaxI"])/self.abf.pointsPerMs # time from peak to nadir

                # determine halfwidth
                ap["Vhalf"]=np.average([ap["Vmax"],ap["Vthreshold"]]) # half way from threshold to peak
                ap["VhalfI1"]=cm.where_cross(chunk,ap["Vhalf"])[0]+I # time it's first crossed
                ap["VhalfI2"]=cm.where_cross(-chunk,-ap["Vhalf"])[1]+I # time it's second crossed
                ap["msHalfwidth"]=(ap["VhalfI2"]-ap["VhalfI1"])/self.abf.pointsPerMs # time between crossings

                # AP error checking goes here
                # TODO:

                # if we got this far, add the AP to the list
                sweepAPs.extend([ap])
            except Exception as e:
                self.log.error("crashed analyzing AP %d of %d",i,len(Is))
                self.log.error(cm.exceptionToString(e))
                #cm.pause()
                #cm.waitFor(30)
                #self.log.error("EXCEPTION!:\n%s"%str(sys.exc_info()))

        self.log.debug("finished analyzing sweep. Found %d APs",len(sweepAPs))
        self.APs.extend(sweepAPs)
        self.abf.derivative=False # leave it how we started

    ### ANALYSIS

    def get_times(self):
        """return an array of times (in sec) of all APs."""
        self.ensureDetection()
        times=[]
        for ap in self.APs:
            times.append(ap["T"])
        return np.array(sorted(times))

    def get_bySweep(self,feature="freqs"):
        """
        returns AP info by sweep arranged as a list (by sweep).

        feature:
            * "freqs" - list of instantaneous frequencies by sweep.
            * "firsts" - list of first instantaneous frequency by sweep.
            * "times" - list of times of each AP in the sweep.
            * "count" - numer of APs per sweep.
            * "average" - average instanteous frequency per sweep.
            * "median" - median instanteous frequency per sweep.
        """
        self.ensureDetection()
        bySweepTimes=[[]]*self.abf.sweeps

        # determine AP spike times by sweep
        for sweep in range(self.abf.sweeps):
            sweepTimes=[]
            for ap in self.APs:
                if ap["sweep"]==sweep:
                    sweepTimes.append(ap["Tsweep"])
            bySweepTimes[sweep]=sweepTimes

        # determine instantaneous frequencies by sweep
        bySweepFreqs=[[]]*self.abf.sweeps
        for i,times in enumerate(bySweepTimes):
            if len(times)<2:
                continue
            diffs=np.array(times[1:])-np.array(times[:-1])
            bySweepFreqs[i]=np.array(1/diffs).tolist()

        # give the user what they want
        if feature == "freqs":
            return bySweepFreqs

        elif feature == "firsts":
            result=np.zeros(self.abf.sweeps) # initialize to this
            for i,freqs in enumerate(bySweepFreqs):
                if len(freqs):
                    result[i]=freqs[0]
            return result

        elif feature == "times":
            return bySweepTimes

        elif feature == "count":
            result=np.zeros(self.abf.sweeps) # initialize to this
            for i,times in enumerate(bySweepTimes):
                result[i]=len(bySweepTimes[i])
            return result

        elif feature == "average":
            result=np.zeros(self.abf.sweeps) # initialize to this
            for i,freqs in enumerate(bySweepFreqs):
                if len(freqs):
                    result[i]=np.nanmean(freqs)
            return result

        elif feature == "median":
            result=np.zeros(self.abf.sweeps) # initialize to this
            for i,freqs in enumerate(bySweepFreqs):
                if len(freqs):
                    result[i]=np.nanmedian(freqs)
            return result

        else:
            self.log.error("get_bySweep() can't handle [%s]",feature)
            return None


if __name__=="__main__":
    #abfFile=r"C:\Users\scott\Documents\important\2016-07-01 newprotos\16701009.abf"
    abfFile=r"C:\Users\scott\Documents\important\abfs\16o14018.abf"
    ap=AP(abfFile)
    ap.detect_time2=1
    ap.detect()
    #print(ap.get_times())
    print(ap.get_bySweep("count"))

    print("DONE")