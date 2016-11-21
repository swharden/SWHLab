import sys
sys.path.append("../") #TODO: MAKE THIS BETTER
import swhlab

if __name__=="__main__":
    print("your system installed SWHLab version is",swhlab.__version__)
    
    print("\n\n\n##### SETTING LOG LEVEL TO 'DEBUG' ####")
    swhlab.loglevel=swhlab.loglevel_DEBUG
    
    print("\n\n\n##### DEMONSTRATING PLOT ####")
    plot=swhlab.PLOT("abfs/gain.abf")
    plot.figure_sweeps()
    plot.show()
    
    print("\n\n\n##### DEMONSTRATING AP DETECTION ####")
    AP=swhlab.AP(plot.abf)
    for sweep,freq in enumerate(AP.get_bySweep("median")):
        print("sweep %d had median frequency %.02f Hz"%(sweep,freq))