#!/usr/bin/env python

import sys
sys.path.append('build/swig/')

# this breaks it?!
# it's ok if it's: yes, yes, commented
import vivi_controller
import dynamics
#import vivi_controller

vc = vivi_controller.ViviController()
foo = vc.getEars(0,0)
foo.set_training("train/0_0.mf", "bar.arff")
foo.tick_file()
#foo.processFile()

print dynamics.get_distance(0)

