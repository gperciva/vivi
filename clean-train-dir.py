#!/usr/bin/env python

import glob


def clean_dir(dirname):
    wav_filenames = glob.glob(dirname+"*.wav")
    wav_filenames = [f for f in wav_filenames if ".forces.wav" not in f]
    for i in range(4):
        try:
            lines = open(dirname+"%i.mf" % i).readlines()
        except:
            return
        for line in lines:
            filename = line.split()[0]
            #print filename
            #print wav_filenames
            if filename in wav_filenames:
                wav_filenames.remove(filename)
    if len(wav_filenames) > 0:
        print "REMOVE THESE FILES:"
        for w in wav_filenames:
            print "rm %s" % (w[:-4]+'*')



clean_dir("train-data/violin/")
clean_dir("train-data/viola/")
clean_dir("train-data/cello/")





