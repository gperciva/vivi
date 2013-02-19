#!/usr/bin/env python

import math

import violin_instrument
import monowav

import scipy


violin = violin_instrument.ViolinInstrument()
wavfile = monowav.MonoWav("artifastring-test.wav")

FS = 22050
half = FS/2
st = 0

violin.finger(0, 0.344)
violin.bow(0, 0.08, 2.5, 0.3)
out = wavfile.request_fill(half)
violin.wait_samples(out, half)
violin.bow(0, 0.08, 2.5, 0.0)

violin.bow(1, 0.08, 1.5, 0.3)
out = wavfile.request_fill(half)
violin.wait_samples(out, half)

violin.bow(0, 0.08, 2.5, 0.3)
violin.bow(1, 0.08, 1.5, 0.3)
out = wavfile.request_fill(22050)
violin.wait_samples(out, 22050)



