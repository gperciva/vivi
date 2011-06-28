#!/usr/bin/env python

import math

import violin_instrument
import monowav

import scipy


violin = violin_instrument.ViolinInstrument()
wavfile = monowav.MonoWav("artifastring-test.wav")

def wait(samples, do_rms=False):
    out = wavfile.request_fill(samples)
    violin.wait_samples(out, samples)
    if do_rms:
        ptr = monowav.shortArray_frompointer(out)
        total = 0.0
        for i in range(samples):
            val = ptr[i]
            total += val*val
        rms = math.sqrt(total)
        return rms

FS = 44100.0
sec = int(0.2*FS)

# stop with bow
for i in scipy.linspace(0.38, 0.45, 10):
    damp = i
    print "*** %f", damp

    # pluck loudly
    violin.reset()
    violin.pluck(2, 0.5, 1.0)
    wait(sec)

    force = 1.0
    steps = sec/256
    for i in range(steps):
        violin.bow(2, 0.08, force, 0.0)
        rms = wait(256, do_rms=True)
        #print "%.3f\t" % force,
        print "%.1f" % rms,
        force *= damp
        #force -= 1.0/(steps-0)
        if force < 0:
            force = 0.0
    print
    force = 0.0
    violin.bow(2, 0.08, force, 0.0)
    out = wavfile.request_fill(sec)
    violin.wait_samples(out, sec)



