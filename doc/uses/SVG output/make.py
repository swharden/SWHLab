import sys
sys.path.append('../../../')
import swhlab
import matplotlib.pyplot as plt
import time
import numpy as np

if __name__=='__main__':
    fname=r"X:\Data\2P01\2015\2015-12-29 TRHIN seek fast\16129025.abf"
    abf=swhlab.ABF(fname)
    plt.figure(figsize=(20,20))
    data=[]
    for i in range(10):
        abf.setsweep(i)
        plt.plot(abf.sweepY+100*i,color='b')
    plt.tight_layout()
    plt.gca().yaxis.set_visible(False)
    plt.gca().xaxis.set_visible(False)
    plt.margins(0)
    for spine in plt.gca().spines.values():
        spine.set_visible(False)
    plt.savefig("ap4.svg")
    plt.show()
    plt.close("all")
    print("DONE")