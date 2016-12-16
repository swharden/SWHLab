# Overview
Using voltage-clamp recordings where EPSCs and IPSCs go in different directions, find a way to separate and quantify the phasic current of these excitatory and inhibitory currents. Some of these currents are so small, they are near the noise floor. How do you pull them out of the noise floor? 

Problem|Solution
---|---
Previously noise has been estimated using a Gaussian fit of the center most data points then subtracted out. **Here, I present a better way to create a Gaussian curve of the noise floor** suitable for subtraction to isolate positive/negative phasic currents. It doesn't use curve fitting or convolution, so it's extremely fast computationally.|![](2016-12-16-tryout.png)

## Programming Steps
 - **Break the data** into "chunks" 10ms in length
 - **Measure the variance** of each chunk and isolate data only from the quietest chunks (where the chunk variance is in the lower 10-percentile of all the chunks)
 - **perform a histogram** on just the quiet data. The result will be assumed to be the noise floor, but requires creation of a curve.
	 - since the noise is random, we can expect a normal distribution. 
	 - This means no curve _fitting_ is required. We can generate this Gaussian curve because mu is the mean of the data, and sigma is the standard deviation of the data.
 - **Subtract** this histogram from the histogram of all the data. The difference will be phasic currents with noise removed, with inhibitory/excitatory currents on opposite sides of zero.

# A Closer Look
These are graphs I made when first trying to figure out if this method will be viable, and if so how to configure it. The code to generate these graphs is in this folder, but is often way more complicated than it needs to be just to generate this data. All color coding is the same (blue is quiet, red is noisy).

## Isolating Quiet Data
Here are two views (standard and logarithmic) of 10 ms segments of data color-coded by their *percentile* variance.

Linear Variance | Logarathmic Variance
---|---
![](2016-12-15-variance-1-logFalse.png)|![](2016-12-15-variance-1-logTrue.png)
![](2016-12-15-variance-2-logFalse.png)|![](2016-12-15-variance-2-logTrue.png)

## Creating a Baseline Noise Curve
I rely on matplotlib's [normal point distribution function (PDF)](http://matplotlib.org/api/mlab_api.html#matplotlib.mlab.normpdf) function to create my gaussian curve. There are many scipy options for this, but let's not force our end user to use scipy. Assume that we have a histogram created where `data` is the bin count and `Xs` are the bin values. `HIST_RESOLUTION` is the histogram bin size.
```python
sigma=np.sqrt(np.var(data))
mean=np.average(data)
curve=mlab.normpdf(Xs,mean,sigma)
```
If you normalize to 1 this doesn't matter, but if you want to preserve the vertical scale of the curve also add:
```
curve*=len(data)*HIST_RESOLUTION # correct vertical scale
```

## Percentile Range Histograms
I found that there's little change in the curve below 20% even in noisy data like mine. It seems like a simple enough number. My rule from now on is to ***use the quietest 20% of a sweep to calculate the noise floor histogram***.

Percentile Histograms | Distribution Curves
---|---
![](2016-12-15-percentile-histogram.png)|![](2016-12-15-percentile-fit.png)

Low Percentiles | Subtraction
---|---
![](2016-12-15-percentile-fitb.png)|![](2016-12-16-tryout.png)
