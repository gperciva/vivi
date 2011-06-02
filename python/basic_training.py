#!/usr/bin/env python

import shared
import dynamics

finger_midis = [0.0, 4.0, 7.0]

EPSILON = 1e-3

class Basic:
	def __init__(self):
		pass

	def get_matching_fingers(self, dyn, coll):
		forces = [[],[],[]]
		cats = [[],[],[]]
		unknowns = [[],[],[]]
		# "level" parameters
		bbd = dynamics.get_distance(dyn)
		bv  = dynamics.get_velocity(dyn)

		for pair in coll.get_items(-1):
			params = shared.files.get_audio_params(pair[0])
			if ((abs(params.bow_bridge_distance - bbd) < EPSILON)
			    and (abs(params.bow_velocity - bv) < EPSILON)):
				for i in range(3):
					if (abs(params.finger_midi
						- finger_midis[i]) < EPSILON):
						cat = int(pair[1][0])
						if cat < 6:
							cats[i].append(cat)
							forces[i].append(params.bow_force)
						else:
							unknowns[i].append(params.bow_force)
		return forces, cats, unknowns

	def get_between(self, forces, cats, cat, unknowns):
		# get extremes
		combo = zip(forces, cats)
		higher_list = map(lambda(x):x[0],
				filter(lambda(x):x[1]>cat, combo))
		lower_list = map(lambda(x):x[0],
				filter(lambda(x):x[1]<cat, combo))
		higher = min(higher_list)
		lower = max(lower_list)
		# deal with unknowns
		unknown_between = filter(lambda(x):x>lower and x<higher, unknowns)
		# TODO: rewrite this in functional style
		between = [lower] + unknown_between + [higher]
		distances = []
		for i in range(len(between)-1):
			distance = between[i+1] - between[i]
			distances.append(distance)
		biggest_distance = max(distances)
		biggest_distance_index = distances.index(biggest_distance)

		force = between[biggest_distance_index] + biggest_distance/2.0
		return force

	def get_missing_force(self, forces, cats, unknowns):
		### start in the "middle-ish"
		if not forces:
			return 1.0
		### get extremes
		if not 5 in cats:
			return 2.0 * max(forces+unknowns)
		if not 1 in cats:
			return 0.5 * min(forces+unknowns)
		### fill in missing
		if not 3 in cats:
			return self.get_between(forces, cats, 3, unknowns)
		if not 4 in cats:
			return self.get_between(forces, cats, 4, unknowns)
		if not 2 in cats:
			return self.get_between(forces, cats, 2, unknowns)
		return None

	def get_next_basic(self, dyn, coll):
		""" the 'main' function of Basic; it returns the
			(force, finger_midi) that should next be judged by the
			human, or None if no training is needed. """
		forces, cats, unknowns = self.get_matching_fingers(dyn, coll)
		for i, finger_midi in enumerate(finger_midis):
			force = self.get_missing_force(forces[i], cats[i], unknowns[i])
			if force:
				return (finger_midi, force)
		return None


