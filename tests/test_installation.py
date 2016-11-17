import swhlab

if __name__=="__main__":
    print("your system installed SWHLab version is",swhlab.__version__)
    plot=swhlab.PLOT("abfs/gain.abf")
    plot.figure_sweeps()
    AP=swhlab.AP(plot.abf)
    print("median AP frequency:")
    for sweep,freq in enumerate(AP.get_freq_bySweep_median()):
        print("sweep %d had median frequency %.02f Hz"%(sweep,freq))