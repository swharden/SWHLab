# Brute Force Extraction of ABF data
The ABFFIO.DLL is a nightmare. Why should an ABF file be more complex than a WAV file? Let's hack some basic functionality. This page will chronicle some hacks in this direction

# Examples
### extract 16-bit integers from ABf files
This example shows how to open an ABF file as a byte string then create an n-dimensional numpy array from it assuming the bytes are 16-bit integers. Some header at the beginning and end isn't data so it's discarded.
```python
with open("17515019.abf",'rb') as f:
  data=np.ndarray(shape=(int(len(raw)/2),),dtype='<i2',buffer=f.read())
data=data[3000:-500] # trim off the header
Ys=data/(2**5) # ADC to unit via to voltage with multiplication offset
Xs=np.arange(len(data))/20000 # create Xs from sample rate
plt.plot(Xs,Ys)
plt.ylabel("membrane potential (mV)")
plt.xlabel("experiment duration (sec)")
```

