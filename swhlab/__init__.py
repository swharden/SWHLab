import logging

logDateFormat='%m/%d/%Y %I:%M:%S %p'
logFormat='%(asctime)s\t%(levelname)s\t%(message)s'
loglevel_SILENT=logging.ERROR
loglevel_QUIET=logging.INFO
loglevel_DEBUG=logging.DEBUG

loglevel=loglevel_QUIET # change this at will

from swhlab.version import __version__
from swhlab.swh_abf import ABF
from swhlab.swh_plot import ABFplot as PLOT
from swhlab.swh_ap import AP