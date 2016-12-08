"""
MOST OF THIS CODE IS NOT USED
ITS COPY/PASTED AND LEFT HERE FOR CONVENIENCE
"""

import os
import sys

# in case our module isn't installed (running from this folder)
if not os.path.abspath('../../../') in sys.path:
    sys.path.append('../../../') # helps spyder get docs

import swhlab
import matplotlib.pyplot as plt
import numpy as np

def analyzeSweep(abf):
    plt.figure(figsize=(10,5))
    plt.plot(abf.sweepX2,abf.sweepYfiltered())
    plt.show()
    return

def showKernel(abf):
    plt.figure()
    plt.plot(abf.kernel)
    plt.show()
    plt.close('all')
    
if __name__=="__main__":
    abfFile=R"C:\Users\scott\Documents\important\demodata\abfs\16d07022.abf"
    abf=swhlab.ABF(abfFile)
    abf.kernel=abf.kernel_gaussian(sizeMS=100)
    showKernel(abf)
    abf.setsweep(200)
    analyzeSweep(abf)
    print("DONE")
