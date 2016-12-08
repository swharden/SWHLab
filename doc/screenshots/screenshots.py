import sys
sys.path.append("../../../")
import matplotlib.pyplot as plt
import swhlab
plt.close('all')
fname=r"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16907055.abf"


### DEMO ########################################
import matplotlib.pyplot as plt
abf=swhlab.ABF(fname)
for sweep in range(4):
    abf.setsweep(sweep)
    plt.plot(abf.sweepX2,abf.sweepY,alpha=.5)
plt.ylabel(abf.units2)
#plt.show()
plt.savefig("readme1.jpg")
plt.close('all')

### DEMO ########################################
#print(sorted(ap.APs[1].keys()))
#['I', 'T', 'Tsweep', 'Vhalf', 'VhalfI1', 'VhalfI2', 'Vmax', 'VmaxI', 'Vmin', 'VminI',
#'VslowIs', 'Vthreshold', 'dVfastIs', 'dVfastMS', 'dVmax', 'dVmaxI', 'dVmin', 'dVminI',
# 'msFallTime', 'msHalfwidth', 'msRiseTime', 'sweep']
import swhlab
import matplotlib.pyplot as plt
ap=swhlab.AP(fname)
ap.detect()
for sweep in range(abf.sweeps):
    aps=[x for x in ap.APs if x["sweep"]==sweep]
    plt.plot([x["Tsweep"] for x in aps],
             [x["Vmax"] for x in aps],
             '.',label="sweep %d"%sweep,alpha=.5)
plt.legend(fontsize=6,loc=8)
plt.ylabel("AP peak value (mV)")
#plt.show()
plt.savefig("readme2.jpg")
plt.close('all')

import swhlab
import matplotlib.pyplot as plt
import numpy as np
ap=swhlab.AP(fname)
ap.detect()
medFreq=[np.median(f) for f in ap.get_bySweep("freqs")]
plt.plot(medFreq[:15],'.',ms=10)
plt.ylabel("Median AP Frequency (Hz)")
plt.xlabel("sweep number")
plt.margins(.1,.1)
#plt.show()
plt.savefig("readme3.jpg")
plt.close('all')