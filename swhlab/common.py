# -*- coding: utf-8 -*-

import numpy as np
import time

def where_cross(data,threshold):
    """return a list of Is where the data first crosses above threshold."""
    Is=np.where(data>threshold)[0]
    Is=np.concatenate(([0],Is))
    Ds=Is[:-1]-Is[1:]+1
    return Is[np.where(Ds)[0]+1]

def timeit(timer=None):
    """simple timer"""
    if timer is None:
        return time.time()
    else:
        took=time.time()-timer
        if took<1:
            return "%.02f ms"%(took*1000.0)
        elif took<60:
            return "%.02f s"%(took)
        else:
            return "%.02f min"%(took/60.0)