"""
Given a project folder (with ABFs and micrographs), convert
all images to JPG, color adjust micrographs, add scale bars, etc.
then create an index.html page
"""

import os
import sys
if not os.path.abspath('../../../') in sys.path:
    sys.path.append('../../../')
import matplotlib.pyplot as plt
import numpy as np
from swhlab.indexing.indexing import doStuff

if __name__=="__main__":
    ABFfolder=R"X:\Data\2P01\2016\2017-01-09 AT1"
    doStuff(ABFfolder,analyze=True,convert=True,index=True,overwrite=True)