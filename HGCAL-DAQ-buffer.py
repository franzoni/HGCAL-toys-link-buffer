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
                    type=bool, default=False,
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


print('\n\nall arguments in input:')
print(parser.parse_args())
print('\n')



numCrossingsOverBuckets = 0.74 # compute this from the actual LHC orbit
probL1A      = args.triggerRate / 40000000. / numCrossingsOverBuckets
if probL1A > 1. :
    print('probL1A is: ',probL1A)
    raise ValueError('You cannot have L1 tirgger probability larger than 1! ')
bucketNumber = 0
dataInBuffer = 0.

# the buffer gets filled of a size 1. (in units of average event) at every L1A (triggerRate)
averageFillingRate = 1. * args.triggerRate / 40000000





################################
# the main loop over the buckets
while  bucketNumber < args.numEvents :

    # things to do for any bucket, irrespective of trials
    bucketNumber +=1
    if not bucketNumber % 100000:
        print('at time: ', datetime.datetime.now(),' bucket bucketNumber: ',bucketNumber)


    # take away data from the buffer
    dataInBuffer -= args.fraction * averageFillingRate
    if (dataInBuffer < 0 ) : dataInBuffer=0
    

    # do we have a trigger?
    if not utils.isThereL1A(probL1A): continue


    # do we have a bunch crossing?
    # replace this selection with the real LHC structure
    if not utils.isThereL1A(numCrossingsOverBuckets): continue
    
    # add the data to the buffer (in units of average event size)
    dataInBuffer += 1.

    # check if the buffer has overflown, in which case remove the last event

# end of the main loop
################################




# print('\n\n\n\nHGCAL-DAQ-buffer')
import sys
print('\n\n\n\n\n',sys.argv[0])
print(sys.version)
