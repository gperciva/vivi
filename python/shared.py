#!/usr/bin/env python
""" "shared" data between all parts of Vivi. """

import collections
AudioParams = collections.namedtuple('AudioParams', """
	string_number,
	finger_midi,
	bow_bridge_distance,
	bow_force,
	bow_velocity
	""")

import training_dir
files = None

import judge_audio
judge = None

import basic_training
basic = None

#import vivi_controller
#AudioParams = vivi_controller.PhysicalActions

#import compare_coll
#compare = None

#import ears
#listen = None
#
#HOPSIZE = ears.EARS_HOPSIZE
#
#import skill
#ability = None


