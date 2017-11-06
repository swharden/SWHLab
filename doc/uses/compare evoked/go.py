import sys
sys.path.append("../../../")
import swhlab
import matplotlib.pyplot as plt
import numpy as np
import os
import glob

files=[]
files.append(["171018jt_0000", "171018jt_0005"])
files.append(["171018jt_0006", "171018jt_0009"])
files.append(["171018jt_0010", "171018jt_0013"])
files.append(["171018ts_0000", "171018ts_0004"])
files.append(["171018ts_0005", "171018ts_0008"])
files.append(["171018ts_0009", "171018ts_0012"])
files.append(["171019jt_0000", "171019jt_0003"])
files.append(["171019jt_0010", "171019jt_0013"])
files.append(["171020jt_0002", "171020jt_0005"])
files.append(["171020jt_0006", "171020jt_0009"])
files.append(["171020jt_0010", "171020jt_0013"])
files.append(["171020jt_0014", "171020jt_0017"])
files.append(["171020jt_0018", "171020jt_0021"])
files.append(["171020ts_0000", "171020ts_0003"])
files.append(["171020ts_0004", "171020ts_0007"])
files.append(["171020ts_0008", "171020ts_0011"])
files.append(["171023jt_0004", "171023jt_0007"])
files.append(["171023jt_0008", "171023jt_0011"])
files.append(["171023jt_0012", "171023jt_0015"])
files.append(["171023ts_0000", "171023ts_0003"])
files.append(["171023ts_0004", "171023ts_0007"])
files.append(["171024jt_0004", "171024jt_0007"])
files.append(["171024jt_0008", "171024jt_0011"])
files.append(["171024jt_0012", "171024jt_0015"])
files.append(["171024jt_0016", "171024jt_0019"])
files.append(["171024ts_0000", "171024ts_0003"])
files.append(["171024ts_0004", "171024ts_0007"])
files.append(["171024ts_0008", "171024ts_0011"])
files.append(["171024ts_0012", "171024ts_0015"])
files.append(["171025jt_0000", "171025jt_0003"])
files.append(["171025jt_0005", "171025jt_0008"])
files.append(["171025jt_0009", "171025jt_0012"])
files.append(["171025ts_0000", "171025ts_0005"])
files.append(["171025ts_0011", "171025ts_0014"])

group_4mo="""
171018jt_0000 (4)
171018jt_0006 (4)
171018jt_0010 (4)
171018ts_0000 (4) ***
171018ts_0005 (4)
171018ts_0009 (4)
171019jt_0000 (4)
171019jt_0010 (4)
171024jt_0004 (4)
171024jt_0008 (4)
171024jt_0012 (4)
171024jt_0016 (4)
171024ts_0000 (4)
171024ts_0008 (4)
171024ts_0004 (4)
171024ts_0012 (4)
"""

group_22mo="""
171020jt_0002 (4)
171020jt_0006 (4)
171020jt_0010 (4)
171020jt_0014 (4)
171020jt_0018 (4) ***
171020ts_0000 (4) CGP@20m
171020ts_0004 (4) ***
171020ts_0008 (4)
171023jt_0004 (4)
171023jt_0008 (4)
171023jt_0012 (4)
171023ts_0004 (4) NR to BAC
171023ts_0000 (4) NR to BAC
171025jt_0000 (4)
171025jt_0005 (4)
171025jt_0009 (4)
171025ts_0000 (4)
171025ts_0011 (4) NR to BAC
"""


def kernel_gaussian(size=100, sigma=None):
    sigma=size/10 if sigma is None else int(sigma)
    points=np.exp(-np.power(np.arange(size)-size/2,2)/(2*np.power(sigma,2)))
    return points/sum(points)

def lowPassFilter(Ys,size=100):
    kernel=kernel_gaussian(size)
    Ys=Ys.flatten()
    Ys=np.convolve(Ys,kernel,mode='same')
    Ys[:int(len(kernel)/2)]=np.nan
    Ys[-int(len(kernel)/2):]=np.nan
    return Ys

def figureStimulus(abf,sweeps=[0]):
    """
    Create a plot of one area of interest of a single sweep.
    """

    stimuli=[2.31250, 2.35270]
    for sweep in sweeps:
        abf.setsweep(sweep)
        for stimulus in stimuli:
            S1=int(abf.pointsPerSec*stimulus)
            S2=int(abf.pointsPerSec*(stimulus+0.001)) # 1ms of blanking
            abf.sweepY[S1:S2]=np.nan # blank out the stimulus area
        I1=int(abf.pointsPerSec*2.2) # time point (sec) to start
        I2=int(abf.pointsPerSec*2.6) # time point (sec) to end
        baseline=np.average(abf.sweepY[int(abf.pointsPerSec*2.0):int(abf.pointsPerSec*2.2)])
        Ys=lowPassFilter(abf.sweepY[I1:I2])-baseline
        Xs=abf.sweepX2[I1:I1+len(Ys)].flatten()
        plt.plot(Xs,Ys,alpha=.5,lw=2)
    return


if __name__=="__main__":

    inputFolder=R"X:\Data\projects\2017-04-24 aging BLA\2017-10-10 BLA aging round2\data"
    outputFolder=R"C:\Users\swharden\Documents\temp"

    ### MAKE FIGURES
    for parent,child in files:
        fname=os.path.join(inputFolder,child+".abf")
        abf=swhlab.ABF(fname)
        if parent in group_4mo:
            bgcolor='#EEEEFF';
            abf.ID=abf.ID+"_4mo"
        elif parent in group_22mo:
            bgcolor='#FFEEEE';
            abf.ID=abf.ID+"_22mo"
        else:
            bgcolor='#FFFFFF';
            abf.ID=abf.ID+"_unknown"

        plt.figure(figsize=(8,8))
        plt.gca().set_facecolor(bgcolor)
        figureStimulus(abf,10+np.arange(5))
        plt.axhline(0,color='k',ls='--')
        plt.margins(0,.1)
        plt.axis([None,None,None,50])
        plt.title("[%s] %s (sweeps 10-15)"%(parent,abf.ID))
        plt.tight_layout()
        plt.savefig(outputFolder+"/%s_auto.png"%abf.ID)
        plt.axis([None,None,-500,50])
        plt.savefig(outputFolder+"/%s_fixed.png"%abf.ID)
        plt.show()
        plt.close('all')
        print("DONE")


    ### MAKE HTML
    html="<html><body>"
    html+="<h1>Auto-Scaled Stimuli</h1>"
    for fname in sorted(glob.glob(outputFolder+"/*auto*.png")):
        html+="<a href='%s'><img src='%s' height='300'></a>"%(os.path.basename(fname),os.path.basename(fname))
    html+="<hr><h1>Fixed-Scale Stimuli:</h1>"
    for fname in sorted(glob.glob(outputFolder+"/*fixed*.png")):
        html+="<a href='%s'><img src='%s' height='300'></a>"%(os.path.basename(fname),os.path.basename(fname))
    html+="</body></html>"
    with open(outputFolder+"/index.html",'w') as f:
        f.write(html)
    print("HTML FILE CREATED.")