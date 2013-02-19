#!/usr/bin/env python

import scipy.special

def agm_sequence(low, high, num):
    #def agm_recursive(low, high, num):
        #print "agm recursive", low, high, num
    agm = scipy.special.agm(low, high)
    if num <= 1:
        return [agm]
    agm_lows = agm_sequence(low, agm, num-1)
    agm_highs = agm_sequence(agm, high, num-1)
    return agm_lows + [agm] + agm_highs

def agm_seq(low, high, num):
    agms = agm_sequence(low, high, num)
    return [low] + agms + [high]

if __name__ == "__main__":
    seq = agm_sequence(0.01, 13.11, 4)
#    print "final:", seq
#    print len(seq)


