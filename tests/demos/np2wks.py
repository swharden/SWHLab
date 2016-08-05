import numpy as np
import swhlab.core.common as cm



### AUTOMATIC DEMO ###
# matrixToWks() gets column names, units, etc. from structured numpy array
APs=cm.matrixfromDicts(cm.dummyListOfDicts()) # fake AP data
cm.matrixToWks(APs,bookName="APs",sheetName="events",xCol='sweep')




### MAKE WORKSHEETS FROM DATA ###
# if you run from origin, it will make the worksheet.
# if you from from spyder, it will do something cool.

data=np.random.random_sample((20,3)) #generate some demo data

# pulls all info from structured numpy array
cm.matrixToWks(data,sheetName="simple")

# you can plot any 2d numpy array (even with missing values)
data[7,1]=np.nan # make some points missing
data[1,1]=np.nan # make some points missing
data[15,0]=np.nan # make some points missing
cm.matrixToWks(data,sheetName="missing")

# you can define column names and units
cm.matrixToWks(data,sheetName="fruity",names=["apples","oranges","pears"],units=["redness","roundness","pearness"])

# it can guess units of some things by their column name
cm.matrixToWks(data,sheetName="xCol",names=["Rm","brainNum","Ih"],xCol="brainNum")