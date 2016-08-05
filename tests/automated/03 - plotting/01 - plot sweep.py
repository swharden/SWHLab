"""
simple examples of how to load an ABF and use swhlab.plot.sweep()
This function has lots of options! reads the docs for all of them.
"""
import swhlab
import os
import pylab

savePrefix=os.path.abspath(os.path.basename(__file__))+"_"
abf=swhlab.ABF(r"C:\Apps\pythonModules\abfs\16718036.abf")

swhlab.plot.sweep(abf) #default to the first sweep
swhlab.plot.save(abf,savePrefix+"1.png")

swhlab.plot.sweep(abf,10) #10th sweep
swhlab.plot.save(abf,savePrefix+"2.png")

swhlab.plot.sweep(abf,-1) #last sweep
swhlab.plot.save(abf,savePrefix+"3.png")

swhlab.plot.sweep(abf,'all',continuous=True)
swhlab.plot.save(abf,savePrefix+"5.png")

swhlab.plot.sweep(abf,'all',alpha=.2) #default as overlay
swhlab.plot.save(abf,savePrefix+"4.png")

swhlab.plot.sweep(abf,'all',offsetY=150) #stacked
swhlab.plot.save(abf,savePrefix+"5.png")

swhlab.plot.sweep(abf,'all',offsetY=20,offsetX=.2) #fancy
swhlab.plot.save(abf,savePrefix+"6.png",close=False)
pylab.grid() # by disabling "close", we can make more changes
pylab.title("I'm changing things up!")
swhlab.plot.save(abf,savePrefix+"7.png")

#swhlab.plot.save(abf) # no filename will "show" the image in a popup