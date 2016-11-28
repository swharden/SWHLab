import swhlab
import matplotlib.pyplot as plt
import numpy as np

if __name__=="__main__":

    # prepare an ABF file as the "abf" (swhlab) object
    abfFname=r'X:\Data\2P01\2016\2016-09-01 PIR TGOT\16831057.abf'
    abf=swhlab.ABF(abfFname)
    abf.setsweep(267)

    # cut off the first half-second (which has memtest)
    Y=abf.sweepY[int(abf.pointsPerSec*.5):]
    X=abf.sweepX2[int(abf.pointsPerSec*.5):]
    baseline=np.average(Y)

    # create a new figure
    plt.figure(figsize=(10,8))

    # design the top axis
    plt.subplot(211)
    plt.grid()
    plt.title("voltage clamp")
    plt.ylabel("current (pA)")
    plt.plot(X,Y,color='r',alpha=.8)
    plt.axhline(baseline,color='k',lw=3,ls='--',alpha=.5)
    plt.margins(0,.1)

    plt.subplot(212)
    plt.grid()
    plt.title("simulated current clamp")
    plt.ylabel("predicted change in Vm")
    iY=np.cumsum(baseline-Y)/1000 # integrate
    plt.plot(X,iY,color='b',alpha=.8)
    plt.margins(0,.1)

    plt.savefig(r"demo.png",dpi=100)
    plt.show()
    plt.close('all')
    print("DONE")