"""
The author is intended to run this..
"""

import os
import shutil
import glob
import subprocess
import sys

def newVersion():
    """increments version counter in swhlab/version.py"""
    version=None
    fname='../swhlab/version.py'
    with open(fname) as f:
        raw=f.read().split("\n")
        for i,line in enumerate(raw):
            if line.startswith("__counter__"):
                if version is None:
                    version = int(line.split("=")[1])
                raw[i]="__counter__=%d"%(version+1)
    with open(fname,'w') as f:
        f.write("\n".join(raw))
    print("upgraded from version %03d to %03d"%(version,version+1))

def cleanUp():
    for delThis in ['../swhlab.egg-info/','../tests/output']:
        if os.path.exists(delThis):
            shutil.rmtree(delThis)
    for fname in glob.glob("../dist/*.zip"):
        os.remove(fname)

def upload():    
    print("packaging and uploading...")
    cmd="cd ../ && python setup.py --quiet sdist upload"
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        print(line.decode('utf-8').strip())
    retval = p.wait()
    if retval:
        print("process returned value:",retval)
        input("press ENTER to exit...")
    else:
        print("success!")
        
def allTestsPass():
    print("waiting for tests to complete...")
    cmd=r"cd ..\tests\ && python runtests.py"
    result=os.system(cmd)
    print("\n"*10)
    if result==0:
        print("All tests finished successfully.")
        return True
    else:
        return False
        
if __name__=="__main__":
    if allTestsPass():
        newVersion()
        cleanUp()
        upload()
        cleanUp()
        print("\n ~ new version was published ~\n")
    else:
        print("Tests failed, publish aborted!\n")