#!/usr/bin/env python

import datetime
from   decimal import Decimal
import HGCALDAQutils as utils

# https://docs.python.org/2/howto/argparse.html
# https://docs.python.org/3/library/argparse.html#default
# https://pymotw.com/2/argparse/#argument-types
from   argparse import ArgumentParser
parser = ArgumentParser(description="Emulate numEvents buckets, and count the number of HGCAL DAQ overflows")
#parser.add_argument("-f", "--file", dest="filename",
#                    help="write report to FILE", metavar="FILE")
# parser.add_argument("-v","--verbose", dest="verbose", type=int, help="activate verbosity",
#                    action='store_false')
parser.add_argument("-v", "--verbosity", dest="verbosity",
                    action='store_true',
                    help="activate verbosity")
parser.add_argument("-n", "--numEvents", dest="numEvents",
                    type=int, default=100005,
                    help="number of LHC buckets simulated", metavar="N")
parser.add_argument("-f", "--fraction", dest="fraction", 
                    type=float, default=1.3,
                    help="buffer empyting rate, relative to the filling rate", metavar="F")
parser.add_argument("-d", "--depthBuffer", dest="depthBuffer",   
                    type=int, default=25,
                    help="buffer depth, in unit of average event size", metavar="D")
parser.add_argument("-t", "--triggerRate", dest="triggerRate",   
                    type=int, default=750000,
                    help="targer rate of L1 accepts [Hz]", metavar="T")
# https://pymotw.com/2/argparse/#mutually-exclusive-options
mutExclGroupLHC = parser.add_mutually_exclusive_group()
mutExclGroupLHC.add_argument('-lhcFlat','--lhcIrrealisticFlat', action='store_true'
                          ,help="file containing beams bucket/bunch structure")
mutExclGroupLHC.add_argument('-lhcReal','--lhcRealisticRun2', action='store_true'
                          ,help="file containing beams bucket/bunch structure")
mutExclGroupLHC.add_argument('-lhcFile','--lhcStructureFromFile', dest='lhcFile'
                          ,default='',help="file containing beams bucket/bunch structure")

mutExclGroupEvSiz = parser.add_mutually_exclusive_group()
mutExclGroupEvSiz.add_argument('-fes','--fixEvSize', action='store_true'
                          ,help="Events are all assumed having the same size")
mutExclGroupEvSiz.add_argument('-varEvPU','--varEvePileUp', dest="nPu",type=int,default=-1
                          ,help="ev-by-ev variable event size, choose PU scenario between 0 and 200")

args = parser.parse_args()


################################
# prepare key variables

# set up the lhcOrbitStructure instance, first
s=''
if  args.lhcIrrealisticFlat:
    pass
elif args.lhcRealisticRun2:
    s='data/25ns_2556b_2544_2215_2332_144bpi_20inj_800ns_bs200ns_v3-bunchArrays.json'
elif args.lhcFile:
    s=args.lhcFile
else:
    raise ValueError('main: none of the three LHC bunch structures options set. It''s needed')
lhcOS                      = utils.lhcOrbitStructure(s)


# set up the event-size variables then
nPuFile=''
if  args.fixEvSize:
    #print('fixEvSize -> will leave the nPuFile empty')
    pass
elif args.nPu != -1:
    if   args.nPu==0:
        nPuFile='/eos/user/p/psilva/HGCal/DataRates/counts_FixedGridWtoQQ_PU0.pck'
    elif args.nPu==200:
        nPuFile='/eos/user/p/psilva/HGCal/DataRates/counts_FixedGridWtoQQ_PU200.pck'
    else:
        raise ValueError('main: none of the valid pile up valies set.')
    #print('args.nPu is set')
    #print(args.nPu)
    #print(nPuFile)
else:
    raise ValueError('main: none of the two event-size options set. It''s needed')

hexaSO = utils.hexaSensorOccupancy(nPuFile)


numCrossingsOverNumBuckets = float( lhcOS.numberBucketsWithBunchXing() ) / lhcOS.numberBuckets()
# other consequent variables
lhcBucketRate              = 40000000

probL1A                    = args.triggerRate / lhcBucketRate / numCrossingsOverNumBuckets
if probL1A > 1. :
    print('probL1A is: ',probL1A)
    raise ValueError('main: You cannot have L1 tirgger probability larger than 1! ')

# the buffer gets filled of a size 1. (in units of average event) at every L1A (triggerRate)
averageFillingRate         = 1. * args.triggerRate / lhcBucketRate
drainingRate               = args.fraction * averageFillingRate




################################
# the main loop over the buckets
bucketNumber               = -1
l1aCount                   = 0
overflowNumber             = 0
dataInBuffer               = 0.
print('\n----- looping -----\n')
while  bucketNumber < args.numEvents :

    # things to do for any bucket, irrespective of trials
    bucketNumber +=1
    if not bucketNumber % 100000:
        print('\n\n ++++ at time: %s  bucket bucketNumber: %d +++ \n'\
              %(datetime.datetime.now(),bucketNumber))

    verb = args.verbosity
    # take away data from the buffer
    dataInBuffer -= drainingRate
    if (dataInBuffer < 0 ) : dataInBuffer=0
    if (verb) : print('\n\tbucketNumber: %d dataInBuffer: %2.2f'% (bucketNumber,dataInBuffer) )

    # do we have a trigger?
    if not utils.isThereL1A(probL1A):
        if (verb) : print('\t\t TRIG NO  BX 00  -  dataInBuffer: %2.2f'%dataInBuffer )
        continue
    else:
        if (verb) : print('\t\t TRIG YES  BX 00  -  dataInBuffer: %2.2f'%dataInBuffer )


    # do we have a bunch crossing?
    # replace this selection with the real LHC structure
    # if not utils.isThereL1A(numCrossingsOverNumBuckets): # superseeded
    if not lhcOS.isThereBunchCrossing(bucketNumber):
        if (verb) : print('\t\t TRIG YES  BX NO -  dataInBuffer: %2.2f'%dataInBuffer )
        continue

    l1aCount   += 1
    # add the data to the buffer (in units of average event size)
    # dataInBuffer += 1.
    # print(hexaSO.relativeOccupancy())
    dataInBuffer += hexaSO.relativeOccupancy()
    if dataInBuffer > args.depthBuffer:
        if (verb) : print('\t\t OVERFLOW         -  dataInBuffer: %2.2f'%dataInBuffer )
        overflowNumber +=1
        # if the next event does not fit, it does not enter the buffer
        dataInBuffer   -= 1.

    if (verb) : print('\t\t TRIG YES  BX YES -  dataInBuffer: %2.2f'%dataInBuffer )
    # check if the buffer has overflown, in which case remove the last event

# end of the main loop
################################



print('\n\n\n\n----- finish -----\nall arguments in input:')
print('',parser.parse_args())
print(' probL1A: %2.4f'%probL1A)
print(' averageFillingRate: %2.4f [average event size / bucket]'%averageFillingRate)
print(' drainingRate: %2.4f [average event size / bucket]'%drainingRate)
print(' number of buckets emulated: %d   (%.2E)'%(bucketNumber, Decimal( bucketNumber ) ))
print(' number of L1As: %d   (%.2E)'%(l1aCount, Decimal( l1aCount )))
print(' number of DAQ overflows: %d   (%.2E)'%(overflowNumber, Decimal( overflowNumber ) ))
print(' fraction of DAQ overflows: %.3E'%(overflowNumber/bucketNumber))


print('\n')


import sys
print('\n\n----- end -----\n',sys.argv[0])
print(sys.version)
