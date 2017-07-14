import sys
sys.path.append("../../../")
import swhlab
import matplotlib.pyplot as plt
import numpy as np

def drawPhasePlot(abf,m1=0,m2=None):
    """
    Given an ABF object (SWHLab), draw its phase plot of the current sweep.
    m1 and m2 are optional marks (in seconds) for plotting only a range of data.
    Assume a matplotlib figure is already open and just draw on top if it.
    """

    if not m2:
        m2 = abf.sweepLength

    cm = plt.get_cmap('CMRmap')
    #cm = plt.get_cmap('CMRmap_r')
    #cm = plt.get_cmap('spectral')
    #cm = plt.get_cmap('winter')

    # prepare Xs, Ys, and dYs
    Y = abf.sweepY
    Y = Y[int(abf.pointsPerSec*m1):int(abf.pointsPerSec*m2)]
    dY = (Y[1:]-Y[:-1])*abf.rate/1000.0 # mV/ms
    dY = np.append(dY,dY[-1])
    Xs = np.arange(len(dY))/abf.pointsPerSec
    Xs = Xs + Xs[-1]*abf.sweep

    # plot the voltage
    plt.subplot(131)
    plt.grid(alpha=.5)
    plt.plot(Xs,Y,lw=.5,color=cm(abf.sweep/abf.sweeps))
    plt.title("membrane voltage")
    plt.ylabel("V (mV)")
    plt.xlabel("time (sec)")
    plt.margins(0,.1)

    # plot the first derivative of the voltage
    plt.subplot(132)
    plt.grid(alpha=.5)
    plt.plot(Xs,dY,lw=.5,color=cm(abf.sweep/abf.sweeps))
    plt.title("voltage velocity")
    plt.ylabel("dV (mV/ms)")
    plt.xlabel("time (sec)")
    plt.margins(0,.1)

    # make the phase plot
    plt.subplot(133)
    plt.grid(alpha=.5)
    plt.plot(Y,dY,alpha=.5,lw=.5,color=cm(abf.sweep/abf.sweeps))
    plt.title("phase plot")
    plt.ylabel("dV (mV/ms)")
    plt.xlabel("V (mV)")
    plt.margins(.1,.1)

    # tighten up the figure
    plt.tight_layout()




if __name__=="__main__":
    #abf=swhlab.ABF(R"X:\Data\SCOTT\2017-07-13 OXT-Tom OneOff\17713015.abf")
    abf=swhlab.ABF(R"X:\Data\SCOTT\2017-07-13 OXT-Tom OneOff\17713013.abf")

    plt.figure(figsize=(12,4))
    for sweep in abf.setsweeps():
        #if sweep<abf.sweeps-1: continue
        print("plotting sweep",sweep,'...')
        plt.set_cmap('winter')
        drawPhasePlot(abf)
    plt.savefig("phase_%s.png"%abf.ID,dpi=300)
    plt.show()

    plt.close('all')
    print("DONE")