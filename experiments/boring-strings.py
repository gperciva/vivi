#!/usr/bin/env python

import math

import violin_instrument
import monowav

import scipy

import utils


violin = violin_instrument.ViolinInstrument()
wavfile = monowav.MonoWav("artifastring-test.wav")

FS = 44100.0
sec = int(0.2*FS)
st = 0

bp = 0.12
force = 1.4
velocity = 0.4

violin.bow(0, bp, force, velocity)
samples = 44100

def note(note_midi, direction):
    #violin.bow(0, bp, force, direction*velocity)
    #violin.bow(0, bp, force, direction*velocity)
    violin.finger(0, utils.midi2pos(note_midi))
    out = wavfile.request_fill(samples)
    violin.wait_samples(out, samples)

note(0,1)
note(2,-1)
note(4,1)
note(5,-1)


