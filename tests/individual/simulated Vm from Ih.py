import swhlab
import matplotlib.pyplot as plt
import numpy as np

if __name__=="__main__":

    abfFname=r'X:\Data\2P01\2016\2016-09-01 PIR TGOT\16831057.abf'
    abf=swhlab.ABF(abfFname) # now it's a swhlab ABF object
    abf.setsweep(267) # set the sweep

    # calculate membrane resistance
    baseline=abf.average(.5)/(10**12) # A
    baselineMT=abf.average(.05,.15)/(10**12) # A
    dV=10/(10**3) # 10 mV
    dI=abs(baselineMT-baseline) # A
    Rm=(dV/dI) # R=E/I MOhm

    # cut off the first half-second (which has memtest)
    Y=abf.sweepY[int(abf.pointsPerSec*.5):]/(10**12) #A
    X=abf.sweepX2[int(abf.pointsPerSec*.5):]

    # create a new figure
    plt.figure(figsize=(10,8))

    # design the top plot
    plt.subplot(311)
    plt.grid()
    plt.title("voltage clamp (Rm = %.02f MOhm)"%(Rm/(10**6)))
    plt.ylabel("current (pA)")
    plt.plot(X,Y*(10**12),color='r',alpha=.8) # plot the data
    plt.axhline(baseline*(10**12),color='k',lw=3,ls='--',alpha=.5)
    plt.margins(0,.1)

    # design the bottom plot
    plt.subplot(312)
    plt.grid()
    plt.title("simulated current clamp")
    plt.ylabel("predicted change in Vm")

    #Rm=500*(10**6)
    traces=[]
    for testRM in [200,225,500,525]:
        testRM=testRM*10**6
        Y2=Y-baseline
        Y2=Y*np.ones(len(Y2))*testRM
        Y2=np.average(Y2)-Y2
        plt.plot(X,np.cumsum(Y2),alpha=.8,
                 label="Rm=%d"%(testRM/(10**6)),lw=2)
        traces.append(np.cumsum(Y2))
    plt.margins(0,.1)
    plt.legend()

    plt.subplot(313)
    plt.title("DIFFERENCE")
    plt.plot(X,traces[1]-traces[0],label="200-225")
    plt.plot(X,traces[3]-traces[2],label="500-525")
    plt.legend()

    # save, show, and close
    #plt.savefig(r"demo.jpg",dpi=100)
    plt.show()
    plt.close('all')
    print("DONE")