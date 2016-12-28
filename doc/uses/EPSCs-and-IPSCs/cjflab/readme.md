## Unit Considerations
- assuming 20kHz each point is .05ms
- the phasic value of _each data point_ is ```pA * .05 ms```
- the phasic value of a _range of data_ is the the sum of all points values divided by the time span
 - getting ```sum(points)``` will still yield lots of pA * lots of ms
 - ```(lots of pA) * (lots of ms) / (total ms)```  leaves only pA

## Output as a function of Autobase Method
description | output
---|---
.1 pA bin, rolling SD autobase|~[](demo_sd.png)
.1 pA bin, gaussian LPF + gaussian autobase|~[](demo_point.png)
1.0 pA bin, gaussian LPF + gaussian autobase|~[](demo_whole.png)

## Unusual Data Points
- `X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d20028.abf`
 - unstable sweeps: 82, 83
 - unclamped AP: 143


## Typical Analysis 
```
setpath "X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d14036.abf";  getstats;
setpath "X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d14052.abf";  getstats; 
setpath "X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d16007.abf";  getstats; 
setpath "X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d16011.abf";  getstats; 
setpath "X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d20008.abf";  getstats; 
setpath "X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d20016.abf";  getstats; 
setpath "X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d20020.abf";  getstats;
setpath "X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d20024.abf";  getstats;
setpath "X:\Data\2P01\2016\2016-09-01 PIR TGOT\16d20028.abf";  getstats;

runonsheets _mStats "sc tagTime";
sc getcols _mStats Time PhasicNeg; sc onex; ccave; wks.name$ = PhasicNeg
sc getcols _mStats Time PhasicPos; sc onex; ccave; wks.name$ = PhasicPos
sc autoxy; ccave;
```
