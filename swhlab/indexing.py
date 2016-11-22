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
import common as cm
import shutil
import swh_image
import protocols

import sys
sys.path.append("../") #TODO: MAKE THIS BETTER
import swhlab

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
            self.log.debug("Indexing [%s]",ABFfolder)
        
            
        # set up class variables
        self.folder1=os.path.abspath(ABFfolder) # folder of ABF files
        self.folder2=os.path.abspath(ABFfolder+"/swhlab/") # web output folder
        if not os.path.isdir(self.folder2):
            self.log.debug("creating [%s]",self.folder2)
            os.mkdir(self.folder2)
            
        # scan the folders
        self.scan()
            
    def scan(self):
        """
        scan folder1 and folder2 into files1 and files2.
        since we are on windows, simplify things by making them all lowercase.
        this WILL cause problems on 'nix operating systems.If this is the case,
        just run a script to rename every file to all lowercase.
        """
        self.files1=cm.list_to_lowercase(sorted(os.listdir(self.folder1)))
        self.files2=cm.list_to_lowercase(sorted(os.listdir(self.folder2)))
        self.files1abf=[x for x in self.files1 if x.endswith(".abf")]
        self.files1abf=cm.list_to_lowercase(cm.abfSort(self.files1abf))
        self.IDs=[x[:-4] for x in self.files1abf]
        self.log.debug("folder1 has %d files",len(self.files1))
        self.log.debug("folder1 has %d abfs",len(self.files1abf))
        self.log.debug("folder2 has %d files",len(self.files2))

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
                swh_image.TIF_to_jpg(os.path.join(self.folder1,fname),saveAs=os.path.join(self.folder2,fname2))
            if not fname[:8]+".abf" in self.files1:
                self.log.error("orphan image: %s",fname)
                
    def analyzeAll(self):
        """analyze every unanalyzed ABF in the folder."""
        searchableData=str(self.files2)
        for ID in self.IDs:
            if not ID+"_data_" in searchableData:
                self.log.debug("%s needs analysis",ID)
                self.analyzeABF(ID)
                #print("BREAKING EARLY.")
                #return
            else:
                self.log.debug("%s has existing analysis, not overwriting",ID)
        return
            
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
        
if __name__=="__main__":
    swhlab.loglevel=swhlab.loglevel_DEBUG
    ABFfolder=None
    for maybe in [r"X:\Data\2P01\2016\2016-09-01 PIR TGOT"]:
        if os.path.isdir(maybe):
            ABFfolder=maybe    
            
    # PROGRAM STARTS HERE
    IN=INDEX(ABFfolder)
    #IN.analyzeABF('16831003')
    IN.analyzeAll()    
    #IN.convertImages()