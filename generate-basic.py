#!/usr/bin/env python

import sys
import os
import os.path
import shutil
import glob

TRAIN_DIRNAME = "train"
BASIC_FINGERS = [0, 6]

def run(instrument_number, st, dyn, finger):
    script = "python interactive-artifastring.py "
    options = "%(instrument_number)s %(st)s %(dyn)s %(finger)s" % locals()
    cmd = script + options
    os.system(cmd)

def basic(instrument_number, st, dyn):
    for finger in BASIC_FINGERS:
        print "Doing finger %i" % (finger)
        raw_input("\t(press enter to continue)")
        run(instrument_number, st, dyn, finger)
    shutil.move("collection.mf", os.path.join(TRAIN_DIRNAME,
        str("%i_%i.mf" % (st, dyn))))
    for audio_filename in glob.glob("audio_*"):
        shutil.move(audio_filename, TRAIN_DIRNAME)

def do_all(instrument_number):
    for st in range(4):
        for dyn in range(1, 4): # HACK FIXME
            print "Doing string %i, dynamic %i" % (st, dyn)
            basic(instrument_number, st, dyn)

if not os.path.exists(TRAIN_DIRNAME):
    os.mkdir(TRAIN_DIRNAME)
do_all(0)

