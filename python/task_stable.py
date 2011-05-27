#!/usr/bin/env python

import os
import scipy

import shared
import vivi_controller
import utils
import examine_note_widget
import operator

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
		return self.most_stable

	def remove_previous_files(self):
		oldfiles = shared.files.get_stable_files(self.st, self.dyn)
		for filename in oldfiles:
			os.remove(filename)

	def make_stable_files(self):
		mpl_filename = shared.files.get_mpl_filename(
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
					ap = shared.AudioParams( self.st, 0,
						shared.dyns.get_distance(self.dyn),
						bow_force,
						bow_direction*shared.dyns.get_velocity(self.dyn))
					stable_filename = shared.files.make_stable_filename(
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
						params.bow_bridge_distance = shared.dyns.get_distance(self.dyn)
						params.bow_velocity = bow_direction * shared.dyns.get_velocity(self.dyn)

						self.controller.note(params, K, STABLE_LENGTH)

						bow_direction *= -1
					self.controller.filesClose()
					self.process_step.emit()

	def get_stable_files_info(self):
		self.files = shared.files.get_stable_files(self.st, self.dyn)
		# 3 notes per file, 9 notes per line
		self.num_rows = 3*len(self.files)/9

		# variables about the files
		self.finger_midi_indices = range(3)
		self.forces_initial = []
		self.extras = []
		self.counts = []
		# get info about the files
		for filename in self.files:
			params, extra, count = shared.files.get_audio_params_extra(filename)
			force = params.bow_force
			if not force in self.forces_initial:
				self.forces_initial.append(force)
			if not extra in self.extras:
				self.extras.append(extra)
			if not count in self.counts:
				self.counts.append(count)

		self.num_counts = len(self.counts)

		if not self.examines:
			self.examines = []
			# initialize 2d array
			for i in range(self.num_rows):
				self.examines.append([])
				for j in range(9):
					examine = examine_note_widget.ExamineNoteWidget(
						examine_note_widget.PLOT_STABLE)
					self.examines[i].append(examine)

			for filename in self.files:
				params, extra, count = shared.files.get_audio_params_extra(filename)
				force = params.bow_force
				# and setup self.examines
				row = self.num_counts*self.extras.index(extra) + self.counts.index(count)
				col_base = 3*self.forces_initial.index(force)
				for fmi in self.finger_midi_indices:
					col = col_base+fmi
#					print row, col, fmi, filename
					self.examines[row][col].load_file(filename[0:-4])
					to_find = "finger_midi_index %i" % fmi
					self.examines[row][col].load_note(to_find)


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
						cv = self.examines[row][col].plot_actions.stability
						cvs.append(cv)
					vals.append( scipy.stats.gmean(cvs) )
			#	row_stable = self.examines[row][0].plot_actions.stability
				#print vals
				row_stable = scipy.stats.gmean(vals)
				block_vals.append(row_stable)
			#print "%.2f\t%.3f" % (self.extras[block], scipy.gmean(block_vals)),
			#print "\t%.3f" % (scipy.std(block_vals))
			candidates.append( (self.extras[block],
				scipy.stats.gmean(block_vals)) )
		desc_candidates = sorted(candidates, key=operator.itemgetter(1))
		print desc_candidates
		self.most_stable = desc_candidates[-1][0]

