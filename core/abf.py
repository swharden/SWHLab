"""
Core SWHLab4 ABF handling class.

The ABF class is for:
    - reading ABF data
    - determining ABF information (i.e., number of channels from header)
    - retrieval of recorded data
    - generation of command protocol
    - baseline subtraction #TODO:
    - decimation
    - saving things to disk (data, memtests, images)

The ABF class is *NOT* for:
    - data analysis
    - plotting of any kind
    - event detection
    - membrane tests
    - gaussian filtering

For things like event detection and membrane tests, do the analysis externally
and load the findings (i.e., MTs[] and APs[]) into the class.
"""

#TODO: remove all instances of outpath and replace with outpre

import os
import sys
import copy
import neo #install this from the github
import numpy as np
import pprint
import pylab
import traceback
import pickle
import glob
import time

import swhlab
import swhlab.core.common as cm

class ABF():
    """Limit functionality strictly to:
    Loading ABFs, saving stats about ABFs
    Calling sweeps, averages, or ranges of cut sweeps
    *NO* analysis, event detection, or graphing
    Methods here only modify dataX and dataY (together, by sweep)
    maybe basic event detecton.
    """

    def __init__(self,ABFfname=None,debugLevel=1,saveInfo=True):
        """SWHLab4 ABF class.
        Basic usage:
            1.) call this with an ABF filename
            2.) select a sweet with setSweep()
            3.) reference data by ABF.dataX and ABF.dataY
        """
        self.valid=False
        if ABFfname is None:
            return #dummy class
        if not type(ABFfname) is str:
            raise Exception('ABF() requires astring (or None) for file name')
        if not ABFfname.lower().endswith(".abf"):
            raise Exception('invalid ABF filename: [%s]'%ABFfname)
        ABFfname=os.path.abspath(ABFfname)
        if not os.path.exists(ABFfname):
            raise Exception('ABF file does not exist:\nGiven path: [%s]'%ABFfname)

        if saveInfo:
            print(" >> ABF",os.path.basename(ABFfname))
        self.fname = os.path.abspath(ABFfname)
        self.ID = os.path.basename(self.fname).replace(".abf","")
        self.outpath = os.path.join(os.path.split(self.fname)[0],"swhlab4/")
        self.outpre = os.path.abspath(self.outpath+"/"+self.ID+"_") #only save data and images with this prefix!!!
        self.reader = neo.io.AxonIO(ABFfname)
        self.valid=False
        try:
            self.header = self.reader.read_header()
            self.block = self.reader.read_block(lazy=False, cascade=True) #TODO: what's cascade?
        except:
            print("can't read the ABF! Is this a waveform?")
            return
        self.valid=True

        # PERMANENT ABF INFO
        startDay=time.strptime(str(self.header["uFileStartDate"]), '%Y%m%d')
        self.timestamp=time.mktime(startDay)+self.header["uFileStartTimeMS"]/1000.0 #time of abf creation in epoch units
        self.units = self.header['listADCInfo'][0]['ADCChUnits'].decode('utf8') #pA or mV
        self.unitsCommand = self.header['listDACInfo'][0]['DACChUnits'].decode('utf8') #pA or mV
        self.holding = self.header['listDACInfo'][0]['fDACHoldingLevel'] #clamp current or voltage
        self.rate = int(1000000/self.header['protocol']['fADCSequenceInterval']) #seconds
        self.timebase = self.header['protocol']['fSynchTimeUnit'] #time unit
        self.nADC = self.header['sections']['ADCSection']['llNumEntries'] #channels
        self.sweeps = self.header['lActualEpisodes']
        self.gapFree=(self.sweeps==0)
        if self.gapFree:
            self.sweeps=1
        self.sweepSize = self.header['protocol']['lNumSamplesPerEpisode']/self.nADC
        self.sweepLength = self.sweepSize/self.rate #TODO: scour code, make sure this isn't exclusively used.
        self.sweepInterval = self.header['protocol']['fEpisodeStartToStart'] # sweep to sweep start (seconds)
        if self.sweepInterval==0:
            self.sweepInterval=self.sweepLength

        # FIGURE OUT COMMENT STUFF
        self.commentTags = self.block.segments[0].eventarrays[0].annotations['comments']
        self.commentTags = [x.decode('utf8') for x in self.commentTags]
        self.commentTimes = np.array(self.block.segments[0].eventarrays[0].times)/self.nADC
        self.commentTimes = self.commentTimes/4 #TODO: WHY IS THIS?! It's not an IC vs VC thing. Sometimes it's /5.
        self.commentSweeps = np.array(self.commentTimes/self.sweepInterval,dtype=int)

        # SETTABLE SWEEP TRANSFORMATIONS
        self.baseline=[None,None] #[1,2] for seconds 1-2 baseline subtraction
        self.decimateMethod=None #avg, max, min, or fast (or None)
        self.decimateBy=100 # only if decimateMethod is used

        ### PROTOCOL ALIGNMENT ###
        #self.offsetX = int(self.nSam*15625/10**6) #what is magic here? THIS WORKS!!!!! Relates to fSynchTimeUnit?
        self.offsetX = int(self.sweepSize/64) #what is magic here? 64-bit data points? #1,000,000/64 = 15625 btw
        self.offsetY = 0 #in measurement units

        # VOLATILE SWEEP INFO
        self.dataY = None #sweep value
        self.dataX = None #seconds by sweep
        self.dataStart = None #ABF start time of sweep data in seconds
        self.currentSweep = None #number starting at 0
        self.channel = 0 #default at 0, but can be selected

        # TIDY-UPS AFTER LOADING AN ABF
        self.generate_colormap()
        self.generate_protocol()
        self.protoComment=cm.determineProtocol(self.fname)
        if saveInfo:
            self.saveThing(self.abfinfo(returnDict=True),'info',overwrite=False)

    ### FILE INFORMATION

    def abfinfo(self,printToo=False,returnDict=False):
        """show basic info about ABF class variables."""
        info="\n### ABF INFO ###\n"
        d={}
        for thingName in sorted(dir(self)):
            if thingName in ['cm','evIs','colormap','dataX','dataY',
                             'protoX','protoY']:
                continue
            if "_" in thingName:
                continue
            thing=getattr(self,thingName)
            if type(thing) is list and len(thing)>5:
                continue
            thingType=str(type(thing)).split("'")[1]
            if "method" in thingType or "neo." in thingType:
                continue
            if thingName in ["header","MT"]:
                continue
            info+="%s <%s> %s\n"%(thingName,thingType,thing)
            d[thingName]=thing
        if printToo:
            print()
            for line in info.split("\n"):
                if len(line)<3:
                    continue
                print("   ",line)
            print()
        if returnDict:
            return d
        return info

    def headerHTML(self,fname=None):
        """read the ABF header and save it HTML formatted."""
        if fname is None:
            fname = self.fname.replace(".abf","_header.html")
        html="<html><body><code>"
        html+="<h2>abfinfo() for %s.abf</h2>"%self.ID
        html+=self.abfinfo().replace("<","&lt;").replace(">","&gt;").replace("\n","<br>")
        html+="<h2>Header for %s.abf</h2>"%self.ID
        html+=pprint.pformat(self.header, indent=1)
        html=html.replace("\n",'<br>').replace(" ","&nbsp;")
        html=html.replace(r"\x00","")
        html+="</code></body></html>"
        print("WRITING HEADER TO:")
        print(fname)
        f=open(fname,'w')
        f.write(html)
        f.close()

    def generate_colormap(self,colormap=None,reverse=False):
        """use 1 colormap for the whole abf. You can change it!."""
        if colormap is None:
            colormap = pylab.cm.Dark2
        self.cm=colormap
        self.colormap=[]
        for i in range(self.sweeps): #TODO: make this the only colormap
            self.colormap.append(colormap(i/self.sweeps))
        if reverse:
            self.colormap.reverse()

    ### SWEEP

    def setSweep(self,sweep=0,force=False):
        """Load X/Y data for a particular sweep.
        determines if forced reload is needed, updates currentSweep,
        regenerates dataX (if not None),decimates,returns X/Y.
        Note that setSweep() takes 0.17ms to complete, so go for it!
        """
        if sweep is None or sweep is False:
            sweep=0
        if sweep<0:
            sweep=self.sweeps-sweep #-1 means last sweep
            if sweep<0: #still!
                sweep=0 #first sweep
        if sweep>(self.sweeps-1):
            print(" !! there aren't %d sweeps. Reverting to last (%d) sweep."%(sweep,self.sweeps-1))
            sweep=self.sweeps-1
        sweep=int(sweep)
        try:
            if self.currentSweep==sweep and force==False:
                return
            self.currentSweep=sweep
            self.dataY = self.block.segments[sweep].analogsignals[self.channel]
            self.dataY = np.array(self.dataY)

            B1,B2=self.baseline
            if B1==None:
                B1=0
            else:
                B1=B1*self.rate
            if B2==None:
                B2==self.sweepSize
            else:
                B2=B2*self.rate

                self.dataY-=np.average(self.dataY[self.baseline[0]*self.rate:self.baseline[1]*self.rate])
            self.sweep_genXs()
            self.sweep_decimate()
            self.generate_protocol(sweep=sweep)
            self.dataStart = self.sweepInterval*self.currentSweep
        except Exception:
            print("#"*400,"\n",traceback.format_exc(),'\n',"#"*400)
        return self.dataX,self.dataY

    def sweep_genXs(self):
        """generate sweepX (in seconds) to match sweepY"""
        if self.decimateMethod:
            self.dataX=np.arange(len(self.dataY))/self.rate
            self.dataX*=self.decimateBy
            return
        if self.dataX is None or len(self.dataX)!=len(self.dataY):
            self.dataX=np.arange(len(self.dataY))/self.rate

    def sweep_decimate(self):
        """
        decimate data using one of the following methods:
            'avg','max','min','fast'
        They're self explainatory. 'fast' just plucks the n'th data point.
        """
        if len(self.dataY)<self.decimateBy:
            return
        if self.decimateMethod:
            points = int(len(self.dataY)/self.decimateBy)
            self.dataY=self.dataY[:points*self.decimateBy]
            self.dataY = np.reshape(self.dataY,(points,self.decimateBy))
            if self.decimateMethod=='avg':
                self.dataY = np.average(self.dataY,1)
            elif self.decimateMethod=='max':
                self.dataY = np.max(self.dataY,1)
            elif self.decimateMethod=='min':
                self.dataY = np.min(self.dataY,1)
            elif self.decimateMethod=='fast':
                self.dataY = self.dataY[:,0]
            else:
                print("!!! METHOD NOT IMPLIMENTED YET!!!",self.decimateMethod)
            self.dataX = np.arange(len(self.dataY))/self.rate*self.decimateBy

    def get_data_around(self,timePoints,thisSweep=False,padding=0.02,msDeriv=0):
        """
        return self.dataY around a time point. All units are seconds.
        if thisSweep==False, the time point is considered to be experiment time
            and an appropriate sweep may be selected. i.e., with 10 second
            sweeps and timePint=35, will select the 5s mark of the third sweep
        """
        if not np.array(timePoints).shape:
            timePoints=[float(timePoints)]
        data=None
        for timePoint in timePoints:
            if thisSweep:
                sweep=self.currentSweep
            else:
                sweep=int(timePoint/self.sweepInterval)
                timePoint=timePoint-sweep*self.sweepInterval
            self.setSweep(sweep)
            if msDeriv:
                dx=int(msDeriv*self.rate/1000) #points per ms
                newData=(self.dataY[dx:]-self.dataY[:-dx])*self.rate/1000/dx
            else:
                newData=self.dataY
            padPoints=int(padding*self.rate)
            pad=np.empty(padPoints)*np.nan
            Ic=timePoint*self.rate #center point (I)
            newData=np.concatenate((pad,pad,newData,pad,pad))
            Ic+=padPoints*2
            newData=newData[Ic-padPoints:Ic+padPoints]
            newData=newData[:int(padPoints*2)] #TODO: omg so much trouble with this!
            if data is None:
                data=[newData]
            else:
                data=np.vstack((data,newData))#TODO: omg so much trouble with this!
        return data

    ### PROTOCOL

    def generate_protocol(self,sweep=None):
        """
        Create (x,y) points necessary to graph protocol for the current sweep.
        """
        #TODO: make a line protocol that's plottable
        if sweep is None:
            sweep = self.currentSweep
        if sweep is None:
            sweep = 0
        if not self.channel in self.header['dictEpochInfoPerDAC'].keys():
            self.protoX=[0,self.sweepSize]
            self.protoY=[self.holding,self.holding]
            self.protoSeqX=self.protoX
            self.protoSeqY=self.protoY
            return
        proto=self.header['dictEpochInfoPerDAC'][self.channel]
        self.protoX=[] #plottable Xs
        self.protoY=[] #plottable Ys
        self.protoX.append(0)
        self.protoY.append(self.holding)
        for step in proto:
            dX = proto[step]['lEpochInitDuration']
            Y = proto[step]['fEpochInitLevel']+proto[step]['fEpochLevelInc']*sweep
            self.protoX.append(self.protoX[-1])
            self.protoY.append(Y) #go to new Y
            self.protoX.append(self.protoX[-1]+dX) #take it to the new X
            self.protoY.append(Y) #update the new Y #TODO: fix for ramps

        if self.header['listDACInfo'][0]['nInterEpisodeLevel']: #nInterEpisodeLevel
            finalVal=self.protoY[-1] #last holding
        else:
            finalVal=self.holding #regular holding
        self.protoX.append(self.protoX[-1])
        self.protoY.append(finalVal)
        self.protoX.append(self.sweepSize)
        self.protoY.append(finalVal)

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

        self.protoX=np.array(self.protoX)
        self.protoY=np.array(self.protoY)

    def clampValues(self,timePoint=0):
        """
        return an array of command values at a time point (in sec).
        Useful for things like generating I/V curves.
        """
        Cs=np.zeros(self.sweeps)
        for i in range(self.sweeps):
            self.setSweep(i) #TODO: protocol only = True
            for j in range(len(self.protoSeqX)):
                if self.protoSeqX[j]<=timePoint*self.rate:
                    Cs[i]=self.protoSeqY[j]
        return Cs

    def guess_protocol(self):
        """
        This just generates a string to define the nature of the ABF.
        The ultimate goal is to use info about the abf to guess what to do with it.
            [vc/ic]-[steps/fixed]-[notag/drugs]-[2ch/1ch]
            This represents 2^4 (18) combinations, but is easily expanded.
        """
        clamp="ic"
        if self.units=="pA":
            clamp="vc"
        command="fixed"
        if self.sweeps>1:
            self.setSweep(0)
            P0=str(self.protoX)+str(self.protoY)
            self.setSweep(1)
            P1=str(self.protoX)+str(self.protoY)
            if not P0==P1:
                command="steps"
        tags="notag"
        if len(self.commentSweeps):
            tags="drugs"
        ch="1ch"
        if self.nADC>1:
            ch="2ch"
        guess="-".join([clamp,command,tags,ch])
        return guess

    ### AVERAGE MATH

    def average_sweep(self,T1=0,T2=None,sweeps=None,stdErr=False):
        """
        given an array of sweeps, return X,Y,Err average.
        This returns *SWEEPS* of data, not just 1 data point.
        """
        T1=T1*self.rate
        if T2 is None:
            T2 = self.sweepSize-1
        else:
            T2 = T2*self.rate
        if sweeps is None:
            sweeps = range(self.sweeps)
        Ys=np.empty((len(sweeps),(T2-T1)))
        for i in range(len(sweeps)):
            self.setSweep(sweeps[i])
            Ys[i]=self.dataY[T1:T2]
        Av = np.average(Ys,0)
        Es = np.std(Ys,0)
        Xs = self.dataX[T1:T2]
        if stdErr: #otherwise return stdev
            Es = Es/np.sqrt(len(sweeps))
        return Xs,Av,Es

    def average_data(self,ranges=[[None,None]],percentile=None):
        """
        given a list of ranges, return single point averages for every sweep.
        Units are in seconds. Expects something like:
            ranges=[[1,2],[4,5],[7,7.5]]
        None values will be replaced with maximum/minimum bounds.
        For baseline subtraction, make a range baseline then sub it youtself.
            returns datas[iSweep][iRange][AVorSD]
        if a percentile is given, return that percentile rather than average.
            percentile=50 is the median, but requires sorting, and is slower.
        """
        ranges=copy.deepcopy(ranges) #TODO: make this cleaner. Why needed?
        # clean up ranges, make them indexes
        for i in range(len(ranges)):
            if ranges[i][0] is None:
                ranges[i][0] = 0
            else:
                ranges[i][0] = int(ranges[i][0]*self.rate)
            if ranges[i][1] is None:
                ranges[i][1] = -1
            else:
                ranges[i][1] = int(ranges[i][1]*self.rate)

        # do the math
        datas=np.empty((self.sweeps,len(ranges),2)) #[sweep][range]=[Av,Er]
        for iSweep in range(self.sweeps):
            self.setSweep(iSweep)
            for iRange in range(len(ranges)):
                I1=ranges[iRange][0]
                I2=ranges[iRange][1]
                if percentile:
                    datas[iSweep][iRange][0]=np.percentile(self.dataY[I1:I2],percentile)
                else:
                    datas[iSweep][iRange][0]=np.average(self.dataY[I1:I2])
                datas[iSweep][iRange][1]=np.std(self.dataY[I1:I2])
        return datas

    ### FILTERING

    def filter_gaussian(self,sigmaMs=100,applyFiltered=False,applyBaseline=False):
        """RETURNS filtered trace. Desn't filter it in place."""
        if sigmaMs==0:
            return self.dataY
        filtered=cm.filter_gaussian(self.dataY,sigmaMs)
        if applyBaseline:
            self.dataY=self.dataY-filtered
        elif applyFiltered:
            self.dataY=filtered
        else:
            return filtered

    ### CUSTOM FILES
    # this seems like a weird thing to have here, but restricting filesystem
    # access to the ABF class ensures that only things with the abf prefix
    # will be written or destroyed.

    def saveThing(self,thing,fname,overwrite=True,ext=".pkl"):
        """save any object as /swhlab4/ID_[fname].pkl"""
        if not os.path.exists(os.path.dirname(self.outpre)):
            os.mkdir(os.path.dirname(self.outpre))
        if ext and not ext in fname:
            fname+=ext
        fname=self.outpre+fname
        if overwrite is False:
            if os.path.exists(fname):
                print(" o- not overwriting [%s]"%os.path.basename(fname))
                return
        time1=cm.timethis()
        pickle.dump(thing, open(fname,"wb"),pickle.HIGHEST_PROTOCOL)
        print(" <- saving [%s] %s (%.01f kB) took %.02f ms"%(\
              os.path.basename(fname),str(type(thing)),
              sys.getsizeof(pickle.dumps(thing, -1))/1e3,
              cm.timethis(time1)))

    def loadThing(self,fname,ext=".pkl"):
        """save any object from /swhlab4/ID_[fname].pkl"""
        if ext and not ext in fname:
            fname+=ext
        fname=self.outpre+fname
        time1=cm.timethis()
        thing = pickle.load(open(fname,"rb"))
        print(" -> loading [%s] (%.01f kB) took %.02f ms"%(\
              os.path.basename(fname),
              sys.getsizeof(pickle.dumps(thing, -1))/1e3,
              cm.timethis(time1)))
        return thing

    def deleteStuff(self,ext="*",spareInfo=True,spare=["_info.pkl"]):
        """delete /swhlab4/ID_*"""
        print(" -- deleting /swhlab4/"+ext)
        for fname in sorted(glob.glob(self.outpre+ext)):
            reallyDelete=True
            for item in spare:
                if item in fname:
                    reallyDelete=False
            if reallyDelete:
                os.remove(fname)

def test():
    fname=r"X:\Data\2P01\2016\2016-07-11 PIR TR IHC\16711054.abf"
    abf=ABF(fname)
    abf.headerHTML()
    abf.setSweep(-1)
    abf.abfinfo(True)
    pylab.plot(abf.dataX,abf.dataY)
    pylab.show()
    print("DONE")

#version_check_threaded() #check for new version whenever this is imported.
if __name__=="__main__":
    test()