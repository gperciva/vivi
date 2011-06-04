#!/usr/bin/env python

import os
import math

import scipy.stats
import dirs

import shared
import vivi_controller
import utils
import dynamics
import vivi_types

import note_actions_cats

STABLE_STEPS = 5
STABLE_REPS = 3
STABLE_MIN = 1.00
STABLE_MAX = 1.10

STABLE_LENGTH = 0.75


class TaskStable():

	def __init__(self, st, dyn, controller):
		self.st = st
		self.dyn = dyn
		self.controller = controller

		self.most_stable = 1.0 # a "null" value
		self.stable_forces = None
		self.num_rows = 0

		self.examines = None


	def set_emit(self, emit):
		self.process_step = emit

	def get_stable(self, forces):
		self.stable_forces = forces
		self.remove_previous_files()
		self.make_stable_files()
		self.examine_stable_files()
		#print "learned new K: ", self.most_stable
		return self.most_stable

	def remove_previous_files(self):
		bbd = dynamics.get_distance(dyn)
		bv  = dynamics.get_velocity(dyn)
		oldfiles = dirs.files.get_task_files("stable", self.st, bbd, bv)
		for filename in oldfiles:
			os.remove(filename)

	def make_stable_files(self):
		mpl_filename = dirs.files.get_mpl_filename(
			self.st, 'main', self.dyn)
		self.controller.load_ears_training(self.st, self.dyn,
			mpl_filename)


		for K in scipy.linspace(STABLE_MIN, STABLE_MAX, STABLE_STEPS):
			# TODO: start counting at 1 due to "if 0" in training_dir
			for count in range(1,STABLE_REPS+1):
				for fi in range(3):
					bow_direction = 1
					# TODO: bow force varies, so this is fake?
					bow_force = self.stable_forces[0][fi]
					# FIXME: oh god ick
					ap = vivi_types.AudioParams( self.st, 0,
						dynamics.get_distance(self.dyn),
						bow_force,
						bow_direction*dynamics.get_velocity(self.dyn))
					stable_filename = dirs.files.make_stable_filename(
						ap, K, count)

					self.controller.filesNew(stable_filename)
					for fmi, finger_midi in enumerate(shared.basic_training.finger_midis):
						bow_force = self.stable_forces[fmi][fi]
						self.controller.comment("stable st %i dyn %i finger_midi_index %i finger_midi %.3f"
							% (self.st, self.dyn, fmi, finger_midi))

						params = vivi_controller.PhysicalActions()
						params.string_number = self.st
						params.dynamic = self.dyn
						params.finger_position = utils.midi2pos(finger_midi)
						params.bow_force = bow_force
						params.bow_bridge_distance = dynamics.get_distance(self.dyn)
						params.bow_velocity = bow_direction * dynamics.get_velocity(self.dyn)

						self.controller.note(params, K, STABLE_LENGTH)

						bow_direction *= -1
					self.controller.filesClose()
					self.process_step.emit()

	def get_stable_files_info(self):
		bbd = dynamics.get_distance(self.dyn)
		bv  = dynamics.get_velocity(self.dyn)
		self.files = dirs.files.get_task_files("stable", self.st, bbd, bv)
		# 3 notes per file, 9 notes per line
		self.num_rows = 3*len(self.files)/9

		# variables about the files
		self.finger_midi_indices = range(3)
		self.forces_initial = []
		self.extras = []
		self.counts = []
		# get info about the files
		for filename in self.files:
			params, extra, count = dirs.files.get_audio_params_extra(filename)
			force = params.bow_force
			if not force in self.forces_initial:
				self.forces_initial.append(force)
			if not extra in self.extras:
				self.extras.append(extra)
			if not count in self.counts:
				self.counts.append(count)

		self.num_counts = len(self.counts)

		# initialize 2d array
		self.notes = []
		for i in range(self.num_rows):
			self.notes.append([])
			for j in range(9):
				self.notes[i].append(None)

		for filename in self.files:
			params, extra, count = dirs.files.get_audio_params_extra(filename)
			force = params.bow_force

			# and setup self.examines
			row = self.num_counts*self.extras.index(extra) + self.counts.index(count)
			col_base = 3*self.forces_initial.index(force)
			for fmi in self.finger_midi_indices:
				col = col_base+fmi
#				print row, col, fmi, filename
				nac = note_actions_cats.NoteActionsCats()
				nac.load_file(filename[0:-4])
				to_find = "finger_midi_index %i" % fmi
				nac.load_note(to_find)
				stability = self.get_stability(nac.note_cats_means)
				self.notes[row][col] = (nac, stability)


	def examine_stable_files(self):
		self.get_stable_files_info()

		# find "most stable" rows
		candidates = []
		for block in range(self.num_rows/self.num_counts):
			block_vals = []
			for count in range(self.num_counts):
				vals = []
				for col_block in range(3):
					cvs = []
					for col_i in range(3):
						row = self.num_counts*block + count
						col = 3*col_block+col_i
#						cv = self.examines[row][col].plot_actions.stability
						cv = self.notes[row][col][1]
						if cv > 0:
							cvs.append(cv)
					vals.append( scipy.stats.gmean(cvs) )
			#	row_stable = self.examines[row][0].plot_actions.stability
				#print vals
				row_stable = scipy.stats.gmean(vals)
				block_vals.append(row_stable)
			#print "%.2f\t%.3f" % (self.extras[block], scipy.gmean(block_vals)),
			#print "\t%.3f" % (scipy.std(block_vals))
			candidates.append( 
				(scipy.stats.gmean(block_vals), self.extras[block]) )
		candidates.sort()
		#print candidates
		self.most_stable = candidates[-1][1]

	def get_stability(self,cats):
		direction = 1
		areas = []
		area = []
		zeros = 1
		for cat in cats:
			if cat < 0:
				continue
			err = 2-cat
			if err == 0:
				continue
			if err * direction > 0:
				area.append(err)
			else:
				if area:
					areas.append(area)
				area = []
				area.append(err)
				direction = math.copysign(1, err)
				zeros += 1
		if area:
			areas.append(area)
		stable = 1.0
		for a in areas:
			area_fitness = 1.0 / math.sqrt(len(a))
			stable *= area_fitness
		return stable

