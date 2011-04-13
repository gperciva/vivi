#!/usr/bin/env python

#import collections

import shared

BOW_POS_FORTE = 0.08
BOW_VEL_FORTE = 0.4
BOW_POS_MF = 0.10
BOW_VEL_MF = 0.33
BOW_POS_MP = 0.12
BOW_VEL_MP = 0.26
BOW_POS_PIANO = 0.14
BOW_VEL_PIANO = 0.2

finger_midis = [0.0, 4.0, 7.0]
bow_positions = [ BOW_POS_FORTE, BOW_POS_MF, BOW_POS_MP, BOW_POS_PIANO ]
bow_velocities = [ BOW_VEL_FORTE, BOW_VEL_MF, BOW_VEL_MP, BOW_VEL_PIANO ]


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
		# "level" parameters
		l_bbd = bow_positions[self.dyn]
		l_bv = bow_velocities[self.dyn]

		for pair in self.coll.coll:
			params = shared.files.get_audio_params(pair[0])
			if ((abs(params.bow_bridge_distance - l_bbd) < EPSILON)
			    and (abs(params.bow_velocity - l_bv) < EPSILON)):
				for i in range(3):
					if (abs(params.finger_midi
						- finger_midis[i]) < EPSILON):
						cat = int(pair[1][0])
						cats[i].append(cat)
						forces[i].append(params.bow_force)
		return forces, cats

	def get_between(self, forces, cats, cat):
		combo = zip(forces, cats)
		higher = map(lambda(x):x[0],
				filter(lambda(x):x[1]>cat, combo))
		lower = map(lambda(x):x[0],
				filter(lambda(x):x[1]<cat, combo))
		mean = (min(higher) + max(lower)) / 2.0
		return mean

	def get_missing_force(self, forces, cats):
		### start in the "middle-ish"
		if not forces:
			return 1.0
		### get extremes
		if not 5 in cats:
			return 2.0 * max(forces)
		if not 1 in cats:
			return 0.5 * min(forces)
		### fill in missing
		if not 3 in cats:
			return self.get_between(forces, cats, 3)
		if not 4 in cats:
			return self.get_between(forces, cats, 4)
		if not 2 in cats:
			return self.get_between(forces, cats, 2)
		return 0

	def get_next_basic(self):
		forces, cats = self.get_matching_fingers()
		finger_midi = -1
		force = -1
		for i in range(3):
			finger_midi = finger_midis[i]
			force = self.get_missing_force(forces[i], cats[i])
			if force > 0:
				break
		if force > 0:
			audioParams = shared.AudioParams(self.st,
				finger_midi,
				bow_positions[self.dyn],
				force,
				bow_velocities[self.dyn])
			return audioParams
		return None


