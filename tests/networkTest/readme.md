# X-Drive Stress Test
This script will stress the X-Drive in two ways:
* copying a 500MB file to the local computer
* manually seaching every folder in a large tree
Each will be done 5 times and the result averaged.

## Demo Output
```
walking the entire tree of: X:\Data\DIC2\2014
(1/5) scanned 976 folders in 15.236 seconds
(2/5) scanned 976 folders in 8.413 seconds
(3/5) scanned 976 folders in 7.390 seconds
(4/5) scanned 976 folders in 6.735 seconds
(5/5) scanned 976 folders in 7.904 seconds
Average time for 5 runs: 9.136 seconds

copying a HUGE file: X:\...\2017-05-11 cell3_annotated.tif
(1/5) copy took 25.438 seconds (17.260 MB/s)
(2/5) copy took 27.470 seconds (15.983 MB/s)
(3/5) copy took 25.859 seconds (16.978 MB/s)
(4/5) copy took 26.391 seconds (16.637 MB/s)
(5/5) copy took 26.455 seconds (16.596 MB/s)
Average time for 5 runs: 26.322 seconds
```