# SWHLab
SWHLab is a python module designed to ***facilitate exploratory analysis of electrophysiological data*** by providing a simple object model through which to interact with it. It is intended to be used as a tool for neurophysiology data exploration, rather than production or presentation. The primary goal of this project is to lower the effort barrier required to impliment experimental analysis methods, with the hope of faciliating scientific discovery by promoting the development of novel analysis techniques. 

```python
import swhlab
import matplotlib.pyplot as plt
abf=swhlab.ABF("16d12031.abf")
for sweep in (abf.sweeps):
  plt.plot(abf.sweepX,sweepY)
plt.ylabel(abf.units)
plt.plot()
```

**Scope:** Although initially designed to analyze whole-cell patch-clamp recordings of neurons from ABF (axon binary format) files, the core class within this module may be eaily modified to accommodate another recording method or file format. SWHLab leans heavily on the [NeoIO](https://pythonhosted.org/neo/io.html) module to provide low-level file access, and therefore is likely to support other electrophysiological file formats with minimal modifiation.

**Data access:** The core of SWHLab is the `swhlab.ABF` class which has tools that make it easy to obtain sweep data, information from the header, protocol information, protocol sweeps, sub-sections of sweeps, averages of ranges of sweeps, baseline-subtracted sweeps, low-pass-filtered sweeps, amplifier information, tag times and comments, etc.

**Event detection:** Event detection classes live in the analysis folder and can be imported as needed. For example, the action potential detection class can be initiated with an ABF object and perform many high level operations:

```python
import swhlab
import matplotlib.pyplot as plt
ap=swhlab.AP("16d12031.abf")
ap.detect()
plt.plot([x["time"] for x in ap.APs],
         [x["freq"] for x in ap.APs])
plt.show()
```

**Protocol detection and data inspection:** If an experiment has thousands of data files, was performed a long time ago, or was conducted by another researcher, it is often useful to quickly inspect the contents of the data. Manually inspecting electrophysiology data can be tedious. The SWHLab module has a _protocols_ sub-module and an _indexing_ sub-module which simplifies this task by:
 1. automatically determine how to analyze a file
  * i.e., if it's current clamp and contains action potentials, analyze it as such
 2. perform the analysis without user input and save the result as a JPG
 3. after potentially thousands of files are analyzed, create a flat-file HTML report which can view the data in any browser
Note that because this entire process can occur without user input, it can be performed automatically as new data is being recorded. This allows operators at the electrophysiology rig to view the results of complicated analysis routines immediately after the data is saved.
