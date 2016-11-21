"""
Things related to generation of custom stimulus protocols (ATF format).
"""

import os
import sys
import pylab
import numpy as np
import time

import swhlab
import swhlab.core.common as cm

atf_header="""
ATF	1.0
8\t2
"AcquisitionMode=Episodic Stimulation"
"SyncTimeUnits=20"
"SweepStartTimesMS=0.000"
"SignalsExported=IN 0"
"Signals="	"IN 0"
"Time (s)"	"Trace #1"
""".strip()

def atf_empty(lengthSec=5,rate=20000):
    data=np.empty((rate*lengthSec,2))
    data[:,0]=np.arange(len(data))/rate
    return data

def atf_sine(lengthSec=5,rate=20000):
    data=np.empty((rate*lengthSec,2))
    data[:,0]=np.arange(len(data))/rate
    data[:,1]=np.sin((data[:,0])*np.pi*2) #1hz sine wave
    return data

def atf_ipsc():
    data=atf_sine()
    pylab.plot(data[:,0],data[:,1])
    pylab.show()
    fname="%d.atf"%time.time()
    np.savetxt(fname,data,fmt="%.6f",header=atf_header,comments='',delimiter='\t')

if __name__=="__main__":
    abf=swhlab.ABF('../abfs/group/16701010.abf')
    print("DONE")