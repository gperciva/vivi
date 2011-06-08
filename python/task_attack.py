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

FORCE_STEPS = 10
REPS = 3

ATTACK_LENGTH = 0.75



class TaskAttack(task_base.TaskBase):

	def __init__(self, st, dyn, controller, emit):
		task_base.TaskBase.__init__(self, st, dyn, controller, emit,
			"attack")

		self.best_attacks = [0, 0, 0] # a "null" value
		self.K = 1.0

		self.notes = None
		self.forces = None


	def set_K(self, K):
		self.K = K

	def get_attack(self, attack_forces):
		self._remove_previous_files()
		self.make_attack_files(attack_forces)
		self.get_attack_files_info()
		return self.best_attacks

	def make_attack_files(self, attack_forces):
		mpl_filename = dirs.files.get_mpl_filename(
			self.st, 'main', self.dyn)
		self.controller.load_ears_training(self.st, self.dyn,
			mpl_filename)

		for fmi, forces in enumerate(attack_forces):
			force_min = forces[0]
			force_max = forces[2]
			for bow_force in scipy.linspace(force_min, force_max, FORCE_STEPS):
				# TODO: start counting at 1 due to "if 0" in training_dir
				for count in range(1,REPS+1):
					finger_midi = basic_training.FINGER_MIDIS[fmi]
					# FIXME: oh god ick
					ap = vivi_types.AudioParams( self.st,
						finger_midi,
						dynamics.get_distance(self.dyn),
						bow_force,
						dynamics.get_velocity(self.dyn))
					attack_filename = dirs.files.make_attack_filename(
						ap, count)
#					print attack_filename

					self.controller.reset()
					self.controller.filesNew(attack_filename)

					self.controller.comment("attack st %i dyn %i finger_midi_index %i finger_midi %.3f"
							% (self.st, self.dyn, fmi, finger_midi))

					params = vivi_controller.PhysicalActions()
					params.string_number = self.st
					params.dynamic = self.dyn
					params.finger_position = utils.midi2pos(finger_midi)
					params.bow_force = bow_force
					params.bow_bridge_distance = dynamics.get_distance(self.dyn)
					params.bow_velocity = dynamics.get_velocity(self.dyn)

					self.controller.note(params, self.K, ATTACK_LENGTH)
					self.controller.filesClose()
					self.process_step.emit()

	def get_attack_files_info(self):
		bbd = dynamics.get_distance(self.dyn)
		bv  = dynamics.get_velocity(self.dyn)
		self.files = dirs.files.get_task_files("attack", self.st, bbd, bv)
		# awkward splitting
		self.finger_files = []
		self.finger_forces = []
		for fmi, fm in enumerate(basic_training.FINGER_MIDIS):
			finger_attacks = []
			finger_forces = []
			for filename in self.files:
				params, count = dirs.files.get_audio_params_count(filename)
				if params.finger_midi == fm:
					finger_attacks.append(filename)
					if count == 1:
						finger_forces.append(params.bow_force)
				#print filename
			self.finger_files.append(finger_attacks)
			self.finger_forces.append(finger_forces)

		# TODO: generalize?
		self.num_rows = len(self.finger_files[0])

		# initialize 2d array
		self.notes = []
		for i in range(self.num_rows):
			self.notes.append([])
			for j in range(3):
				self.notes[i].append(None)


		for col, filelist in enumerate(self.finger_files):
			for row, filename in enumerate(filelist):
				nac = note_actions_cats.NoteActionsCats()
				nac.load_file(filename[0:-4])
				to_find = "finger_midi_index %i" % col
				nac.load_note(to_find)
				cats_means = nac.note_cats_means
				att = self.portion_attack(cats_means)
				mse = self.mse(att)
				self.notes[row][col] = (nac, mse, filename)

#		for n in self.notes:
#			print n

		for col in range(len(self.notes[0])):
			cands = []
			for block in range(len(self.notes)/REPS):
				params = dirs.files.get_audio_params(
					self.notes[REPS*block][col][2])
				bow_force = params.bow_force
				vals = []
				for count in range(REPS):
					row = REPS*block + count
					val = self.notes[row][col]
					if val[1] > 0:
						vals.append(val[1])
				val = scipy.stats.gmean(vals)
				cands.append( (val, block, bow_force) )
			cands.sort()
			lowest = cands[0][2]
			self.best_attacks[col] = lowest


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
		total = 0
		for val in values:
			err = 2 - val
			total += err*err
		total /= float(len(values))
		return total

