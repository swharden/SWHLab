"""
Things related to documentation generation.
"""

import os
import sys
#sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import imp
import pydoc
import glob
import swhlab
import swhlab.core.common as cm

def gendocs(subpath='core'):
    for fname in glob.glob(swhlab.LOCALPATH+"/%s/*.py"%subpath):
        name=os.path.basename(fname).split(".")[0]
        try:
            thing=imp.load_source(name, fname)
        except:
            print("!!! CRASHED ON IMPORT !!")
            return
        pydoc.writedoc(thing)
    for fname in glob.glob("*.html"):
        if fname.startswith("swhlab."):
            continue
        root,name=os.path.split(fname)
        fname2=os.path.join(root,"swhlab.%s."%subpath+name)
        os.rename(fname,fname2)
        print("converted to",fname2)

def docIndex():
    html='<html><body><h1>SWHLab4 Code Documentation</h1><code><ul>'
    for fname in sorted(glob.glob("*.html")):
        name=os.path.basename(fname).replace(".html",'')
        link=os.path.basename(fname)
        html+='<li><h3><a href="%s">%s</a></h3>'%(link,name)
    html+='</ul></code></body></html>'
    f=open('index.html','w')
    f.write(html)
    f.close()

if __name__=="__main__":
    os.chdir(swhlab.LOCALPATH+"/doc/pydoc/")
    for fname in glob.glob("*.html"):
        os.remove(fname)
    gendocs('core')
    gendocs('indexing')
    gendocs('tests')
    gendocs('origin')
    docIndex()
    print("documentation generation complete.")
    try:
        ftp=cm.ftp_login('/swhlab/docs/module/')
        for fname in glob.glob("*.html"):
            cm.ftp_upload(ftp,fname,os.path.basename(fname))
        ftp.quit()
        print("docs uploaded successfully.")
    except:
        print("docs were not uploaded.")