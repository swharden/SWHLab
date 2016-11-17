"""
Operations to help with images (usually micrographs) This module does things 
like add scale bars, and help with multichannel representation and analysis.
"""

import os
import numpy as np
from scipy import ndimage
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from . import common

def convert(fname,saveAs=True,showToo=False):
    """
    Convert weird TIF files into web-friendly versions.
    Auto contrast is applied (saturating lower and upper 0.1%).
        make saveAs True to save as .TIF.png
        make saveAs False and it won't save at all
        make saveAs "someFile.jpg" to save it as a different path/format
    """

    # load the image
    #im = Image.open(fname) #PIL can't handle 12-bit TIFs well
    im=ndimage.imread(fname) #scipy does better with it
    im=np.array(im,dtype=float) # now it's a numpy array

    # do all image enhancement here
    cutoffLow=np.percentile(im,.01)
    cutoffHigh=np.percentile(im,99.99)
    im[np.where(im<cutoffLow)]=cutoffLow
    im[np.where(im>cutoffHigh)]=cutoffHigh

    # IMAGE FORMATTING
    im-=np.min(im) #auto contrast
    im/=np.max(im) #normalize
    im*=255 #stretch contrast (8-bit)
    im = Image.fromarray(im)

    # IMAGE DRAWING
    msg="%s\n"%os.path.basename(fname)
    msg+="%s\n"%common.epochToString(os.path.getmtime(fname))
    d = ImageDraw.Draw(im)
    fnt = ImageFont.truetype("arial.ttf", 20)
    d.text((6,6),msg,font=fnt,fill=0)
    d.text((4,4),msg,font=fnt,fill=255)

    if showToo:
        im.show()
    if saveAs is False:
        return
    if saveAs is True:
        saveAs=fname+".png"
    im.convert('RGB').save(saveAs)
    return saveAs

if __name__=="__main__":
    print("DONT RUN THIS.")