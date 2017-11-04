"""
Minimal-case pure-python ABF file reader by Scott Harden.

PURPOSE:
    This script is a demonstration of how to use native python 3 (stock libraries) to read header and data
    out of an Axon Binary Format (ABF) version 2 (ABF2) file created with ClampEx 10 / ClampFit 10.
    This is developed and tested only for episodic files.
    
DETAILS:
    After reviewing the python-neo project carefully, I essentially mimiced their implimentation with added
    emphasis on simplicity. Only ABF2 is supported here. Unlike Neo which intends to fit Axon files into
    their feature-rich pythonic object model, here I am trying to minimize complexity.
    
ADDITIONAL INFORMATION:
    https://github.com/NeuralEnsemble/python-neo/blob/master/neo/rawio/axonrawio.py
    http://www.mathworks.com/matlabcentral/fileexchange/22114-abf2load
    http://www.moleculardevices.com/pages/software/developer_info.html
    
    
"""
import os
import glob
import struct
import datetime

# memory-mapped variables arranged by blocked. This is a blend of custom work (swharden) and previous libraries.
EpochSectionDescription=[('nEpochNum','h'),('nEpochDigitalOutput','h'),('sUnused','28s')]
EpochInfoPerDACDescription=[('nEpochNum','h'),('nDACNum','h'),('nEpochType','h'),('fEpochInitLevel','f'),
('fEpochLevelInc','f'),('lEpochInitDuration','i'),('lEpochDurationInc','i'),('lEpochPulsePeriod','i'),
('lEpochPulseWidth','i'),('sUnused','18s'),]
DACInfoDescription=[('nDACNum','h'),('nTelegraphDACScaleFactorEnable','h'),('fInstrumentHoldingLevel','f'),
('fDACScaleFactor','f'),('fDACHoldingLevel','f'),('fDACCalibrationFactor','f'),('fDACCalibrationOffset','f'),
('lDACChannelNameIndex','i'),('lDACChannelUnitsIndex','i'),('lDACFilePtr','i'),('lDACFileNumEpisodes','i'),
('nWaveformEnable','h'),('nWaveformSource','h'),('nInterEpisodeLevel','h'),('fDACFileScale','f'),
('fDACFileOffset','f'),('lDACFileEpisodeNum','i'),('nDACFileADCNum','h'),('nConditEnable','h'),
('lConditNumPulses','i'),('fBaselineDuration','f'),('fBaselineLevel','f'),('fStepDuration','f'),
('fStepLevel','f'),('fPostTrainPeriod','f'),('fPostTrainLevel','f'),('nMembTestEnable','h'),
('nLeakSubtractType','h'),('nPNPolarity','h'),('fPNHoldingLevel','f'),('nPNNumADCChannels','h'),
('nPNPosition','h'),('nPNNumPulses','h'),('fPNSettlingTime','f'),('fPNInterpulse','f'),('nLTPUsageOfDAC','h'),
('nLTPPresynapticPulses','h'),('lDACFilePathIndex','i'),('fMembTestPreSettlingTimeMS','f'),
('fMembTestPostSettlingTimeMS','f'),('nLeakSubtractADCIndex','h'),('sUnused','124s'),]
TagInfoDescription=[('lTagTime','i'),('sComment','56s'),('nTagType','h'),('nVoiceTagNumber_or_AnnotationIndex','h')]
protocolInfoDescription=[('nOperationMode','h'),('fADCSequenceInterval','f'),('bEnableFileCompression','b'),
('sUnused','3s'),('uFileCompressionRatio','I'),('fSynchTimeUnit','f'),('fSecondsPerRun','f'),
('lNumSamplesPerEpisode','i'),('lPreTriggerSamples','i'),('lEpisodesPerRun','i'),('lRunsPerTrial','i'),
('lNumberOfTrials','i'),('nAveragingMode','h'),('nUndoRunCount','h'),('nFirstEpisodeInRun','h'),
('fTriggerThreshold','f'),('nTriggerSource','h'),('nTriggerAction','h'),('nTriggerPolarity','h'),
('fScopeOutputInterval','f'),('fEpisodeStartToStart','f'),('fRunStartToStart','f'),('lAverageCount','i'),
('fTrialStartToStart','f'),('nAutoTriggerStrategy','h'),('fFirstRunDelayS','f'),('nChannelStatsStrategy','h'),
('lSamplesPerTrace','i'),('lStartDisplayNum','i'),('lFinishDisplayNum','i'),('nShowPNRawData','h'),
('fStatisticsPeriod','f'),('lStatisticsMeasurements','i'),('nStatisticsSaveStrategy','h'),('fADCRange','f'),
('fDACRange','f'),('lADCResolution','i'),('lDACResolution','i'),('nExperimentType','h'),
('nManualInfoStrategy','h'),('nCommentsEnable','h'),('lFileCommentIndex','i'),('nAutoAnalyseEnable','h'),
('nSignalType','h'),('nDigitalEnable','h'),('nActiveDACChannel','h'),('nDigitalHolding','h'),
('nDigitalInterEpisode','h'),('nDigitalDACChannel','h'),('nDigitalTrainActiveLogic','h'),('nStatsEnable','h'),
('nStatisticsClearStrategy','h'),('nLevelHysteresis','h'),('lTimeHysteresis','i'),('nAllowExternalTags','h'),
('nAverageAlgorithm','h'),('fAverageWeighting','f'),('nUndoPromptStrategy','h'),('nTrialTriggerSource','h'),
('nStatisticsDisplayStrategy','h'),('nExternalTagType','h'),('nScopeTriggerOut','h'),('nLTPType','h'),
('nAlternateDACOutputState','h'),('nAlternateDigitalOutputState','h'),('fCellID','3f'),('nDigitizerADCs','h'),
('nDigitizerDACs','h'),('nDigitizerTotalDigitalOuts','h'),('nDigitizerSynchDigitalOuts','h'),('nDigitizerType','h')]
ADCInfoDescription=[('nADCNum','h'),('nTelegraphEnable','h'),('nTelegraphInstrument','h'),
('fTelegraphAdditGain','f'),('fTelegraphFilter','f'),('fTelegraphMembraneCap','f'),('nTelegraphMode','h'),
('fTelegraphAccessResistance','f'),('nADCPtoLChannelMap','h'),('nADCSamplingSeq','h'),('fADCProgrammableGain','f'),
('fADCDisplayAmplification','f'),('fADCDisplayOffset','f'),('fInstrumentScaleFactor','f'),('fInstrumentOffset','f'),
('fSignalGain','f'),('fSignalOffset','f'),('fSignalLowpassFilter','f'),('fSignalHighpassFilter','f'),
('nLowpassFilterType','b'),('nHighpassFilterType','b'),('fPostProcessLowpassFilter','f'),
('nPostProcessLowpassFilterType','c'),('bEnabledDuringPN','b'),('nStatsChannelPolarity','h'),
('lADCChannelNameIndex','i'),('lADCUnitsIndex','i'),]
sectionNames=['ProtocolSection','ADCSection','DACSection','EpochSection','ADCPerDACSection','EpochPerDACSection',
'UserListSection','StatsRegionSection','MathSection','StringsSection','DataSection','TagSection','ScopeSection',
'DeltaSection','VoiceTagSection','SynchArraySection','AnnotationSection','StatsSection',]
headerDescriptionV2=[('fFileSignature',0,'4s'),('fFileVersionNumber',4,'4b'),('uFileInfoSize',8,'I'),
('lActualEpisodes',12,'I'),('uFileStartDate',16,'I'),('uFileStartTimeMS',20,'I'),('uStopwatchTime',24,'I'),
('nFileType',28,'H'),('nDataFormat',30,'H'),('nSimultaneousScan',32,'H'),('nCRCEnable',34,'H'),('uFileCRC',36,'I'),
('FileGUID',40,'I'),('uCreatorVersion',56,'I'),('uCreatorNameIndex',60,'I'),('uModifierVersion',64,'I'),
('uModifierNameIndex',68,'I'),('uProtocolPathIndex',72,'I'),]
BLOCKSIZE = 512

def fread(f,byteLocation,structFormat=None,nBytes=1):
    """
    Given an already-open (rb mode) file object, return a certain number of bytes at a specific location.
    If a struct format is given, calculate the number of bytes required and return the object it represents.
    """
    f.seek(byteLocation)
    if structFormat:
        val = struct.unpack(structFormat, f.read(struct.calcsize(structFormat)))
        val = val[0] if len(val)==1 else list(val)
        return val
    else:
        return f.read(nBytes)

def abf_read_header(fname, saveHeader=True):
    """
    Practice pulling data straight out of an ABF's binary header. Support only ABF2 (ClampEx an ClampFit 10).
    Use only native python libraries. Strive for simplicity and readability (to promote language portability).
    This was made by Scott Harden after a line-by-line analysis of axonrawio.py from the neo io library.
    Unlike NeoIO's format, I'm going to try to prevent nested dictionaries to keep things simple.
    """
    
    ### THESE OBJETS WILL BE FULL WHEN THIS FUNCTION IS COMPLETE
    header={} # information about the file format
    sections={} # contains byte positions (and block sizes) for header information
    strings=[] # a list of strings stored in the ABF header (protocol file, abf comment, and channel labels / units)
    protocol = {} # info about the ABF recording
    tags=[] # timed comments made during the abf as a list of lists [pos,comment,tagtype,voice]
    adcs=[] # ADC info as a list of dicts
    dacs=[] # DAC info as a list of dicts
    digitalOutputs=[] # one 0b00000000 code per epoch
    config={} # a concise collection of ABF info I think is useful. I intend only to return this object.
    
    ### READ THE FIRST PART OF THE FILE INTO MEMORY
    # TODO: figure out the most memory-effecient way to do this
    f=open(fname,'rb')
    config["abf_filename"]=os.path.abspath(fname) # full path to the abf file on disk
    config["abf_ID"]=os.path.basename(fname)[:-4] # abf filename without the ".abf"
    
    ### DECODE HEADER - this tells basic information about the file format
    for key, byte_location, fmt in headerDescriptionV2:
        header[key]=fread(f,byte_location,fmt)
    header['fFileSignature']=header['fFileSignature'].decode()
    
    ### DECODE SECTIONS - sections are where (byte location) in this file different data is stored
    for sectionNumber, sectionName in enumerate(sectionNames):
        uBlockIndex, uBytes, llNumEntries = fread(f,76+sectionNumber*16,"IIl")
        sections[sectionName] = [uBlockIndex,uBytes,llNumEntries]
    config["abf_sweep_start_time"]=header['uFileStartTimeMS']/1000/1000
          
    ### DECODE STRINGS - figure out where (byte location) strings are in this file
    # There are 20 strings. Protocol path, ABF comment, then alternating channel name and units.
    byte_location = sections['StringsSection'][0]*BLOCKSIZE
    string_size = sections['StringsSection'][1]
    strings_data = fread(f,byte_location,structFormat=None,nBytes=string_size)
    for key in [b'AXENGN', b'clampex', b'Clampex', b'CLAMPEX', b'axoscope']:
        if key in strings_data:
            for line in strings_data.split(key)[1].split(b'\x00')[1:-1]:
                strings.append(line.decode())
            config["abf_protocol_file"]=strings[0]
            config["abf_comment"]=strings[1]
            config["abf_channels"]=strings[2::2]
            config["abf_units"]=strings[3::2]
            break
        
    ### DECODE ADC INFO - a list of dictionaries, one per ADC employed
    for ADCsection in range(sections['ADCSection'][2]):
        thisADC={}
        byte_location=sections['ADCSection'][0]*BLOCKSIZE+sections['ADCSection'][1]*ADCsection
        for key, fmt in ADCInfoDescription:
            thisADC[key]=fread(f,byte_location,fmt)
            byte_location+=struct.calcsize(fmt)
        adcs.append(thisADC)
        
    ### PROTOCOL - info about the nature of the recording
    byte_location=sections['ProtocolSection'][0]*BLOCKSIZE
    for key, fmt in protocolInfoDescription:
        protocol[key]=fread(f,byte_location,fmt)
        byte_location+=struct.calcsize(fmt)
    protocol.pop('sUnused', None) # we don't need this
        
    ### TAGS (COMMMENTS) - those with a timestamp/comment (not those embedded in the protocol)
    #TODO: not sure what the tagtime units actually are. Byte positions? Block number?
    byte_location=sections['TagSection'][0]*BLOCKSIZE
    for i in range(sections['TagSection'][2]):
        thisTag=[]
        for key, fmt in TagInfoDescription:
            val=fread(f,byte_location,fmt)
            if type(val) is bytes:
                val=val.decode().strip()
            thisTag.append(val)
            byte_location+=struct.calcsize(fmt)
        tags.append(thisTag)
        
    ### DAC SECTIONS    
    for dacNumber in range(sections['DACSection'][2]):
        thisDAC={}
        byte_location=sections['DACSection'][0]*BLOCKSIZE+sections['DACSection'][1]*dacNumber                              
        for key, fmt in DACInfoDescription:
            thisDAC[key]=fread(f,byte_location,fmt)
            byte_location+=struct.calcsize(fmt)
        thisDAC.pop('sUnused', None) # we don't need this
        if thisDAC['nWaveformEnable']==0: continue # don't record unused DACs
        dacs.append(thisDAC)
        
    ### EPOCHS PER DAC - this is what appear on the waveform tab
    epochs=[]
    for epochNumber in range(sections['EpochPerDACSection'][2]):
        thisEpoch={}
        byte_location=sections['EpochPerDACSection'][0]*BLOCKSIZE+sections['EpochPerDACSection'][1]*epochNumber
        for key, fmt in EpochInfoPerDACDescription:
            thisEpoch[key]=fread(f,byte_location,fmt)
            byte_location+=struct.calcsize(fmt)
        thisEpoch.pop('sUnused', None) # we don't need this
        epochs.append(thisEpoch)
    
    ### DIGITAL OUTPUTS - this is where digital outputs are stored. Returns binary string (7-0)
    # this does not exist in Neo IO. It was hacked-in by Scott Harden (github: swharden) to capture digital outputs.
    # let's just add the digital output string to the epochs array we already have started.
    byte_location=sections['EpochSection'][0]*BLOCKSIZE
    for epochNumber in range(sections['EpochSection'][0]):
        if epochNumber>=len(epochs):
            break # don't bother looking up unused epochs
        thisEpoch=epochs[epochNumber]
        for key, fmt in EpochSectionDescription:
            val=fread(f,byte_location,fmt)
            if key=='nEpochDigitalOutput':
                val=format(val, 'b').rjust(8,'0') # convert to a binary string (7->0)
            thisEpoch[key]=val
            byte_location+=struct.calcsize(fmt)
        thisEpoch.pop('sUnused', None) # we don't need this
        epochs[epochNumber]=thisEpoch
        
    ### WE ARE DONE READING THE FILE
    f.close()
    
    ### EXTRA CONFIG - cherry-pick just what I find useful and arrange it in a simple dictionary
    config["abfVersion"]=float("".join([str(x) for x in header['fFileVersionNumber']]))/100 # now a float
    config['signalNames']=config['abf_channels'][:len(adcs)] # don't need more than the number of channels
    config['signalUnits']=config['abf_units'][:len(adcs)] # don't need more than the number of channels
    config['comments']=[x[:2] for x in tags]
    config['nSweeps']=sections['SynchArraySection'][2]
    
    # Determine the recording date from the header   
    YY = int(header['uFileStartDate'] / 10000)
    MM = int((header['uFileStartDate'] - YY * 10000) / 100)
    DD = int(header['uFileStartDate'] - YY * 10000 - MM * 100)
    hh = int(header['uFileStartTimeMS'] / 1000. / 3600.)
    mm = int((header['uFileStartTimeMS'] / 1000. - hh * 3600) / 60)
    ss = header['uFileStartTimeMS'] / 1000. - hh * 3600 - mm * 60
    ms = int((ss%1)*1e6)
    ss = int(ss)
    config['abf_datetime'] = datetime.datetime(YY, MM, DD, hh, mm, ss, ms) 
