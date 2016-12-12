# Spectral Noise Reduction
The code in [01.py](01.py) outlines how to take a noisy electrophysiological recording and improve it. The assumption is that the noise is 60 Hz and its harmonics. This is the result:

![](done.png)

## Frequency component of this signal
Plotting the raw frequency component and highlighting 60 Hz and every third harmonic, it becomes evident that not every odd harmonic is an offender.

![](offenders.png)

Although I could selectively silence just the bad ones...

![](offenders2.png)

It doesn't make a huge difference as compared to just silencing all of them.
