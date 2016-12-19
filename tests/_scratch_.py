import sys
sys.path.insert(0,'../') # force us to import ../swhlab/ module
import swhlab
import numpy as np

if __name__=='__main__':
    abf=swhlab.ABF(R"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d16025.abf")

    abf.setsweep(0)
    proto1=abf.protoY
    abf.setsweep(1)
    proto2=abf.protoY

    print(proto1[3])
    print(proto2[3])

    for i in range(len(proto1)):
        if proto1[i]!=proto2[i]:
            print("protocol steps.")
            steps=np.arange(len(proto1))
            steps=steps*(proto2[i]-proto1[i])+proto1[i]
            break
    else:
        print("protocol does not change.")
        steps=np.ones(len(proto1))
    print(steps)