# script to stress test the X-Drive
import os
import time

path_big_file=R"X:\Data\SCOTT\2017-05-10 GCaMP6f\GCaMP6f PFC GABA cre\2017-05-10-23 misc\2017-05-11 cell3_annotated.tif"
path_path_to_walk=R"X:\Data\DIC2\2014"

def timeIt(timeStart=None):
    if timeStart:
        return time.time()-timeStart
    return time.time()

def test_listing(path,runs=5):
    print("walking the entire tree of:",path)
    times=[]
    for run in range(runs):
        t1=timeIt()
        abfs,folders=0,0
        for dirpath, subdirs, files in os.walk(path):
            folders+=1
            for x in files:
                if x.endswith(".abf"):
                    abfs+=1
        times.append(timeIt(t1))
        print("(%d/%d) scanned %d folders in %.03f seconds"%(run+1,runs,folders,times[-1]))
    print("Average time for %d runs: %.03f seconds"%(runs,sum(times)/len(times)))

def test_copying(path,runs=5):
    print("copying a HUGE file:",path)
    times=[]
    for run in range(runs):
        t1=timeIt()
        os.system('echo f | xcopy /f /y "%s" "%s"'%(path, './test.data'))
        times.append(timeIt(t1))
        mbs=os.stat('./test.data').st_size/times[-1]/1024/1024
        os.remove('./test.data')
        print("(%d/%d) copy took %.03f seconds (%.03f MB/s)"%(run+1,runs,times[-1],mbs))
    print("Average time for %d runs: %.03f seconds"%(runs,sum(times)/len(times)))
    return

if __name__=="__main__":
    test_listing(path_path_to_walk)
    test_copying(path_big_file)
<<<<<<< HEAD
    print("DONE")
=======
    print("DONE")
>>>>>>> origin/master
