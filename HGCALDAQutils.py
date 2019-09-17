import random
import json

def isThereL1A(probability):
    if probability > 1:
        print("isThereL1A: probability set to", probability)
        raise ValueError('isThereL1A: You cannot have L1 tirgger probability larger than 1 ! ')
    return random.random() < probability


class lhcOrbitStructure:

    beamOne = []
    beamTwo = []

    def __init__(self,theFile=''):
        print('creating lhcOrbitStructure')
        print('the file is: %s'%theFile)

        if not theFile:
            pass
            # set up nominal beam lists by hand
        else:
            with open( theFile ) as json_file:
                theDic = json.load(json_file)
                # print( type( theDic)  )

                # print( theDic['beam1'] )
                # print( type( theDic['beam1']) )

                self.beamOne =  theDic['beam1']
                self.beamTwo =  theDic['beam2']
