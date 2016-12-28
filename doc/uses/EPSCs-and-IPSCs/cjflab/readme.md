## infinity data points
- `X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d20028.abf`
 - unstable? sweeps 82/83
 - unclamped AP: 143

## units
- assuming 20kHz each point is .05ms
- the phasic value of _each data point_ is ```pA * .05 ms```
- the phasic value of a _range of data_ is the the sum of all points values divided by the time span
 - ```sum(pA * ms) / ms``` (leaving only pA)
