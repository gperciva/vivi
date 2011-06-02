#!/usr/bin/env python

import shared
import dynamics

finger_midis = [0.0, 4.0, 7.0]

EPSILON = 1e-3

class Basic:
	def __init__(self):
		self.st = -1
		self.dyn = -1
		self.coll = None

	def set_collection(self, st, dyn, coll):
		""" Gives a collection to Basic for analysis.
		    Remember that passing a list is by reference!"""
		self.st = st
		self.dyn = dyn
		self.coll = coll

	def get_matching_fingers(self):
		forces = [[],[],[]]
		cats = [[],[],[]]
		unknowns = [[],[],[]]
		# "level" parameters
#		bbd = shared.dyns.get_distance(self.dyn)
		bbd = dynamics.get_distance(self.dyn)
		bv  = dynamics.get_velocity(self.dyn)

		for pair in self.coll.get_items(-1):
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
		#print forces
		#print cats
		#print unknowns
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
		return 0

	def get_next_basic(self):
		forces, cats, unknowns = self.get_matching_fingers()
		finger_midi = -1
		force = -1
		for i in range(3):
			finger_midi = finger_midis[i]
			force = self.get_missing_force(forces[i], cats[i], unknowns[i])
			if force > 0:
				break
		if force > 0:
			return (force, finger_midi)
		return None


