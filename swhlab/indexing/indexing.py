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

import os
import logging
import shutil
import numpy as np
import sys

try:
    import swhlab
except:
    sys.path.append("../../")
    import swhlab
import swhlab.analysis.protocols as protocols
import imaging
import swhlab.common as cm
import style

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
            if not ID+"_data_" in searchableData:
                self.log.debug("%s needs analysis",ID)
                self.analyzeABF(ID)
                #print("BREAKING EARLY.")
                #return
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
                html=html.replace('<img ','<img height="400" ')
            if "_plot_" in fname:
                html=html.replace('<img ','<img height="200" ')
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
            if overwrite is False and parentID+"_basic.html" in self.files2:
                #print("skipping",parentID)
                continue
            filesByType=cm.filesByType(self.groupFiles[parentID])
            html="<h1>%s</h1>"%parentID
            for category in [x for x in filesByType.keys() if len(filesByType[x])]:
                html+="<h3>%s</h3>"%category
                for fname in filesByType[category]:
                    html+=self.htmlFor(fname)
            saveAs=os.path.abspath("%s/%s_basic.html"%(self.folder2,parentID))
            print("creating",saveAs,'...')
            style.save(html,saveAs,launch=launch)
            
    def html_index(self):
        html="<h1>MENU</h1>"
        for htmlFile in [x for x in self.files2 if x.endswith(".html")]:
            if not "_" in htmlFile:
                continue
            name=htmlFile.split("_")[0]
            if name in self.groups.keys():
                html+='<a href="%s" target="content">%s</a><br>'%(htmlFile,name)
        style.save(html,os.path.abspath(self.folder2+"/index_menu.html"))
        html="<h1>SPLASH</h1>"
        style.save(html,os.path.abspath(self.folder2+"/index_splash.html"))
        style.frames(os.path.abspath(self.folder2+"/index.html"),launch=True)
        return

def doStuff(ABFfolder,analyze=False,convert=False,index=True,overwrite=True):
    IN=INDEX(ABFfolder)
    if analyze:
        IN.analyzeAll()    
    if convert:
        IN.convertImages()
    if index:
        IN.scan() # scanning is slow, so don't do it often
        IN.html_single_basic(IN.groups.keys(),overwrite=overwrite)
        IN.html_index() # generate master
    
            
if __name__=="__main__":
    swhlab.loglevel=swhlab.loglevel_QUIET
    ABFfolder=None
    for maybe in [
                  r"X:\Data\2P01\2016\2016-09-01 PIR TGOT",
                  r"C:\Users\scott\Documents\important\abfs",
                  ]:
        if os.path.isdir(maybe):
            ABFfolder=maybe    
    print("using ABF folder:",ABFfolder)
    
    doStuff(ABFfolder,
            analyze=False,
            convert=False,
            index=True,
            overwrite=True)
    
    
#    IN.analyzeABF('16o14022')
#    IN.html_single_basic('16o14022')

    print("DONE")