"""
SWHLab4 - ABF analysis in Python by Scott Harden (SWHarden.com)

Usage:
 >>> import swhlab
 >>> abf=swhlab.ABF('./path/to/some.abf')
 >>> swhlab.plot.sweep(abf,'all')
 >>> swhlab.plot.show(abf)
"""

import os
import tempfile
import imp
import sys

UPDATEFROM="http://www.swharden.com/software/swhlab/versions/"
UPDATECHECK="http://www.swharden.com/software/swhlab/version.php"
LOCALPATH=os.path.dirname(os.path.realpath(__file__)) #'/path/to/swhlab/'
TEMPPATH = tempfile.gettempdir()+"/swhlab/"

def reload():
    # unload all modules with 'swhlab' in them
    print(" ~~ FORCABLY RELOADING SWHLAB ~~")
    print("     (don't do this too often)")
    loadedmodules=sys.modules.keys()
    for module in loadedmodules:
        if not "swhlab" in module:
            continue
        print("      reloading [%s]"%module)
        imp.reload(sys.modules[module])
        #del module
    # unload things we imported into the toplevel namespace
    try:
        global VERSION,ABF
        del VERSION
        del ABF
    except:
        pass
    print(" -- reload successful.")

from swhlab.version import version as VERSION # variable from adjacent file

#import every script from this submodule. order is critical!
from swhlab.core import abf
ABF = abf.ABF
from swhlab.core import common
from swhlab.core import plot
from swhlab.core import ap, memtest
from swhlab.origin import origin
from swhlab.core import version

if __name__=="__main__":
    reload()