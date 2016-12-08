# SWHLab
SWHLab is a python module designed to ***facilitate exploratory analysis of electrophysiological data*** by providing a simple object model through which to interact with it. The primary goal of this project is to lower the effort barrier required to impliment experimental analysis methods, with the hope of faciliating scientific discovery by promoting the development of novel analysis techniques. 

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

**Event detection:** Event detection classes live in the analysis folder and can be imported as needed. For example, the action potential detection class can be initiated with an ABF object and perform many high level operations. (`swhlab.AP`), for example, takes-in a single `swhlab.ABF` object and p

SWHLab is a python module intended to provide easy access to high level ABF file opeartions to aid analysis of whole-cell patch-clamp electrophysiological recordings. Although graphs can be interactive, the default mode is to output PNGs and generate flat file HTML indexes to allow data browsing through any browser on the network. 

**Scope:** SWHLab is a collection of tools to provide easy access to ABF files containing patch-clamp electrophysiology data. NeoIO provides
direct access to ABF data, and SWHLab makes it easy to perform high-level operations (such as event detection, action potential characterization, calculation of cell capacitance from voltage clamp or current clamp traces). SWHLab intended to be used as a tool for neurophysiology data exploration, rather than production or presentation. It can be easily incorporated into other projects where accessing ABF data is desired.
plt.ylabel(abf.units)
