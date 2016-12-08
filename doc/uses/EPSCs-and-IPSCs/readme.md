# Challenge
What is the best way to simultaneously quantify sEPSC and sIPSC influence from voltage-clamp recordings?

## Method 1: moving baseline derivative threshold detection
This method is used in [01.py](01.py)
* take a wide moving gaussian filter average of each trace and subtract it from the original data, centering the trace around 0pA.
* use a derivative method (dT of 2ms?) and capture all points which lie outside of a threshold (let's say 1 pA/ms)
* use the directionality of the derivative to define the "crossing" as an EPSC or IPSC

![](demo2.jpg) | ![](output.png)
--- | ---

## Method 2: moving baseline derivative threshold detection
This method is used in [02.py](02.py). In this demo, the drug (2 minutes of drug between the vertical red lines) increases upward events (IPSCs) and tips the balance from excitation to inhibition, then recovers. It may be over-simplistic to turn a distribution into a single point. I wonder if there's a better way. When one considers the shape of EPSCs and IPSCs, it becomes obvious that trying to fit a gaussian curve is not the best solution.

* take a wide moving gaussian filter average of each trace and subtract it from the original data, centering the trace around 0pA.
* create a 200-bin histogram of the points in the 2-second sweep and find its peak
 * if downward events dominate, the baseline average is pulled down, so the 0-centered line will "rest" slightly above 0pA. Therefore, the peak distribution will be slightly above 0pA, indicating net excitation. Call this value the 

baseline | drug
---|---
![](data-baseline-1.png) | ![](data-drug-1.png)
![](data-baseline-2.png) | ![](data-drug-2.png)
notice how the red line shifts _below_ 0pA | note how the red line shifts _above_ 0pA
![](distro.png)
