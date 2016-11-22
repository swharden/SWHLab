import logging

logDateFormat='%m/%d/%Y %I:%M:%S %p'
logFormat='%(asctime)s\t%(levelname)s\t%(message)s'
loglevel_SILENT=logging.FATAL
loglevel_QUIET=logging.INFO
loglevel_DEBUG=logging.DEBUG
loglevel_ERROR=logging.ERROR

loglevel=loglevel_QUIET # change this at will

import sys
sys.path.append("../") #TODO: THIS HELPS SPYDER FIND DOCS

from swhlab.version import __version__
from swhlab.core import ABF
from swhlab.plotting.core import ABFplot as PLOT
from swhlab.analysis.ap import AP