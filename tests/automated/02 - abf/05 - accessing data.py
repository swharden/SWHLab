"""
shows how to pull data from a file
"""
import swhlab
abf=swhlab.ABF(r"C:\Apps\pythonModules\abfs\16718036.abf")
abf.setSweep(10)
print(abf.sweepSize,abf.sweepLength,abf.sweepInterval) #ABF sweep info
print(abf.dataX) #access to raw X data (seconds)
print(abf.dataY) #access to raw Y data (mV or pA)