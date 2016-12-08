## iterating through sweeps
You could use `setsweep(sweepNum)` to manually set the sweep. To print the data from every sweep you would have to do something like this:

> ```python
abf=ABF("16d12001.abf")
for i in range(abf.nSweeps):
    abf.setsweep(i)
    print(abf.sweepY)
```

A better alternative is to use the `setsweeps()` generator! It sets the sweep automatically. To print data from every sweep, just do this:

> ```python
abf=ABF("16d12001.abf")
for sweep in abf.setsweeps():
    print(abf.sweepY)
```
    
In both cases, the output is:
> ```
[ 84.606 -76.396   1.002 ...,   7.21  -26.659  88.05 ]
[ 95.063  30.425 -63.488 ..., -63.957  79.739  23.787]
[  2.289  37.038   0.572 ..., -39.47   10.829 -14.148]
[ 92.65  -14.149 -51.532 ..., -74.923  48.574  40.873]
[  5.52  -49.743 -96.119 ..., -41.402  57.862 -34.983]
[-60.543 -71.977  15.328 ..., -91.621 -75.589 -17.799]
[ 49.24  -42.804  46.702 ..., -59.665 -82.801  66.771]
[  9.254  59.779 -51.602 ..., -21.375  -1.283  16.509]
[ -3.544  13.622 -15.717 ...,  26.75  -16.768 -79.236]
[ 59.821   4.73   85.693 ..., -97.234  88.224 -64.665]
```
