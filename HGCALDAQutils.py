import random
import json
import dill
import pickle
import numpy as np

#########################################################
# a random flat trowing tool
def isThereL1A(probability):
    if probability > 1:
        print("isThereL1A: probability set to", probability)
        raise ValueError('isThereL1A: You cannot have L1 tirgger probability larger than 1 ! ')
    return random.random() < probability





#########################################################
# class to handle the LHC bunch structure:
#                                           load beam1/2 filled bunches
#                                           return presence/absence of a bunch corssing, as a function of bucket-in-orbit-ID
class lhcOrbitStructure:
    """
    class to handle the LHC bunch structure:
    """
    beamOne                = []
    beamTwo                = []
    numverOfBuckets        = 0
    typicalNumverOfBuckets = 3564
    bunchCrossing   = []

    def __init__(self,theFile=''):
        print('creating lhcOrbitStructure')
        print('the LHC beam struacture file: %s'%theFile)
        if not theFile: print('(since empty, the beam structure will be set to 3564 full buckets for both beams (irrealistic)')

        # load the beam1 and beam2 filling schema: a flat "all buckets have a bunch" (irrealistic)
        # or a specific configuration from file
        if not theFile:
            # if not file is pecified, put a bunch in each (of typicalNumverOfBuckets) bucket
            self.beamOne = [1]*self.typicalNumverOfBuckets
            self.beamTwo = [1]*self.typicalNumverOfBuckets
        else:
            with open( theFile ) as json_file:
                theDic = json.load(json_file)
                self.beamOne =  theDic['beam1']
                self.beamTwo =  theDic['beam2']

        # basic consistency checks on the loaded filling schema for beam1 and beam2
        if len(self.beamOne) != len(self.beamTwo):
            raise ValueError('lhcOrbitStructure:\
            loaded beamOne and beamTwo have different size, which cannot be. ')
        if len(self.beamOne) != self.typicalNumverOfBuckets:
            print('\t *** loaded number of buckets %d differs\
            from the LHC standard value %d'%(len(self.beamOne),self.typicalNumverOfBuckets) )

        self.numverOfBuckets = len(self.beamOne)

        # if there's a bunch in each bucket, you have a collision (bunchCrossing==1), otherwise not ( ==0)
        self.bunchCrossing =   [one*two for one,two in zip(self.beamOne,self.beamTwo) ]


    def numberBuckets(self):
        return self.numverOfBuckets

    def numberBucketsWithBunchXing(self):
        return self.bunchCrossing.count(1)

    def isThereBunchCrossing(self,bucketNumber=0):
        return self.bunchCrossing[ bucketNumber % self.numverOfBuckets] >0





def histoAverage(theHisto=[1]):
    s    = sum(theHisto) 
    bins = [i for i in range( len(theHisto) )]
    # print(theHisto)
    # print(bins)
    average = 0.
    for one,two in list( zip(bins ,theHisto)  ):
        average += one*two
    average /= s
    return average


#########################################################
# class to handle the occupancy of hexaboards (studied by CMSSW)
# 
#        convert pickles from your legacy Python 2 codebase to Python 3
#        https://rebeccabilbro.github.io/convert-py2-pickles-to-py3/

class hexaSensorOccupancy:
    """
    class to handle the occupancy of hexaboards (studied by CMSSW)
    """
    histo      = []
    histoSize  = 0
    histoMean  = 0.

    def __init__(self,theFile=''):
        # open the pickele
        # (possibly handling the pyt2 case as well - for now do pyt3)
        # load the hitogram and store it somewhere
        # compute the average of the historgam
        if theFile=='':
            # if no file is pecified, trivialise the historgram -> occupancy always the same value
            self.histo = [0,1]
            #self.histo = [0,0,0,0,0,0,1/3.,1/3.,1/3.,0,0,0,0,0,]
        else :
            # move this to the class constructor
            theFile = '/afs/cern.ch/user/f/franzoni/work/HGCAL-DAQ-buffer/counts_FixedGridWtoQQ_PU0.pck'
            # Convert Python 2 "ObjectType" to Python 3 object
            dill._dill._reverse_typemap["ObjectType"] = object
    
            # Open the pickle using latin1 encoding
            with open(theFile, "rb") as f:
                loaded = pickle.load(f, encoding="latin1")
                # move the choice of sensor to the higher level class (and add it as a constructor parameter)
                waferKey=(0,8,-2,3)
                #waferKey=(0,8,-3,0) # good for a test high occup
                #waferKey=(0,8,-6,0) # good for a test half of abobe
                self.histo=loaded[waferKey]
                # print(type(self.histo))

        self.histoSize = len(  self.histo )
        self.histoMean = histoAverage( self.histo  )
        print(self.histo)
        print(self.histoSize)
        print(self.histoMean)
        
    def relativeOccupancy(self):
        return np.random.choice(self.histoSize, 1, p=self.histo )[0] / self.histoMean
        # return random.random()
        # replace here w/ the actual thrown histogram
