"""
SWHLab is a python module intended to provide easy access to high level ABF
file opeartions to aid analysis of whole-cell patch-clamp electrophysiological
recordings. Although graphs can be interactive, the default mode is to output
PNGs and generate flat file HTML indexes to allow data browsing through any
browser on the network. Direct ABF access was provided by the NeoIO module.

* if a site-packages warning is thrown, force use of developmental version by:
      sys.path.insert(0,'../')
      
"""
import logging
import sys
import os
import swhlab

def tryLoadingFrom(tryPath,moduleName='swhlab'):
    """if the module is in this path, load it from the local folder."""
    if not 'site-packages' in swhlab.__file__:
        print("loaded custom swhlab module from",
              os.path.dirname(swhlab.__file__))
        return # no need to warn if it's already outside.
    while len(tryPath)>5:
        sp=tryPath+"/swhlab/" # imaginary swhlab module path
        if os.path.isdir(sp) and os.path.exists(sp+"/__init__.py"):
            if not os.path.dirname(tryPath) in sys.path:
                sys.path.insert(0,os.path.dirname(tryPath))
            print("#"*80)
            print("# WARNING: using site-packages swhlab module")
            print("#"*80)
        tryPath=os.path.dirname(tryPath)
    return
tryLoadingFrom(os.path.abspath('./'))

# from here, assume everything is fine.

logDateFormat='%m/%d/%Y %I:%M:%S %p'
logFormat='%(asctime)s\t%(levelname)s\t%(message)s'
loglevel_SILENT=logging.FATAL
loglevel_QUIET=logging.INFO
loglevel_DEBUG=logging.DEBUG
loglevel_ERROR=logging.ERROR
loglevel=loglevel_QUIET # change this at will

from swhlab.version import __version__
from swhlab.core import ABF
from swhlab.plotting.core import ABFplot as PLOT
from swhlab.analysis.ap import AP