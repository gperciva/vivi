#!/usr/bin/env python

import sys
import os
import os.path
import shutil
import glob

TRAIN_DIRNAME = "train"
BASIC_FINGERS = [0]

def run(instrument_number, st, dyn, finger):
	script = "python interactive-artifastring.py "
	options = "%(instrument_number)s %(st)s %(dyn)s %(finger)s" % locals()
	cmd = script + options
	os.system(cmd)

def basic(instrument_number, st, dyn):
	for finger in BASIC_FINGERS:
		print "Doing string %i, finger %i" % (st, finger)
		raw_input("(press enter to continue)")
		run(instrument_number, st, dyn, finger)
	shutil.move("collection.mf", os.path.join(TRAIN_DIRNAME,
		str("%i_%i.mf" % (st, dyn))))
	for audio_filename in glob.glob("audio_*"):
		shutil.move(audio_filename, TRAIN_DIRNAME)


def do_all(instrument_number):
	for st in range(4):
		#for dyn in range(4):
		basic(instrument_number, st, 0)

if not os.path.exists(TRAIN_DIRNAME):
	os.mkdir(TRAIN_DIRNAME)
do_all(0)

