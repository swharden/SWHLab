import sys
sys.path.insert(0,'../') # force us to import ../swhlab/ module
import swhlab

import numpy as np
import unittest
import os
import shutil
import webbrowser
import matplotlib.pyplot as plt
import sys

testAbfPath='./abfs/gain.abf'

HTML_TEMPLATE="""<html><head><style>

img{
    margin: 10px;
    border: 1px solid black;
    box-shadow: 5px 5px 10px grey;
    height: 300px;
    }

body{}
    
</style></head><body><div align="center">
~CONTENT~
</div><br><br><br><br></body></html>
"""

ALLGOOD=True
LOG=""

class TEST_01_core(unittest.TestCase):
    """only use functionality in core.py"""    
    
    def tearDown(self):
        global ALLGOOD,LOG
        for method, error in self._outcome.errors:
            LOG+='\n%s: '%method
            if error:
                LOG+="FAIL [%s]"%str(error)
                ALLGOOD=False
            else:
                LOG+="PASS"
    
    def test_0010_loadAndClose(self):
        """just load an ABF"""
        abf=swhlab.ABF(testAbfPath)
        assert(len(abf.sweepY)) # ensure we have data
        
    def test_0020_sweepManipulation(self):
        """try setting sweeps to different use cases."""
        abf=swhlab.ABF(testAbfPath)
        abf.setsweep(0)
        abf.setsweep(1)
        abf.setsweep(-1) # negative numbers start from end
        assert(abf.sweep==abf.sweeps-1)
        abf.setsweep('-1') # should convert to 1
        abf.setsweep('-lolz') # should fail
        
    def test_0030_average(self):
        """test abf.average()"""
        abf=swhlab.ABF(testAbfPath)
        abf.average()
        abf.average(.2,.3)
        abf.average(setsweep=-1)
        assert abf.sweep == abf.sweeps-1
        abf.average(999,999)
        abf.average(888,999)
        abf.average(0,999)
        abf.average(-999,999)
        abf.average(-999,0)
        
    def test_0040_averageSweep(self):
        """test abf.averageSweep()"""
        abf=swhlab.ABF(testAbfPath)
        abf.averageSweep()
        abf.averageSweep(0,1)
        
    def test_0050_derivative(self):
        abf=swhlab.ABF(testAbfPath)
        abf.derivative=True
        abf.setsweep(1)
        assert len(abf.sweepD)>100
        
class TEST_01_plot(unittest.TestCase):
    """only use functionality in core and plotting/core.py"""    
        
    def tearDown(self):
        global ALLGOOD,LOG
        for method, error in self._outcome.errors:
            LOG+='\n%s: '%method
            if error:
                LOG+="FAIL [%s]"%str(error)
                ALLGOOD=False
            else:
                LOG+="PASS"
    
    def test_0005_plotWithOnlyCore(self):
        abf=swhlab.ABF(testAbfPath)
        abf.derivative=True
        abf.setsweep(-1) # required to do again
        
        plt.figure(figsize=(10,10))
        
        plt.subplot(211)
        plt.grid(alpha=.5)
        plt.title("plotting directly from swhlab.ABF")
        plt.ylabel(abf.units2)
        plt.plot(abf.sweepX,abf.sweepY,alpha=.5)
        
        plt.subplot(212)
        plt.grid(alpha=.5)
        plt.ylabel(abf.unitsD2)
        plt.xlabel("time (sec)")
        plt.plot(abf.sweepX,abf.sweepD,alpha=.5)

        plt.tight_layout()
        plt.savefig('./output/raw.png')
        plt.close('all')
    
    def test_0010_loadAndClose(self):
        plot=swhlab.PLOT(testAbfPath)
        assert(plot.abf.sweeps>1)
        
    def test_0020_singleSweep(self):
        plot=swhlab.PLOT(testAbfPath)
        plot.figure_sweep(2)
                
    def test_0030_saveFig(self):
        plot=swhlab.PLOT(testAbfPath)
        plot.figure_sweep(2)
        plot.save('./output/sweep.png',fullpath=True)
        
    def test_0035_frame(self):
        plot=swhlab.PLOT(testAbfPath)
        plot.figure_sweep(2)
        swhlab.plotting.frameAndSave(plot.abf,"demo frame",
                                     saveAsFname='./output/sweepFramed.jpg')
        
    def test_0040_saveJPG(self):
        plot=swhlab.PLOT(testAbfPath)
        plot.figure_sweep(2)
        plot.save('./output/sweep.jpg',fullpath=True)
        
    def test_0050_figures(self):
        plot=swhlab.PLOT(testAbfPath)
        plot.figure_chronological()
        plot.save('./output/chron.jpg',fullpath=True)
        plot.figure_sweeps()
        
        plot.kwargs["lw"]=5
        plot.kwargs["alpha"]=.5
        plot.save('./output/overlay.jpg',fullpath=True)
        plot.figure_sweeps(offsetX=.1,offsetY=50)
        
        plt.axis([0,1,None,None])
        plot.save('./output/kwargs.jpg',fullpath=True)
        
class TEST_02_APs(unittest.TestCase):
    """action potential detection"""    
        
    def tearDown(self):
        global ALLGOOD,LOG
        for method, error in self._outcome.errors:
            LOG+='\n%s: '%method
            if error:
                LOG+="FAIL [%s]"%str(error)
                ALLGOOD=False
            else:
                LOG+="PASS"
                
    def test_0010_detect(self):
        abf=swhlab.ABF(testAbfPath)
        APs=swhlab.AP(abf)
        APs.detect()
        assert len(APs.APs)
        
    def test_0020_detectAndPlot1(self):
        abf=swhlab.ABF(testAbfPath)
        APs=swhlab.AP(abf)
        APs.detect()
        
        plt.figure()
        #freqs firsts times 
        for feature in "count average median".split(" "):
            plt.plot(np.arange(abf.sweeps),APs.get_bySweep(feature),'.-',
                     label=feature,alpha=.5)
        plt.legend(loc=2)
        plt.margins(.1,.1)
        plt.xlabel("sweep")
        plt.savefig('./output/APs1.jpg')
        plt.close('all')
        
    def test_0021_detectAndPlot2(self):
        abf=swhlab.ABF(testAbfPath)
        APs=swhlab.AP(abf)
        APs.detect()        
        Xs=APs.get_bySweep("times")
        Ys=APs.get_bySweep("freqs")        
        plt.figure(figsize=(10,8))
        for sweep in range(abf.sweeps):
            if not len(Ys[sweep]):
                continue
            abf.setsweep(sweep)            
            plt.subplot(212)
            plt.plot(Xs[sweep][1:],Ys[sweep],'.',alpha=.5,label="sweep %d"%sweep,ms=10)
            plt.subplot(211)
            plt.plot(abf.sweepX2,abf.sweepY,alpha=.5)
        plt.ylabel(abf.units2)
        plt.subplot(212)
        plt.grid(alpha=.5)
        plt.legend(loc=3)
        plt.margins(.1,.1)
        plt.ylabel("frequency (Hz)")
        plt.xlabel("time (seconds)")
        plt.tight_layout()
        plt.savefig('./output/APsFreqs.jpg')
        plt.close('all')
        
class TEST_99_html(unittest.TestCase):
    """create an index page for ./output"""   
    
    def tearDown(self):
        global ALLGOOD,LOG
        for method, error in self._outcome.errors:
            LOG+='\n%s: '%method
            if error:
                LOG+="FAIL [%s]"%str(error)
                ALLGOOD=False
            else:
                LOG+="PASS"
    
    def test_0000_cleanup(self):
        plt.close('all')
        
    def test_0010_index(self):
        pics=[x for x in os.listdir('./output') if x[-3:] in ['jpg','png']]
        html="<h1>SWHLab unittest figures</h1>"
        for pic in sorted(pics):
            #html+='<br><br><br>'
            #html+='<h2>%s</h2>'%pic
            html+='<a href="%s"><img src="%s"></a>'%(pic,pic)
        html+='<div align="left"><hr><h1>TEST RESULTS:</h1>'
        for line in LOG.split("\n"):
            color="#00CC00"
            if ": FAIL " in line:
                color="#FF0000"
            html+='<code style="color: %s;">%s</code><br>'%(color,line)
        html+='<code><b>All good to proceed? %s</b></code>'%str(ALLGOOD)
        html+="</div>"
        f=open('./output/index.html','w')
        html=HTML_TEMPLATE.replace("~CONTENT~",html)
        if not ALLGOOD:
            html=html.replace('body{','body{background-color: #FFCCCC;')
        f.write(html)
        f.close()
        webbrowser.open_new_tab(os.path.abspath('./output/index.html'))
        #print(1/0)

def isEverythingGood(verbose=False):
    """return True if all unit tests pass."""
    global ALLGOOD
    swhlab.loglevel=swhlab.loglevel_SILENT   
    if verbose:
        swhlab.loglevel=swhlab.loglevel_DEBUG
    try:
        shutil.rmtree('./output/') # delete old test outputs
    except:
        pass
    try:
        os.mkdir('./output')
    except:
        pass
    if os.path.isdir('./output'):
        swhlab.plotting.core.IMAGE_SAVE=True
        swhlab.plotting.core.IMAGE_SHOW=False        
        unittest.main()
        if ALLGOOD:
            return True
        else:
            return False
    else:
        print("PROBLEM DELETING OR MAKING OUTPUT FOLDER")
        return False
    
        
if __name__=="__main__":
    if isEverythingGood(verbose=True):
        sys.exit(0)
    else:
        sys.exit(1)