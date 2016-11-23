import logging
import sys
import os


# this is how force python to load THIS swhlab module (not the system one)
if not 'swhlab' in sys.modules:
    if 'site-packages' in os.path.abspath('./'):
        import swhlab
        print("### swhlab imported normally ###")
    else:
        print("### ATTEMPTING CUSTOM SWHLAB MODULE IMPORT ###")
        if os.path.isdir('../swhlab/'): # this is the module to use
            sys.path.insert(0,'../') # must be inserted (top), not appended (bottom)
        import swhlab # even though we don't use it, submodules (tests) will.
        print("### IMPORTED [%s]"%os.path.abspath(os.path.dirname(swhlab.__file__)))

__version3__='asdfasdf' # for testing

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