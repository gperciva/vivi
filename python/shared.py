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

#NoteParams = collections.namedtuple('NoteParams', """
#	string_number,
#	dynamic,
#	finger_midi,
#	bow_force
#""")

import training_dir
files = None

import judge_audio
judge = None

import basic_training
basic = None

# FIXME: to avoid the dreaded
#   [MRSERR] MarControl::to() -  Incompatible type requested -
#   expected mrs_string for control  mrs_string/currentlyPlaying
# I have to import vivi_controller here for some unknown reason!
import vivi_controller

import dynamics
dyns = None


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


