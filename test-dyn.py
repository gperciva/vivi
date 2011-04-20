#!/usr/bin/env python

import sys
sys.path.append('build/swig/')

import dynamics

foo = dynamics.Dynamics()
print foo.get_distance(0)

