import sys
sys.path.insert(0,'../') # force us to import ../swhlab/ module
import swhlab
import numpy as np
import matplotlib.pyplot as plt

if __name__=='__main__':
    abf=swhlab.ABF(R"X:\Data\2P01\10.7.0.3_modelCell\17217003.abf")
    plt.plot(abf.sweepX2,abf.sweepY)
    plt.show()

    print(steps)