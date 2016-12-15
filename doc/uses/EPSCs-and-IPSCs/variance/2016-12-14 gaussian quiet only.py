import os
import swhlab
import matplotlib.pyplot as plt
import numpy as np
import pickle

def variationPerChunk(data,chunkSize=None):
    if chunkSize is None:
        chunkSize=int(len(data)/100)
    chunkSize=int(chunkSize)
    nChunks=int(len(data)/chunkSize)
    chunks=np.reshape(data[:nChunks*chunkSize],(chunkSize,nChunks))
    return np.var(chunks,axis=1)

if __name__=="__main__":
#    abfPath=r"X:\Data\2P01\2016\2016-09-01 PIR TGOT"
#    abfFile=os.path.join(abfPath,"16d07022.abf")
#    abf=swhlab.ABF(abfFile)
#    abf.setsweep(200)
#    data=abf.sweepY[10000:]
#    np.save("sweepdata.npy",data)

    Y=np.load("sweepdata.npy")
    X=np.arange(len(Y))/20000
    
    variances=variationPerChunk(Y)
    varianceCutoff=np.percentile(variances,5) # quietest 5%
    
    plt.figure(figsize=(10,3))
    plt.plot(X,Y)
    
    for i,variance in enumerate(variances):
        if variance<=varianceCutoff:
            plt.axvspan(i*100/20000,
                        (i+1)*100/20000,
                        color='r',alpha=.1)
    
    plt.margins(0,.5)
    plt.tight_layout()
    plt.show()
    
    print("DONE")