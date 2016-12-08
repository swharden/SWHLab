import sys
sys.path.insert(0,"../")
import swhlab
import numpy as np
np.set_printoptions(precision=3)

abf=swhlab.ABF(R"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d07027.abf")
print(abf.sweeps())