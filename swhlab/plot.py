"""
This module contains scripts to plot SWHLab ABF objects.
Try to keep analysis (event detection, etc) out of this.
"""

import os
import logging
from . import abf as ABFmodule
ABF=ABFmodule.ABF
import matplotlib.pyplot as plt

class ABFplot:
    def __init__(self,abf,loglevel=logging.DEBUG):
        """Load an ABF and get ready to plot stuff."""
        self.log = logging.getLogger("swhlab plot")
        self.log.setLevel(loglevel)
        
        # prepare ABF class
        if type(abf) is str:
            self.log.debug("filename given, turning it into an ABF class")
            abf=ABF(abf)
        self.abf=abf
            
        # TODO: size in pixels
        self.figure_width=10
        self.figure_height=5
        self.figure_dpi=300
        self.subplot=False # set to True to prevent running plt.figure()
        
        self.gridAlpha=.5
        self.title=os.path.basename(abf.filename)
        self.traceColor='b'
        self.kwargs={"alpha":.8}
        self.rainbow=True
        self.colormap="Dark2"
        self.marginX,self.marginY=0,.1
        
        self.log.debug("plot initiated")

        
    ### high level plot operations
            
    def figure(self):
        """make sure a figure is ready."""
        if self.subplot:
            self.log.debug("subplot mode enabled, not creating new figure")
        else:
            self.log.debug("creating new figure")
            plt.figure(figsize=(self.figure_width,self.figure_height))
        
    def show(self):
        numFigures=plt._pylab_helpers.Gcf.get_num_fig_managers()
        self.log.debug("showing figures (%d)"%numFigures)
        plt.show()
        
    def close(self,closeAll=True):
        numFigures=plt._pylab_helpers.Gcf.get_num_fig_managers()
        if closeAll:
            self.log.debug("closing all %d figures"%numFigures)
            plt.close('all')
        else:
            self.log.debug("closing 1 figure (of %d)"%numFigures)
            plt.close()
                     
    ### misc
    def getColor(self,fraction,reverse=False):
        cm=plt.get_cmap(self.colormap)
        if reverse:
            fraction=1-fraction
        return cm(fraction)
        
    def setColorBySweep(self):
        if self.rainbow:
            self.kwargs["color"]=self.getColor(self.abf.sweep/self.abf.sweeps)
        else:
            self.kwargs["color"]=self.traceColor
    ### plot modifications
                
    def comments(self,minutes=False):
        """
        Add comment lines/text to an existing plot. Defaults to seconds.
        Call after a plot has been made, and after margins have been set.
        """ 
        if self.comments==0:
            return
        self.log.debug("adding comments to plot")
        for i,t in enumerate(self.abf.comment_times):
            if minutes:
                t/=60.0
            plt.axvline(t,color='r',ls=':')
            X1,X2,Y1,Y2=plt.axis()
            Y2=Y2-abs(Y2-Y1)*.02
            plt.text(t,Y2,self.abf.comment_tags[i],color='r',rotation='vertical',
                     ha='right',va='top',weight='bold',alpha=.5,size=8,)
            
    def decorate(self,show=False):
        self.log.debug("decorating")
        plt.title(self.title)
        plt.xlabel("seconds")
        plt.ylabel(self.abf.units2)
        if self.gridAlpha:
            plt.grid(alpha=self.gridAlpha)
        plt.margins(self.marginX,self.marginY)
        plt.tight_layout()
        if show:
            plt.show()
        
    ### figure creation
    
    def figure_chronological(self):
        """plot every sweep of an ABF file."""
        self.log.debug("creating chronological plot")
        self.figure()
        for sweep in range(self.abf.sweeps):
            self.abf.setsweep(sweep)
            self.setColorBySweep()
            plt.plot(self.abf.sweepX,self.abf.sweepY,**self.kwargs)
        self.comments()
        self.decorate()
        
    def figure_sweep(self,sweep=0):
        self.log.debug("plotting sweep %d",sweep)
        self.figure()
        self.abf.setsweep(sweep)
        plt.plot(self.abf.sweepX2,self.abf.sweepY,**self.kwargs)
        self.decorate()
            
    def figure_sweeps(self, offsetX=0, offsetY=0):
        """plot every sweep of an ABF file."""
        self.log.debug("creating overlayed sweeps plot")
        self.figure()
        for sweep in range(self.abf.sweeps):
            self.abf.setsweep(sweep)
            self.setColorBySweep()
            plt.plot(self.abf.sweepX2+sweep*offsetX,
                     self.abf.sweepY+sweep*offsetY,
                     **self.kwargs)
        if offsetX:
            self.marginX=.05
        self.decorate()
        
if __name__=="__main__":
    abfFile=r"C:\Users\scott\Documents\important\2016-07-01 newprotos\16701009.abf"
    #abfFile=r"C:\Users\scott\Documents\important\2016-07-01 newprotos\16701015.abf"
    plot=ABFplot(abfFile)

    plot.subplot=True
    
    plt.figure()
    plt.subplot(221)
    plot.figure_chronological()
    plt.subplot(222)
    plot.figure_sweep(10)
    plt.subplot(223)
    plot.figure_sweeps(.1,100)
    plt.subplot(224)
    plot.figure_sweeps(0,100)
    
    plot.show()
    plot.close(True)
    
#    for abfFile in glob.glob(r"C:\Users\scott\Documents\important\2016-07-01 newprotos\*.abf"):
#        abf=ABF(abfFile)
    
    print("DONE")