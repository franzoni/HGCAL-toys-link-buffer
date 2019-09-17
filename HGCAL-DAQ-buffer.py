#!/usr/bin/env python

import datetime
import HGCALDAQutils as utils

# https://docs.python.org/2/howto/argparse.html
# https://docs.python.org/3/library/argparse.html#default
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
                    type=int, default=10000,
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
args = parser.parse_args()



################################
# prepare key variables
lhcBucketRate              = 40000000
numCrossingsOverNumBuckets = 0.74 # compute this from the actual LHC orbit schema
probL1A                    = args.triggerRate / lhcBucketRate / numCrossingsOverNumBuckets
if probL1A > 1. :
    print('probL1A is: ',probL1A)
    raise ValueError('main: You cannot have L1 tirgger probability larger than 1! ')

# the buffer gets filled of a size 1. (in units of average event) at every L1A (triggerRate)
averageFillingRate         = 1. * args.triggerRate / lhcBucketRate
drainingRate               = args.fraction * averageFillingRate



################################
# the main loop over the buckets
bucketNumber               = 0
l1aNumber                  = 0
overflowNumber             = 0
dataInBuffer               = 0.
print('\n----- looping -----\n')
while  bucketNumber < args.numEvents :

    # things to do for any bucket, irrespective of trials
    bucketNumber +=1
    if not bucketNumber % 100000:
        print('\n\n ++++ at time: ', datetime.datetime.now(),' bucket bucketNumber: ',bucketNumber,'+++ \n\n')

    # take away data from the buffer
    dataInBuffer -= drainingRate
    if (dataInBuffer < 0 ) : dataInBuffer=0

    if (args.verbosity) : print('\n\tbucketNumber: %d dataInBuffer: %2.2f'% (bucketNumber,dataInBuffer) )

    # do we have a trigger?
    if not utils.isThereL1A(probL1A):
        if (args.verbosity) : print('\t\t TRIG NO  BX 00  -  dataInBuffer: %2.2f'%dataInBuffer )
        continue
    else:
        if (args.verbosity) : print('\t\t TRIG YES  BX 00  -  dataInBuffer: %2.2f'%dataInBuffer )


    # do we have a bunch crossing?
    # replace this selection with the real LHC structure
    if not utils.isThereL1A(numCrossingsOverNumBuckets): 
        if (args.verbosity) : print('\t\t TRIG YES  BX NO -  dataInBuffer: %2.2f'%dataInBuffer )
        continue

    l1aNumber   += 1
    # add the data to the buffer (in units of average event size)
    dataInBuffer += 1.
    if dataInBuffer > args.depthBuffer:
        if (args.verbosity) : print('\t\t OVERFLOW         -  dataInBuffer: %2.2f'%dataInBuffer )
        overflowNumber +=1
        # if the next event does not fit, it does not enter the buffer
        dataInBuffer   -= 1.

    if (args.verbosity) : print('\t\t TRIG YES  BX YES -  dataInBuffer: %2.2f'%dataInBuffer )
    # check if the buffer has overflown, in which case remove the last event

# end of the main loop
################################




print('\n\n\n\n----- finish -----\nall arguments in input:')
print('',parser.parse_args())
print(' probL1A: %2.4f'%probL1A)
print(' averageFillingRate: %2.4f [average event size / bucket]'%averageFillingRate)
print(' drainingRate: %2.4f [average event size / bucket]'%drainingRate)
print(' number of buckets: %d'%bucketNumber)
print(' number of L1As: %d'%l1aNumber)
print(' number of DAQ overflows: %d'%overflowNumber)
print(' fraction of DAQ overflows: %2.4f'%(overflowNumber/bucketNumber))


print('\n')


import sys
print('\n\n----- end -----\n',sys.argv[0])
print(sys.version)
