import os
import swhlab
import matplotlib.pyplot as plt

if __name__=="__main__":
    abfPath=r"X:\Data\2P01\2016\2016-09-01 PIR TGOT"
    abf1=swhlab.ABF(os.path.join(abfPath,"16d14010.abf"))
    abf2=swhlab.ABF(os.path.join(abfPath,"16d14011.abf"))
    I1,I2=abf1.pointsPerSec*.5,abf1.sweepLength
    abf1.kernel=abf1.kernel_gaussian(50,True)
    abf2.kernel=abf2.kernel_gaussian(50,True)
    plt.figure(figsize=(10,3))
    
    for i in range(5,10):
        abf1.setsweep(abf1.sweeps-i)
        abf2.setsweep(i)
        Xoffset=abf1.sweepLength*i
        Y1=abf1.sweepYfiltered()[I1:]
        Y2=abf2.sweepYfiltered()[I1:]
        Y1=Y1-Y1[0]
        Y2=Y2-Y2[0]
        plt.plot(abf1.sweepX2[I1:]+.1*i,Y1+30*i,alpha=.5,color='b')
        plt.plot(abf2.sweepX2[I1:]+1.5+.1*i,Y2+30*i,alpha=.5,color='g')
    plt.margins()
    plt.title("5 sweeps at -70 vs -50")
    plt.show()
    
    print("DONE")