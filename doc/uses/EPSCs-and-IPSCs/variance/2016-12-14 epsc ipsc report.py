import os
import swhlab
import matplotlib.pyplot as plt
import numpy as np
import pickle

if __name__=="__main__":
    abfPath=r"X:\Data\2P01\2016\2016-09-01 PIR TGOT"
    abfFile=os.path.join(abfPath,"16d14060.abf")
    abf=swhlab.ABF(abfFile)
    Xs=np.arange(abf.sweeps)*abf.sweepLength
    
    # figure out if we should calculate or load phasic data
    phasicFname=abf.filename+".phasic.npy"
    if not os.path.exists(phasicFname):
        data=np.empty((abf.sweeps,3))
        for sweep in abf.setsweeps():
            print("analyzing sweep %d of %d"%(sweep,abf.sweeps))
            data[sweep]=abf.phasic(returnSeparated=True)
        np.save(phasicFname,data)
    else:
        data = np.load(phasicFname)
        
    # plot the result with comments
    plt.figure(figsize=(5,5))
    
    plt.subplot(211)
    plt.plot(Xs,data[:,2],'.',color='k',alpha=.1)
    plt.plot(Xs,swhlab.common.lowpass(data[:,2],40), '-',color='k',alpha=.5,lw=2)
    for t in abf.comment_times:
        plt.axvline(t,color='r',ls='--',alpha=.5)
    plt.axhline(0,color='r',ls='--',alpha=.5)
    plt.margins(0,.1)
    plt.tight_layout()
    plt.ylabel("net excitation (pA)")
    plt.title(abf.ID)
    
    plt.subplot(212)
    plt.plot(Xs,data[:,0],'.',color='r',alpha=.1)
    plt.plot(Xs,swhlab.common.lowpass(data[:,0],40), '-',color='r',alpha=.5,lw=2)
    plt.plot(Xs,data[:,1],'.',color='b',alpha=.1)
    plt.plot(Xs,swhlab.common.lowpass(data[:,1],40), '-',color='b',alpha=.5,lw=2)
    for t in abf.comment_times:
        plt.axvline(t,color='r',ls='--',alpha=.5)
    plt.margins(0,.1)
    plt.tight_layout()
    plt.ylabel("separated excitation (pA)")
    plt.xlabel("experiment duration (sec)")    
    
    plt.savefig(abf.ID+".png")
    plt.show()
    
    print("DONE")