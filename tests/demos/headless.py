import imp
import os
import glob

import swhlab

def getABFs():
    os.chdir(os.path.dirname(swhlab.LOCALPATH)+"/abfs/")
    print("I see %d ABFs"%len(glob.glob("*.abf")))

if __name__=="__main__":
    getABFs()
    abf=swhlab.ABF(glob.glob("*.abf")[0])
    swhlab.plot.sweep(abf,-1)
    swhlab.plot.show(abf)
    print("DONE")
