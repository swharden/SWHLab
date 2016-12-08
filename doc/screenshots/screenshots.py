import sys
sys.path.append("../../../")
import matplotlib.pyplot as plt
import swhlab
import numpy as np
plt.close('all')
fname=r"X:\Data\2P01\2016\2016-09-01 PIR TGOT\16907055.abf"

np.set_printoptions(precision=4)


abfFile=R"C:\Users\scott\Documents\important\demodata\abfs\16d07022.abf"
abf=swhlab.ABF(abfFile)
abf.kernel=abf.kernel_gaussian(sizeMS=100)
abf.setsweep(200)
plt.figure(figsize=(10,3))
plt.grid()
plt.plot(abf.sweepX2,abf.sweepY,alpha=.5,label="original")
plt.plot(abf.sweepX2,abf.sweepYfiltered(),alpha=.5,lw=3,color='r',label="filtered")
plt.axis([.5,1,-120,-70])
plt.legend()
plt.savefig("lowpass.png")

#### DEMO ########################################
#import matplotlib.pyplot as plt
#abf=swhlab.ABF(fname)
#for sweep in range(5):
#    abf.setsweep(sweep)
#    print(abf.sweepY.astype('float'))

#[-71.4722 -71.4722 -71.5027 ..., -69.7021 -69.7021 -69.7632]
#[-69.7327 -69.7327 -69.7327 ..., -64.1174 -64.1479 -64.1174]
#[-64.1174 -64.1479 -64.1174 ..., -70.282  -70.3125 -70.282 ]
#[-70.282  -70.282  -70.282  ..., -73.3643 -73.3337 -73.3032]
#[-73.3337 -73.3032 -73.3643 ..., -75.0122 -74.9817 -74.9817]

#### DEMO ########################################
#import matplotlib.pyplot as plt
#abf=swhlab.ABF(fname)
#for sweep in range(4):
#    abf.setsweep(sweep)
#    plt.plot(abf.sweepX2,abf.sweepY,alpha=.5)
#plt.ylabel(abf.units2)
##plt.show()
#plt.savefig("readme1.png")
#plt.close('all')
#
#### DEMO ########################################
##print(sorted(ap.APs[1].keys()))
##['I', 'T', 'Tsweep', 'Vhalf', 'VhalfI1', 'VhalfI2', 'Vmax', 'VmaxI', 'Vmin', 'VminI',
##'VslowIs', 'Vthreshold', 'dVfastIs', 'dVfastMS', 'dVmax', 'dVmaxI', 'dVmin', 'dVminI',
## 'msFallTime', 'msHalfwidth', 'msRiseTime', 'sweep']
#import swhlab
#import matplotlib.pyplot as plt
#ap=swhlab.AP(fname)
#ap.detect()
#for sweep in range(abf.sweeps):
#    aps=[x for x in ap.APs if x["sweep"]==sweep]
#    plt.plot([x["Tsweep"] for x in aps],
#             [x["Vmax"] for x in aps],
#             '.',label="sweep %d"%sweep,alpha=.5)
#plt.legend(fontsize=6,loc=8)
#plt.ylabel("AP peak value (mV)")
##plt.show()
#plt.savefig("readme2.png")
#plt.close('all')
#
#import swhlab
#import matplotlib.pyplot as plt
#import numpy as np
#ap=swhlab.AP(fname)
#ap.detect()
#medFreq=[np.median(f) for f in ap.get_bySweep("freqs")]
#plt.plot(medFreq[:15],'.',ms=10)
#plt.ylabel("Median AP Frequency (Hz)")
#plt.xlabel("sweep number")
#plt.margins(.1,.1)
##plt.show()
#plt.savefig("readme3.png")
#plt.close('all')