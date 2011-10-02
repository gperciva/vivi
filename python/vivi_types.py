#!/usr/bin/env python
""" custom types used in Vivi """

import collections
import utils
import dynamics

AudioParams = collections.namedtuple('AudioParams', """
    string_number,
    finger_midi,
    bow_bridge_distance,
    bow_force,
    bow_velocity
    """)

def audio_params_to_physical(audio_params, dyn, physical):
    physical.string_number = audio_params.string_number
    physical.dynamic = dyn
    physical.finger_position = utils.midi2pos(audio_params.finger_midi)
    physical.bow_force = audio_params.bow_force
    physical.bow_bridge_distance = audio_params.bow_bridge_distance
    physical.bow_velocity = audio_params.bow_velocity
    return None # it's done with pass-by-reference

