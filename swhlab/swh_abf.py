"""
This module contains the core SWHLab class which provides ABF file access.
NeoIO provides ABF file access, the ABF class here simplifies it.
Plotting is strictly kept out of this module.
Analysis (event detection, etc) is also kept out of this module.
"""

import os
import logging
import webinspect
from neo import io
import glob
import pprint
import webbrowser
import numpy as np


import sys
sys.path.append("../") #TODO: MAKE THIS BETTER
import swhlab.version as version

def abfID(fname):
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
    raw=f.read(5000) #it should be in the first 5k of the file
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
 
    def __init__(self, fname, createFolder=True, loglevel=version.logLevel):        
        """
        Load an ABF and makes its stats and sweeps easily available.
        
        Arguments:
            fname - filename of an ABF object
            createFolder - if True, the ./swhlab/ folder will be created
        """
        logging.basicConfig(format=version.logFormat, datefmt=version.logDateFormat, level=loglevel)
        self.log = logging.getLogger("swhlab ABF")
        self.log.setLevel(loglevel)
        if "ABF object" in str(fname):
            self.log.debug("reusing same ABF object")
            for item in sorted(dir(fname)):
                try:
                    setattr(self,item,getattr(fname,item))
                except:
                    pass
            return
        self.log.debug("_"*60)    
        self.log.info("SWHLab (%s) loading ABF [%s]",version.__version__,str(fname))        
        if not os.path.exists(str(fname)):
            self.log.error("path doesn't exist!")
            return
            
        # load the ABF and populate properties
        self.ABFreader = io.AxonIO(filename=fname)
        self.ABFblock = self.ABFreader.read_block(lazy=False, cascade=True)     
        self.header=self.ABFreader.read_header()
        self.protocomment=abfProtocol(fname) # get ABF file comment
        self.ID=abfID(fname) # filename without extension
        self.filename=os.path.abspath(fname) # full path to file on disk
        self.fileID=os.path.abspath(os.path.splitext(self.filename)[0]) # no extension
        self.outFolder=os.path.abspath(os.path.dirname(fname)+"/swhlab/") # save stuff here
        self.outPre=os.path.join(self.outFolder,self.ID)+'_' # save files prefixed this
        self.sweeps=self.ABFblock.size["segments"] # number of sweeps in ABF
        self.timestamp=self.ABFblock.rec_datetime # when the ABF recording started
        self.derivative=False # whether or not to use the first derivative
        self.setsweep() # run setsweep to populate sweep properties
        self.comments_load() # populate comments
        if createFolder:
            self.output_touch() # make sure output folder exists
        #TODO: detect if invalid or corrupted ABF
        self.log.debug("ABF loaded. (protocol: %s)"%self.protocomment)    
        
    def setsweep(self, sweep=0, channel=0):
        """set the sweep and channel of an ABF. Both start at 0."""
        if sweep<0:
            sweep=self.sweeps-1-sweep # if negative, start from the end
        sweep=max(0,min(sweep,self.sweeps-1)) # correct for out of range sweeps
        if 'sweep' in dir(self) and self.sweep == sweep and self.derivative is False:
            self.log.debug("sweep %d already set",sweep)
            return
        #self.log.debug("loading sweep %d (Ch%d)",sweep,channel)
        self.channels=self.ABFblock.segments[sweep].size["analogsignals"]
        if self.channels>1:
            self.log.error("multichannel not yet supported") #TODO
        self.trace = self.ABFblock.segments[sweep].analogsignals[channel]
        self.sweep=sweep # currently selected sweep
        self.channel=channel # currently selected channel
        
        # sweep information
        self.rate = int(self.trace.sampling_rate) # Hz
        self.period = float(1/self.rate) # seconds (inverse of sample rate)
        self.pointsPerSec = int(self.rate) # for easy access
        self.pointsPerMs = int(self.rate/1000.0) # for easy access
        self.sweepInterval = self.trace.duration.magnitude # sweep interval (seconds)
        self.sweepLength = self.trace.t_stop-self.trace.t_start # in seconds
        self.length = self.sweepLength*self.sweeps # length (sec) of total recording
        self.lengthMinutes = self.length # length (minutes) of total recording
        if str(self.trace.dimensionality) == 'pA':
            self.units,self.units2="pA","clamp current (pA)"     
            self.unitsD,self.unitsD2="pA/ms","current velocity (pA/ms)"       
        elif str(self.trace.dimensionality) == 'mV':
            self.units,self.units2="mV","membrane potential (mV)"
            self.unitsD,self.unitsD2="V/s","potential velocity (V/s)"
        else:
            self.units,self.units2="?","unknown units"
            self.unitsD,self.unitsD2="?","unknown units"
                
        # sweep data        
        self.sweepY = self.trace.magnitude # sweep data (mV or pA)
        self.sweepT = self.trace.times.magnitude # actual sweep time (sec)
        self.sweepStart = self.trace.t_start # time start of sweep (sec)
        self.sweepX2 = self.sweepT-self.trace.t_start.magnitude # sweeps overlap
        self.sweepX = self.sweepX2+sweep*self.sweepInterval # assume no gaps
        if self.derivative:
            self.log.debug("taking derivative")
            self.sweepD=np.diff(self.sweepY) # take derivative
            self.sweepD=np.insert(self.sweepD,0,self.sweepD[0]) # add a point
            self.sweepD/=(self.period*1000) # correct for sample rate
        else:
            self.sweepD=[0] # derivative is forced to be empty
        
    def comments_load(self):
        """read the header and populate self with information about comments"""
        self.comment_times,self.comment_sweeps,self.comment_tags=[],[],[]
        self.comments=0 # will be >0 if comments exist
        self.comment_text=""
        self.comment_tags = list(self.ABFblock.segments[0].eventarrays[0].annotations['comments'])
        self.comment_times = list(self.ABFblock.segments[0].eventarrays[0].times/self.trace.itemsize)
        self.comment_sweeps = list(self.comment_times)
        for i in range(len(self.comment_tags)):
            self.comment_tags[i]=self.comment_tags[i].decode("utf-8")
            self.comment_sweeps[i]=int(self.comment_times[i]/self.sweepInterval)
            self.comments+=1
            msg="sweep %d (%s) %s"%(self.comment_sweeps[i],self.comment_times[i],self.comment_tags[i])
            self.log.debug("COMMENT: %s",msg)
            self.comment_text+=msg+"\n"
        
    ### advanced data access
    
    def average(self,t1=0,t2=None,setsweep=False):
        """return the average of part of the current sweep."""
        if setsweep:
            self.setsweep(setsweep)
        if t2 is None:
            t2=self.sweepLength
        return np.average(self.sweepY[t1*self.pointsPerSec:t2*self.pointsPerSec])
        
    def averageSweep(self,sweepFirst=0,sweepLast=None):
        """
        Return a sweep which is the average of multiple sweeps.
        For now, standard deviation is lost.
        """
        if sweepLast is None:
            sweepLast=self.sweeps-1
        nSweeps=sweepLast-sweepFirst+1
        runningSum=np.zeros(len(self.sweepY))
        for sweep in np.arange(nSweeps)+sweepFirst:
            self.setsweep(sweep)
            runningSum+=self.sweepY
        average=runningSum/nSweeps
        #TODO: standard deviation?
        return average
            
                
                
            
            
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
        webinspect.launch(self.ABFblock.segments[0].eventarrays[0],'self.ABFblock.segments[0].eventarrays[0]')
        webinspect.launch(self.ABFblock.segments[5].analogsignals[0],'self.ABFblock.segments[5].analogsignals[0]')
        webinspect.launch(self.ABFblock.segments[5],'self.ABFblock.segments[5]')
        webinspect.launch(self.ABFblock,'self.ABFblock')
        webinspect.launch(self.ABFreader,'self.ABFreader')
        headerHTML(self.header,self.outPre+"_header.html")
    

if __name__=="__main__":
    print("#"*40+"\nRUNNING DEMO SCRIPT\n"+"#"*40)
    #abfFile=r"C:\Users\scott\Documents\important\2016-07-01 newprotos\16701009.abf"
    abfFile=r"C:\Users\scott\Documents\important\abfs\16o14022.abf"
    abf=ABF(abfFile,loglevel=logging.INFO) # initiate the ABF access class
    abf.derivative=True # tell it to use the first derivative
    for sweep in range(abf.sweeps): # for each sweep in the ABF
        abf.setsweep(sweep) # set that sweep
        print("sweep %d minimum: %.02f %s"%(abf.sweep,min(abf.sweepD),abf.unitsD))