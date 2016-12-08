import swhlab

import matplotlib.pyplot as plt
abf=swhlab.ABF(r"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16907055.abf")
for sweep in range(4):
    abf.setsweep(sweep)
    plt.plot(abf.sweepX2,abf.sweepY,alpha=.5)
plt.ylabel(abf.units2)
plt.plot()