"""
Plot some sweeps where optogenetic blue light stimulation (BLS)
was applied by a digital output.
"""

note="""
quantity class modified:
    class Quantity(np.ndarray):

        # TODO: what is an appropriate value?
        __array_priority__ = 21

        def __new__(cls, data, units='', dtype=None, copy=True):
            if isinstance(data, Quantity):
                if units:
                    data = data.rescale(units)
                if isinstance(data, unit_registry['UnitQuantity']):
                    return 1*data
                return np.array(data, dtype=dtype, copy=copy, subok=True).view(cls)

            ret = np.array(data, dtype=dtype, copy=copy).view(cls)
            if type(units) is bytes:
                units=units.decode
            units=str(units).strip()
            if " " in units:
                units=units.split(" ")
                units=units[1]
            if units=="method":
                units="years"
            #print(">>>>>>",type(units),units)
            ret._dimensionality.update(validate_dimensionality(units))
            return ret
"""

import os
import sys
if not os.path.abspath('../../../') in sys.path:
    sys.path.append('../../../')
import matplotlib.pyplot as plt
import numpy as np
import swhlab

import webinspect

if __name__=="__main__":
    fname=r"X:\Data\2P01\2016\2017-01-09 AT1\17109017.abf"
    abf=swhlab.ABF(fname)
    webinspect.blacklist=['t_start','t_stop']
    for item in abf.ABFreader.read_protocol():
        plt.figure()
        for analogSignal in item.__dict__['analogsignals'][1:]:
            print()
            print(analogSignal)
            plt.plot(analogSignal)
        plt.show()

    print("DONE")