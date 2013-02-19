#!/usr/bin/env python
""" various convenience utilities """

import os
import math
import random

EPSILON_PARAMS = 1e-3
import subprocess

def play(filename, start=None, length=None):
    """ plays a wav file (optional: part of one) using play(1). """
    cmd = "play -q "+filename
    #cmd = "play -q -t alsa "+filename
##    cmd = "mplayer -ao jack -really-quiet "
    if start >= 0:
        cmd += " trim %f %f" % (start, length)
#        cmd += " -ss %f -endpos %f " %(start, length)
#    print "utils:", cmd
    os.system(cmd)
    retcode = 0
    #cmd = cmd.split()
    #p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #(stdout, sterr) = p.communicate()
    #retcode = p.returncode
    if retcode > 0:
        print "FAILURE!  play returned:", retcode
    #print "play end:", p.returncode

#def visualize_cats(cats, length=8):
#    cats_string = ''
#    for c in cats:
#        stars = int(round(c*length))
#        cats_string += '*'*stars
#        cats_string += ' '*(length-stars)
#        cats_string += ' '*(length/4)
#    return cats_string

def midi2freq(note):
    """ midi pitch to frequency """
    freq = 440.0*pow(2, (note-69)/12.0)
    return freq

def freq2midi(freq):
    """ frequency to midi pitch """
    if freq == 0:
        return 0
    note = 69.0 + 12 * math.log(freq/440.0 , 2)
    return note

def midi2pos(num):
    """ midi pitch (relative to open string) to string position """
    return 1.0 - 1.0 / (1.05946309**num)

def pos2midi(pos):
    """ string position to midi pitch (relative to open string) """
    return 12.0*math.log(1.0/(1.0 - pos)) / math.log(2.0)

def norm_bounded(mu, sigma):
    """ returns a normally-distributed random value between
    -3*sigma and +3*sigma (inclusive) of mu.

    If a generated value is outside of that range, it tries
    picking another value a maximum of 3 times.  If none
    of those are within the bounds, then it simply returns
    mu."""
    if sigma == 0:
        return mu
    loops = 0
    while loops < 3:
        value = random.gauss( mu, sigma)
        if ( abs(value-mu) <= 3*sigma):
            return value
        else:
            loops += 1
    return mu

def is_in_list(needle, haystack):
    """ is needle in the haystack list, returning -1 if not. """
    try:
        return haystack.index(needle)
    except ValueError:
        return -1


def dyn_to_level(dyn):
    """ dynamic number to level (order of basic training) """
    level = -1
    if dyn == 0:
        level = 0
    elif dyn == 1:
        level = 2
    elif dyn == 2:
        level = 3
    elif dyn == 3:
        level = 1
    return level

def level_to_dyn(level):
    """ level (order of basic training) to dynamic number """
    dyn = -1
    if level == 0:
        dyn = 0
    elif level == 1:
        dyn = 3
    elif level == 2:
        dyn = 1
    elif level == 3:
        dyn = 2
    return dyn

def st_to_text(st):
    """ string number to text """
    text = 'X'
    if st == 0:
        text = 'G'
    elif st == 1:
        text = 'D'
    elif st == 2:
        text = 'A'
    elif st == 3:
        text = 'E'
    return text

def dyn_to_text(dyn):
    """ dynamic number to text """
    text = 'X'
    if dyn == 0:
        text = 'f'
    elif dyn == 1:
        text = 'mf'
    elif dyn == 2:
        text = 'mp'
    elif dyn == 3:
        text = 'p'
    return text

def almost_equals(one, two):
    """ compares two floats to accuracy EPSILON_PARAMS """
    return abs(one - two) < EPSILON_PARAMS


def interpolate(x, x0, y0, x1, y1):
    if (x1 - x0) == 0:
        return y0
    else:
        return y0 + (x-x0)*(y1-y0)/(x1-x0)

# limits printing floats to X decimal places
def printList(list, digits=2, comma=1, eol=True):
    line = ''
    if comma==1:
        for x in list: line += str(("% ."+str(digits)+"f, " ) % (x))
        print line[:-2],
    else:
        for x in list: line += str(("% ."+str(digits)+"f " ) % (x))
        print line,

