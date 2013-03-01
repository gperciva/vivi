#!/usr/bin/env python

import sys
sys.path.append('../build/swig')

import math
import numpy

import vivi_controller

import scipy

import utils
import pylab
import scipy.io.wavfile

import vivi_defines
HOPSIZE = vivi_defines.HOPSIZE


DAMPEN_NOTE_SECONDS = 1.0

vivi = vivi_controller.ViviController()
vivi.set_stable_K(0, 0, 1.1)
vivi.load_ears_training(0, "../final/violin/0.mpl")


begin = vivi_controller.NoteBeginning()
begin.physical.string_number = 0
begin.physical.dynamic = 0
begin.physical.finger_position = 0.0
begin.physical.bow_force = 2.0
begin.physical.bow_bridge_distance = 0.1
begin.physical.bow_velocity = 0.4

end = vivi_controller.NoteEnding()
#end.lighten_bow_force = False
end.keep_bow_velocity = True


DAMPEN_HOPS = 10
DAMPEN_WAIT = 172
def try_thing(basename):
    vivi.filesNew("test-%s" % basename)
    vivi.note(begin, DAMPEN_NOTE_SECONDS, end)
    vivi.m_feedback_adjust_force = False

    init_force = vivi.actions.bow_force
    for i in range(DAMPEN_HOPS):
        if basename == "instant":
            vivi.actions.bow_force = 0.
        if basename == "linear":
            factor= (DAMPEN_HOPS-float(i))/ (DAMPEN_HOPS+1)
            vivi.actions.bow_force = init_force*factor
            #print init_force, factor, vivi.actions.bow_force
        if basename == "squared":
            factor= ((DAMPEN_HOPS-float(i)) / (DAMPEN_HOPS+1))**2
            vivi.actions.bow_force = init_force*factor
            #print init_force, factor, vivi.actions.bow_force
        if basename == "one_over_x":
            factor= 1.0 / (i+2.0)
            vivi.actions.bow_force = init_force * factor
            print init_force, factor, vivi.actions.bow_force
        if basename == "exp-05":
            vivi.actions.bow_force *= 0.5
            #print vivi.actions.bow_force
        if basename == "exp-08":
            vivi.actions.bow_force *= 0.8
        if basename == "exp-02":
            vivi.actions.bow_force *= 0.2
        vivi.hop()

    vivi.actions.bow_force = 0.
    for i in range(DAMPEN_WAIT):
        vivi.hop()

    vivi.filesClose()

    sample_rate, samples = scipy.io.wavfile.read("test-%s.wav" % basename)
    samples = numpy.float64(samples[:HOPSIZE*(len(samples)/HOPSIZE)])
    chunks = numpy.reshape( samples, (len(samples)/HOPSIZE,HOPSIZE) )
    rmss = []
    for chunk in chunks:
        rms = numpy.sqrt( sum(chunk**2) / len(chunk))
        rmss.append(rms)
    pylab.plot(rmss, label=basename)


try_thing("instant")
try_thing("linear")
try_thing("squared")
try_thing("exp-05")
try_thing("exp-08")
try_thing("exp-02")
try_thing("one_over_x")

pylab.legend()
pylab.show()

