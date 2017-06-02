"""
scripts to help automate data analysis and display.
this will eventually replace swh_index.

All output data should be named:
    * 12345678_experiment_thing.jpg (time course experiment, maybe with drug)
    * 12345678_intrinsic_thing.jpg (any intrinsic property)
    * 12345678_tif_thing.jpg (anything copied, likely a processed image)
    * 12345678_jpg_thing.jpg (anything copied, likely a micrograph)
    * 12345678_data_aps.npy (data stored in a numpy array)
    * 12345678_data_IVfast.npy (data stored in a numpy array)
"""

# start out this way so tests will import the local swhlab module

import os
import sys
if not os.path.abspath('../../../') in sys.path:
    sys.path.append('../../../')

sys.path.insert(0,os.path.abspath('../../'))
import swhlab
import time
# now import things regularly

import logging
import shutil
import numpy as np
import swhlab.analysis.protocols as protocols
import swhlab.indexing.imaging as imaging
import swhlab.indexing.style as style
import swhlab.common as cm

class INDEX:
    def __init__(self,ABFfolder):
        """
        The SWHLab INDEX class allows a web-browsable index of ABF data.

        This is intended to allow:
          * Automatic analysis of ABF files and output of data images
          * Watching of directories and automatic analysis of new ABFs
          * Manipulation and enhancement of micrographs (even multichannel)
          * creation of individual HTML pages for ABFs, cells, and folders

        General sequence:
          * convert folder1 TIFs to JPGs
          * analyze data for cells that need it
          * create their individual pages for cells that need it
          * create master index
        """
        logging.basicConfig(format=swhlab.logFormat, datefmt=swhlab.logDateFormat, level=swhlab.loglevel)
        self.log = logging.getLogger("swhlab INDEX")
        self.log.setLevel(swhlab.loglevel)
        if not type(ABFfolder) is str or not os.path.isdir(ABFfolder):
            self.log.error("PATH DOESNT EXIST [%s]",ABFfolder)
            return
        else:
            self.log.info("Indexing [%s] ...",ABFfolder)


        # determine file paths
        self.folder1=os.path.abspath(ABFfolder) # folder of ABF files
        self.folder2=os.path.abspath(ABFfolder+"/swhlab/") # web output folder
        if not os.path.isdir(self.folder2):
            self.log.debug("creating [%s]",self.folder2)
            os.mkdir(self.folder2)

        # scan the folders for files
        self.scan()

        # figure out parent/children ABF, ID, and file groups
        self.groups=cm.abfGroups(self.folder1) # keys are a list of parents
        self.log.debug("identified %d cells",len(self.groups))
        nChildren=[len(x) for x in self.groups.values()]
        self.log.debug("average parent has %.02f children",np.average(nChildren))
        self.groupFiles=cm.abfGroupFiles(self.groups,self.folder2)
        nChildrenFiles=[len(x) for x in self.groupFiles.values()]
        self.log.debug("average parent has %.02f ./swhlab/ files",np.average(nChildrenFiles))

    def scan(self):
        """
        scan folder1 and folder2 into files1 and files2.
        since we are on windows, simplify things by making them all lowercase.
        this WILL cause problems on 'nix operating systems.If this is the case,
        just run a script to rename every file to all lowercase.
        """
        t1=cm.timeit()
        self.files1=cm.list_to_lowercase(sorted(os.listdir(self.folder1)))
        self.files2=cm.list_to_lowercase(sorted(os.listdir(self.folder2)))
        self.files1abf=[x for x in self.files1 if x.endswith(".abf")]
        self.files1abf=cm.list_to_lowercase(cm.abfSort(self.files1abf))
        self.IDs=[x[:-4] for x in self.files1abf]
        self.log.debug("folder1 has %d files",len(self.files1))
        self.log.debug("folder1 has %d abfs",len(self.files1abf))
        self.log.debug("folder2 has %d files",len(self.files2))
        self.log.debug("scanning folders took %s",cm.timeit(t1)) # ~200ms

    ### DATA ANALYSIS AND CONVERSION

    def convertImages(self):
        """
        run this to turn all folder1 TIFs and JPGs into folder2 data.
        TIFs will be treated as micrographs and converted to JPG with enhanced
        contrast. JPGs will simply be copied over.
        """

        # copy over JPGs (and such)
        exts=['.jpg','.png']
        for fname in [x for x in self.files1 if cm.ext(x) in exts]:
            ID="UNKNOWN"
            if len(fname)>8 and fname[:8] in self.IDs:
                ID=fname[:8]
            fname2=ID+"_jpg_"+fname
            if not fname2 in self.files2:
                self.log.info("copying over [%s]"%fname2)
                shutil.copy(os.path.join(self.folder1,fname),os.path.join(self.folder2,fname2))
            if not fname[:8]+".abf" in self.files1:
                self.log.error("orphan image: %s",fname)

        # convert TIFs (and such) to JPGs
        exts=['.tif','.tiff']
        for fname in [x for x in self.files1 if cm.ext(x) in exts]:
            ID="UNKNOWN"
            if len(fname)>8 and fname[:8] in self.IDs:
                ID=fname[:8]
            fname2=ID+"_tif_"+fname+".jpg"
            if not fname2 in self.files2:
                self.log.info("converting micrograph [%s]"%fname2)
                imaging.TIF_to_jpg(os.path.join(self.folder1,fname),saveAs=os.path.join(self.folder2,fname2))
            if not fname[:8]+".abf" in self.files1:
                self.log.error("orphan image: %s",fname)

    def analyzeAll(self):
        """analyze every unanalyzed ABF in the folder."""
        searchableData=str(self.files2)
        self.log.debug("considering analysis for %d ABFs",len(self.IDs))
        for ID in self.IDs:
            if not ID+"_" in searchableData:
                self.log.debug("%s needs analysis",ID)
                try:
                    self.analyzeABF(ID)
                except:
                    print("EXCEPTION! "*100)
            else:
                self.log.debug("%s has existing analysis, not overwriting",ID)
        self.log.debug("verified analysis of %d ABFs",len(self.IDs))

    def analyzeABF(self,ID):
        """
        Analye a single ABF: make data, index it.
        If called directly, will delete all ID_data_ and recreate it.
        """
        for fname in self.files2:
            if fname.startswith(ID+"_data_"):
                self.log.debug("deleting [%s]",fname)
                os.remove(os.path.join(self.folder2,fname))
        self.log.info("analyzing (with overwrite) [%s]",ID)
        protocols.analyze(os.path.join(self.folder1,ID+".abf"))

    ### HTML GENERATION

    def htmlFor(self,fname):
        """return appropriate HTML determined by file extension."""
        if os.path.splitext(fname)[1].lower() in ['.jpg','.png']:
            html='<a href="%s"><img src="%s"></a>'%(fname,fname)
            if "_tif_" in fname:
                html=html.replace('<img ','<img class="datapic micrograph"')
            if "_plot_" in fname:
                html=html.replace('<img ','<img class="datapic intrinsic" ')
            if "_experiment_" in fname:
                html=html.replace('<img ','<img class="datapic experiment" ')
        elif os.path.splitext(fname)[1].lower() in ['.html','.htm']:
            html='LINK: %s'%fname
        else:
            html='<br>Not sure how to show: [%s]</br>'%fname
        return html

    def html_single_basic(self,abfID,launch=False,overwrite=False):
        """
        generate a generic flat file html for an ABF parent. You could give
        this a single ABF ID, its parent ID, or a list of ABF IDs.
        If a child ABF is given, the parent will automatically be used.
        """
        if type(abfID) is str:
            abfID=[abfID]
        for thisABFid in cm.abfSort(abfID):
            parentID=cm.parent(self.groups,thisABFid)
            saveAs=os.path.abspath("%s/%s_basic.html"%(self.folder2,parentID))
            if overwrite is False and os.path.basename(saveAs) in self.files2:
                continue
            filesByType=cm.filesByType(self.groupFiles[parentID])
            html=""
            html+='<div style="background-color: #DDDDDD;">'
            html+='<span class="title">summary of data from: %s</span></br>'%parentID
            html+='<code>%s</code>'%os.path.abspath(self.folder1+"/"+parentID+".abf")
            html+='</div>'
            catOrder=["experiment","plot","tif","other"]
            categories=cm.list_order_by(filesByType.keys(),catOrder)
            for category in [x for x in categories if len(filesByType[x])]:
                if category=='experiment':
                    html+="<h3>Experimental Data:</h3>"
                elif category=='plot':
                    html+="<h3>Intrinsic Properties:</h3>"
                elif category=='tif':
                    html+="<h3>Micrographs:</h3>"
                elif category=='other':
                    html+="<h3>Additional Files:</h3>"
                else:
                    html+="<h3>????:</h3>"
                #html+="<hr>"
                #html+='<br>'*3
                for fname in filesByType[category]:
                    html+=self.htmlFor(fname)
                html+='<br>'*3
            print("creating",saveAs,'...')
            style.save(html,saveAs,launch=launch)

    def html_single_plot(self,abfID,launch=False,overwrite=False):
        """create ID_plot.html of just intrinsic properties."""
        if type(abfID) is str:
            abfID=[abfID]
        for thisABFid in cm.abfSort(abfID):
            parentID=cm.parent(self.groups,thisABFid)
            saveAs=os.path.abspath("%s/%s_plot.html"%(self.folder2,parentID))
            if overwrite is False and os.path.basename(saveAs) in self.files2:
                continue
            filesByType=cm.filesByType(self.groupFiles[parentID])
            html=""
            html+='<div style="background-color: #DDDDFF;">'
            html+='<span class="title">intrinsic properties for: %s</span></br>'%parentID
            html+='<code>%s</code>'%os.path.abspath(self.folder1+"/"+parentID+".abf")
            html+='</div>'
            for fname in filesByType['plot']:
                html+=self.htmlFor(fname)
            print("creating",saveAs,'...')
            style.save(html,saveAs,launch=launch)


    def html_index(self,launch=True):
        html="<h1>MENU</h1>"
        htmlFiles=[x for x in self.files2 if x.endswith(".html")]
        for htmlFile in cm.abfSort(htmlFiles):
            if not htmlFile.endswith('_basic.html'):
                continue
            name=htmlFile.split("_")[0]
            if name in self.groups.keys():
                html+='<a href="%s" target="content">%s</a> '%(htmlFile,name)
                html+='<span style="color: #CCC;">'
                html+='[<a href="%s" target="content">int</a>]'%(name+"_plot.html")
                html+='</span>'
                html+='<br>'
        style.save(html,os.path.abspath(self.folder2+"/index_menu.html"))
        html="<h1>SPLASH</h1>"
        style.save(html,os.path.abspath(self.folder2+"/index_splash.html"))
        style.frames(os.path.abspath(self.folder2+"/index.html"),launch=launch)
        return

### TODO: streamline from here down #########################################

def doStuff(ABFfolder,analyze=False,convert=False,index=True,overwrite=True,
            launch=True):
    """Inelegant for now, but lets you manually analyze every ABF in a folder."""
    IN=INDEX(ABFfolder)
    if analyze:
        IN.analyzeAll()
    if convert:
        IN.convertImages()
#    if analyze or convert:
#        IN=INDEX(ABFfolder) # rescan needed

    #INDEXING IS DONE BY PHP NOW SO THIS ISN'T NEEDED
#    if index:
#        IN.scan() # scanning is slow, so don't do it often
#        IN.html_single_basic(IN.groups.keys(),overwrite=overwrite)
#        IN.html_single_plot(IN.groups.keys(),overwrite=overwrite)
#        IN.scan() # scanning is slow, so don't do it often
#        IN.html_index(launch=launch) # generate master

def analyzeSingle(abfFname):
    """Reanalyze data for a single ABF. Also remakes child and parent html."""
    assert os.path.exists(abfFname) and abfFname.endswith(".abf")
    ABFfolder,ABFfname=os.path.split(abfFname)
    abfID=os.path.splitext(ABFfname)[0]
    IN=INDEX(ABFfolder)
    IN.analyzeABF(abfID)
    IN.scan()
    IN.html_single_basic([abfID],overwrite=True)
    IN.html_single_plot([abfID],overwrite=True)
    IN.scan()
    IN.html_index()

    return

if __name__=="__main__":

    print(sys.argv)

    swhlab.loglevel=swhlab.loglevel_QUIET
    ABFfolder=None

    while True:

        for maybe in [
                      #r"X:\Data\SCOTT\2017-01-09 AT1 NTS",
#                      r"X:\Data\SCOTT\2017-05-15 LHA TGOT",
                      r"X:\Data\SCOTT\2017-04-24 aging BLA",
                      #r"X:\Data\SCOTT\2017-04-19 OT ChR2",
                      ]:
            if os.path.isdir(maybe):
                ABFfolder=maybe
        print("using ABF folder:",ABFfolder)

        doStuff(ABFfolder,analyze=True,convert=True,index=True,overwrite=True,launch=False)
        #doStuff(ABFfolder,analyze=True,convert=True,index=True,overwrite=True)
        for i in range(10):
            time.sleep(1)
            print("waiting",i)

    print("DONE")