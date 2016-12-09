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
import swhlab.common as cm
import matplotlib.pyplot as plt
import numpy as np

import warnings # suppress VisibleDeprecationWarning warning
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)

if __name__=="__main__":
    #abfFile=R"C:\Users\scott\Documents\important\demodata\abfs\16d07022.abf"
    abfFile=R"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d07022.abf"
    abf=swhlab.ABF(abfFile)
    for sweep in abf.setsweeps():
        print("Sweep",sweep,"phasic current is",abf.phasicNet())


#Sweep 0 phasic current is -7.84370105278
#Sweep 1 phasic current is -3.92867583759
#Sweep 2 phasic current is -4.68253583272
#Sweep 3 phasic current is -7.2651550911
#Sweep 4 phasic current is -5.6990834645
#Sweep 5 phasic current is -3.04249607924
#Sweep 6 phasic current is -6.49318707287
#Sweep 7 phasic current is -4.33582645295
#Sweep 8 phasic current is -7.28951428466
#Sweep 9 phasic current is -6.03569290767
#Sweep 10 phasic current is -4.76673467752
#Sweep 11 phasic current is -6.04359593419
#Sweep 12 phasic current is -6.49995283789
#Sweep 13 phasic current is -1.75327048562
#Sweep 14 phasic current is -4.76436320886
#Sweep 15 phasic current is -3.55029773378
#Sweep 16 phasic current is -3.11413632698
#Sweep 17 phasic current is -8.1363760241