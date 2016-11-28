import swhlab
import matplotlib.pyplot as plt
import numpy as np

if __name__=="__main__":

    abfFname=r'X:\Data\2P01\2016\2016-09-01 PIR TGOT\16831057.abf'
    abf=swhlab.ABF(abfFname) # now it's a swhlab ABF object
    abf.setsweep(267) # set the sweep

    # calculate membrane resistance
    baseline=abf.average(.5) # average current at -70mV
    baselineMT=abf.average(.05,.15) # average current at -80mV
    dV=10/(10**3) # 10 mV
    dI=abs(baselineMT-baseline)/(10**12) # pA
    Rm=(dV/dI)/(10**6) # R=E/I MOhm

    # cut off the first half-second (which has memtest)
    Y=abf.sweepY[int(abf.pointsPerSec*.5):]
    X=abf.sweepX2[int(abf.pointsPerSec*.5):]

    # create a new figure
    plt.figure(figsize=(10,8))

    # design the top plot
    plt.subplot(211)
    plt.grid()
    plt.title("voltage clamp (Rm = %.02f MOhm)"%Rm)
    plt.ylabel("current (pA)")
    plt.plot(X,Y,color='r',alpha=.8) # plot the data
    plt.axhline(baseline,color='k',lw=3,ls='--',alpha=.5)
    plt.margins(0,.1)

    # design the bottom plot
    plt.subplot(212)
    plt.grid()
    plt.title("simulated current clamp")
    plt.ylabel("predicted change in Vm")
    dV=np.cumsum(baseline-Y)/Rm # dV=dI/R
    plt.plot(X,dV,color='b',alpha=.8)
    plt.margins(0,.1)

    # save, show, and close
    plt.savefig(r"demo.jpg",dpi=100)
    plt.show()
    plt.close('all')