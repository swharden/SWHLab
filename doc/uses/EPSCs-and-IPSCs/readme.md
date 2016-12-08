# Challenge
What is the best way to simultaneously quantify sEPSC and sIPSC influence from voltage-clamp recordings?

## Method 1: moving baseline derivative threshold detection
* take a wide moving gaussian filter average of each trace and subtract it from the original data, centering the trace around 0pA.
* use a derivative method (dT of 2ms?) and capture all points which lie outside of a threshold (let's say 1 pA/ms)
* use the directionality of the derivative to define the "crossing" as an EPSC or IPSC

![](EPSCs-and-IPSCs/demo2.jpg) | ![](EPSCs-and-IPSCs/output.png)
--- | ---

## Method 2: moving baseline derivative threshold detection
