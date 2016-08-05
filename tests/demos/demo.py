import os
import swhlab

if __name__=="__main__":
    SEEKPATH=os.path.dirname(swhlab.LOCALPATH)+"/abfs/"
    print("Looking for ABFs in:",SEEKPATH)

    abfs=[]
    for root, dirs, files in os.walk(SEEKPATH):
        for file in files:
            fname=os.path.abspath(root+'/'+file)
            if fname.endswith('.abf'):
                abfs.append(fname)
    if len(abfs):
        print("found %d ABFs:"%len(abfs))
        print("showing the first one:",os.path.basename(abfs[0]))
        abf=swhlab.ABF(abfs[0])
        swhlab.plot.sweep(abf,'all')
        swhlab.plot.show(abf)
    else:
        print("I don't seen any ABFs anywhere! Put some in.")