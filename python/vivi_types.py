#!/usr/bin/env python
""" custom types used in Vivi """

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


