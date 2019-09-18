import random
import json


def isThereL1A(probability):
    if probability > 1:
        print("isThereL1A: probability set to", probability)
        raise ValueError('isThereL1A: You cannot have L1 tirgger probability larger than 1 ! ')
    return random.random() < probability



class lhcOrbitStructure:

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
