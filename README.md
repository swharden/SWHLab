# SWHLab
SWHLab is a python module intended to provide easy access to high level ABF file opeartions to aid analysis of whole-cell patch-clamp electrophysiological recordings. Although graphs can be interactive, the default mode is to output PNGs and generate flat file HTML indexes to allow data browsing through any browser on the network. Direct ABF access was provided by the  [NeoIO](https://pythonhosted.org/neo/io.html) module. _This is a collection of scripts I use for work, and is not intended to be run by anyone other than the author. Source is available for educational purposes only._

## More Resources
A hodgepodge collection of information is on the temporary website:
* http://swhlab.swharden.com

## SWHLab and CJFLab
CJFLab is an electrophysiology analysis suite for OriginLab written by Charles Jason Frazier. For more information, see the [github project for CJFLab] (https://github.com/swharden/CJFLab). Many of the scripts in this module depend on functions only available through CJFLab.

## Example Output
![screenshot](screenshots/screenshot1.jpg)
![screenshot](screenshots/screenshot2.jpg)
![screenshot](screenshots/screenshot3.jpg)
![screenshot](screenshots/screenshot4.png)
![screenshot](screenshots/screenshot5.png)

Either use the update commands from within origin (`sc update`) or update via github desktop client. Don't do both, or the github desktop client will get confused!

## Developer notes 
If you're not one of the primary authors of this softare, you can ignore this.

### setting up a new system
* absoulte file paths are required for now. Work only in C:\Apps\pythonModules\
* create an EMPTY directory all lowercase: C:\Apps\pythonModules\swhlab
* on the [main github page](https://github.com/swharden/SWHLab), clone this project using the desktop project
* when asked where to save it, set it to C:\Apps\pythonModules\ (NOT the swhlab folder!)

### making changes to the project
* it is recommended that you periodically use the 'sync' button of the desktop client to keep your code current
* when you've made changes you wish to commit, add a brief note as to what you've done, click commit, and you MUST click sync again
