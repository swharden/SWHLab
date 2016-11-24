"""
Operations to help with images (usually micrographs) This module does things 
like add scale bars, and help with multichannel representation and analysis.
"""
# start out this way so tests will import the local swhlab module
import sys
import os
sys.path.insert(0,os.path.abspath('../../'))
import swhlab

# now import things regularly
import numpy as np
import pylab
import datetime
import glob

def TIF_to_jpg(fnameTiff, overwrite=False, saveAs=""):
    """
    given a TIF taken by our cameras, make it a pretty labeled JPG.

    if the filename contains "f10" or "f20", add appropraite scale bars.

    automatic contrast adjustment is different depending on if its a DIC
    image or fluorescent image (which is detected automatically).
    """
    
    if saveAs == "":
        saveAs=fnameTiff+".jpg"

    if overwrite is False and os.path.exists(saveAs):
        print("file exists, not overwriting...")
        return

    # load the image
    img=pylab.imread(fnameTiff)
    img=img/np.max(img) # now the data is from 0 to 1

    # determine the old histogram
    hist1,bins1=np.histogram(img.ravel(),bins=256, range=(0,1))
    #pylab.plot(bins[:-1],hist)

    # detect darkfield by average:
    if np.average(img)<.2:
        vmin=None
        vmax=None
        msg=" | FLU"
        while np.average(img)<.5:
            img=np.sqrt(img)
            msg+="^(.5)"
    else:
        msg=" | DIC"
        percentile=.005
        vmin=np.percentile(img.ravel(),percentile)
        vmax=np.percentile(img.ravel(),100-percentile)


    # determine the new histogram
    hist2,bins2=np.histogram(img.ravel(),bins=256, range=(0,1))

    # plot it with resizing magic
    fig=pylab.figure(facecolor='r')
    fig.gca().imshow(img,cmap=pylab.gray(),vmin=vmin,vmax=vmax)
    pylab.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    pylab.gca().xaxis.set_major_locator(pylab.NullLocator())
    pylab.gca().yaxis.set_major_locator(pylab.NullLocator())
    pylab.axis('off')

    # resize it to the original size
    fig.set_size_inches(img.shape[1]/100, img.shape[0]/100)

    # add text
    msg="%s | %s"%(os.path.basename(fnameTiff),
         datetime.datetime.fromtimestamp(os.path.getmtime(fnameTiff)))+msg
    center=10
    pylab.text(center,center,"%s"%(msg),va="top",color='w',size='small',
               family='monospace',weight='bold',
               bbox=dict(facecolor='k', alpha=.5))

    # add scale bar
    scaleWidthPx=False
    if "f10" in fnameTiff:
        scaleWidthPx,scaleBarText=39,"25 um"
    if "f20" in fnameTiff:
        scaleWidthPx,scaleBarText=31,"10 um"
    if scaleWidthPx:
        scaleBarPadding=10
        x2,y2=img.shape[1]-scaleBarPadding,img.shape[0]-scaleBarPadding
        x1,y1=x2-scaleWidthPx,y2
        for offset,color,alpha in [[2,'k',.5],[0,'w',1]]:
            pylab.plot([x1+offset,x2+offset],[y1+offset,y2+offset],'-',
                       color=color,lw=4,alpha=alpha)
            pylab.text((x1+x2)/2+offset,y1-5+offset,scaleBarText,color=color,
                       ha="center",weight="bold",alpha=alpha,
                       size="small",va="bottom",family="monospace")

    # add histogram
    #pylab.plot(img.shape[1]-bins1[:-1][::-1]*200,-hist1/max(hist1)*100+110,color='g')
    #pylab.plot(img.shape[1]-bins2[:-1][::-1]*200,-hist2/max(hist2)*100+110,color='b')
    #pylab.show()

    # save it
    pylab.savefig(saveAs,dpi=100)

    # clean up
    pylab.close()

def TIF_to_jpg_all(path):
    """run TIF_to_jpg() on every TIF of a folder."""
    for fname in sorted(glob.glob(path+"/*.tif")):
        print(fname)
        TIF_to_jpg(fname)

if __name__=="__main__":
    print("DONT RUN THIS.")