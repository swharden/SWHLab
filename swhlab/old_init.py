# start out this way so tests will import the local swhlab module
import sys
import os
sys.path.insert(0,os.path.abspath('../'))
import swhlab

import logging

# if swhlab is installed in 'site-packages' like normal, import it silently.
# if a local (development) module exists, import that one instead.
module_was_found=False # True if swhlab was found (maybe not imported)
module_lives_outside=False # True if not in a 'site-packages' folder
if 'swhlab' in sys.modules:
    module_was_found=True
if not module_was_found or not 'site-packages' in __file__:
    module_lives_outside=True
    print("Running outside site-pacakges, so hunt for swhlab module ...")
    #while not 'swhlab' in os.listdir():
    #while not os.path.isdir('swhlab'):
    while not module_was_found:
        if os.path.isdir('swhlab') and "__init__.py" in os.listdir('swhlab'):
            module_was_found=True
            break
        else:
            os.chdir('../')
            print("  python moved to",os.path.abspath('./'))
            if os.path.abspath('../')==os.path.abspath('./'):
                break

if not module_was_found:
    print("swhlab module was never found!")
else:
    if not 'swhlab' in sys.modules:
        import swhlab
        print("swhlab was imported from",swhlab.__file__)
    
    # by here, we assume swhlab is properly loaded.
    from swhlab.version import __version__
    __version2__='lolz'
    
    logDateFormat='%m/%d/%Y %I:%M:%S %p'
    logFormat='%(asctime)s\t%(levelname)s\t%(message)s'
    loglevel_SILENT=logging.FATAL
    loglevel_QUIET=logging.INFO
    loglevel_DEBUG=logging.DEBUG
    loglevel_ERROR=logging.ERROR
    loglevel=loglevel_QUIET # change this at will

    from swhlab.core import ABF
    from swhlab.plotting.core import ABFplot as PLOT
    from swhlab.analysis.ap import AP