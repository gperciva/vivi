#!/usr/bin/env python

import math

import task_base

import scipy.stats
import dirs
import basic_training

import shared
import vivi_controller
import utils
import dynamics
import vivi_types
import basic_training

import note_actions_cats

ATTACK_LENGTH = 0.75



class TaskAttack(task_base.TaskBase):

	def __init__(self, st, dyn, controller, emit, finger_index):
		task_base.TaskBase.__init__(self, st, dyn, controller, emit,
			"attack-%i"%finger_index)
		#self.STEPS = 8
		self.best_attack = 0 # a "null" value
		self.fmi = finger_index

		self.notes = None
		self.forces = None

	def set_K(self, K):
		self.controller.set_stable_K(self.st, self.dyn, K)

	def set_forces(self, forces):
		self.attack_forces = forces
		self.LOW_INIT = self.attack_forces[0]
		self.HIGH_INIT = self.attack_forces[2]

	def steps_full(self):
		return 2*(self.STEPS * self.REPS)

	def _make_files(self):
		self._setup_controller()

		for bow_force in self.test_range:
			# TODO: start counting at 1 due to "if 0" in training_dir
			for count in range(1,self.REPS+1):
				finger_midi = basic_training.FINGER_MIDIS[self.fmi]
				# FIXME: oh god ick
				ap = vivi_types.AudioParams( self.st,
					finger_midi,
					dynamics.get_distance(self.dyn),
					bow_force,
					dynamics.get_velocity(self.dyn))
				attack_filename = dirs.files.make_attack_filename(
					self.taskname,
					ap, count)
#				print attack_filename

				self.controller.reset()
				self.controller.filesNew(attack_filename)

				self.controller.comment("attack st %i dyn %i finger_midi %.3f"
						% (self.st, self.dyn, finger_midi))

				begin = vivi_controller.NoteBeginning()
				begin.physical.string_number = self.st
				begin.physical.dynamic = self.dyn
				begin.physical.finger_position = utils.midi2pos(finger_midi)
				begin.physical.bow_force = bow_force
				begin.physical.bow_bridge_distance = dynamics.get_distance(self.dyn)
				begin.physical.bow_velocity = dynamics.get_velocity(self.dyn)

				end = vivi_controller.NoteEnding()
				self.controller.note(begin, ATTACK_LENGTH, end)
				self.controller.filesClose()
				self.process_step.emit()

	def get_attack_files_info(self):
		self._examine_files()

	def _examine_files(self):
		files = self._get_files()

		# awkward splitting
		self.files = []
		self.forces = []
		for filename in files:
			params, count = dirs.files.get_audio_params_count(filename)
			if params.finger_midi == basic_training.FINGER_MIDIS[self.fmi]:
				self.files.append(filename)
				if count == 1:
					self.forces.append(params.bow_force)
		self.num_rows = len(self.files)

		# initialize 2d array
		self.notes = []
		for i in range(self.num_rows):
			self.notes.append([])
			for j in range(1):
				self.notes[i].append(None)

		for row, filename in enumerate(self.files):
			col = 0
			nac = note_actions_cats.NoteActionsCats()
			nac.load_file(filename[0:-4])
			to_find = "finger_midi %i" % basic_training.FINGER_MIDIS[self.fmi]
			nac.load_note(to_find)
			cats_means = nac.note_cats_means
			att = self.portion_attack(cats_means)
			mse = self.mse(att)
			self.notes[row][col] = (nac, mse, filename)

#		for n in self.notes:
#			print n

		cands = []
		col = 0
		for block in range(len(self.notes)/self.REPS):
			params = dirs.files.get_audio_params(
				self.notes[self.REPS*block][col][2])
			bow_force = params.bow_force
			vals = []
			for count in range(self.REPS):
				row = self.REPS*block + count
				val = self.notes[row][col]
				if val[1] > 0:
					vals.append(val[1])
			if len(vals) > 0:
				val = scipy.stats.gmean(vals)
			else:
				val = 0
			cands.append( (val, block, bow_force) )
		cands.sort()
		lowest_index = cands[0][1]
		self.best_attack = cands[0][2]
#		print '------'
#		for c in cands:
#			print c
#		print '------'
#		print self.fmi, lowest_index, self.best_attack
		return lowest_index, self.best_attack


	def portion_attack(self, values):
		newvalues = []
		past_values = scipy.zeros(9)
		pvi = 0
		M = 0.5
		filled = 0
		for val in values:
			if val < 0:
				continue
			newvalues.append(val)
			past_values[pvi] = val
			pvi += 1
			if pvi >= 9:
				pvi = 0
				filled = 1
			if filled:
				mse = self.mse(past_values)
				if M > mse:
					break
		#print newvalues
		#sys.exit(1)
		return newvalues			

	def mse(self, values):
		if len(values) == 0:
			return 0
		total = 0
		for val in values:
			err = 2 - val
			total += err*err
		total /= float(len(values))
		return total

