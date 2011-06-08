#!/usr/bin/env python
""" deals with basic training of dynamics in training collection """

import dirs
import dynamics

FINGER_MIDIS = [0.0, 4.0, 7.0]

EPSILON = 1e-3

def _almost_equals(one, two):
	""" compares two floats to accuracy EPSILON """
	return abs(one - two) < EPSILON

def _get_matching_fingers(dyn, coll):
	""" finds all items in coll that match the dynamic.  Splits
		matching items into lists matching FINGER_MIDIS pitches."""

	def is_level_match(pair, level_bbd, level_bv):
		""" does a collection pair match the level parameters? """
		params = dirs.files.get_audio_params(pair[0])
		return (_almost_equals(params.bow_bridge_distance, level_bbd) and
			_almost_equals(params.bow_velocity, level_bv))

	# "level" parameters
	bbd = dynamics.get_distance(dyn)
	bv  = dynamics.get_velocity(dyn)
	match_level = filter(lambda(pair): is_level_match(pair, bbd, bv),
						coll.get_items(-1))

	# TODO: functional-ify this
	# split forces+cats into fingers
	forces = [[], [], []]
	cats = [[], [], []]
	unknowns = [[], [], []]
	for pair in match_level:
		params = dirs.files.get_audio_params(pair[0])
		for i, fm in enumerate(FINGER_MIDIS):
			if _almost_equals(params.finger_midi, fm):
				cat = int(pair[1][0])
				if cat < 6:
					cats[i].append(cat)
					forces[i].append(params.bow_force)
				else:
					unknowns[i].append(params.bow_force)
	return forces, cats, unknowns

def _get_between(forces, cats, cat, unknowns):
	""" finds a force between the boundaries """
	# get extremes
	combo = zip(forces, cats)
	higher_force = min(map(lambda(x):x[0],
	                       filter(lambda(x):x[1]>cat, combo)))
	lower_force  = max(map(lambda(x):x[0],
	                       filter(lambda(x):x[1]<cat, combo)))
	# deal with unknowns
	unknown_between = filter(lambda(x):x>lower_force and x<higher_force,
	                         unknowns)
	between = [lower_force] + unknown_between + [higher_force]
	distances = [x-y for x, y in zip(between[:-1], between[1:])]
	biggest_distance = max(distances)
	biggest_distance_index = distances.index(biggest_distance)
	force = between[biggest_distance_index] + biggest_distance/2.0
	return force

def _get_missing_force(forces, cats, unknowns):
	""" finds the 'next missing force' to get, according to the
		basic training plan. """
	### start in the "middle-ish"
	if not forces:
		force = 1.0
	### get extremes
	elif not 5 in cats:
		force = 2.0 * max(forces+unknowns)
	elif not 1 in cats:
		force = 0.5 * min(forces+unknowns)
	### fill in missing
	elif not 3 in cats:
		force = _get_between(forces, cats, 3, unknowns)
	elif not 4 in cats:
		force = _get_between(forces, cats, 4, unknowns)
	elif not 2 in cats:
		force = _get_between(forces, cats, 2, unknowns)
	else:
		force = None
	return force

def get_next_basic(dyn, coll):
	""" the 'main' function of Basic; it returns the
		(force, finger_midi) that should next be judged by the
		human, or None if no training is needed. """
	forces, cats, unknowns = _get_matching_fingers(dyn, coll)
	for i, finger_midi in enumerate(FINGER_MIDIS):
		force = _get_missing_force(forces[i], cats[i], unknowns[i])
		if force:
			return (force, finger_midi)
	return None


