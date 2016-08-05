"""
Load an ABF and access basic stats.
"""
import swhlab

abf=swhlab.ABF(r'C:\Apps\pythonModules\abfs\16711016.abf')
abf.abfinfo(True)
print("this ABF rate:",abf.abfinfo(returnDict=True)["rate"])