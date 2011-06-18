#!/usr/bin/env python

import math
import scipy.stats

import task_base

import dirs
import note_actions_cats
import dynamics
import vivi_controller

import utils
import vivi_types
import basic_training


STABLE_LENGTH = 0.75


class TaskStable(task_base.TaskBase):

	def __init__(self, st, dyn, controller, emit):
		task_base.TaskBase.__init__(self, st, dyn, controller, emit,
			"stable")
		self.STEPS = 6
		self.LOW_INIT = 1.0 # blah numbers to start with
		self.HIGH_INIT = 1.1

		self.stable_forces = None

		# TODO: eliminate this
		self.most_stable = 1.0
		self.notes = None

	def set_forces(self, forces):
		self.stable_forces = forces

	def steps_full(self):
		return 2 * (self.STEPS * self.REPS)

	def _make_files(self):
		self._setup_controller()

		for K in self.test_range:
			self.controller.set_stable_K(self.st, self.dyn, K)
			for count in range(self.REPS):
				# TODO: this loop could be done in a separate C++ file
				for force_relative_index in range(3):
					bow_direction = 1
					# TODO: bow force varies, so this is fake?
					bow_force = self.stable_forces[0][force_relative_index]
					# the finger_midi position is fake, as is the
					# bow force
					stable_filename = dirs.files.make_stable_filename(
						vivi_types.AudioParams(self.st, 0,
							dynamics.get_distance(self.dyn),
							bow_force,
							bow_direction*dynamics.get_velocity(self.dyn)),
						K, count+1)

					self.controller.filesNew(stable_filename)
					for fmi, finger_midi in enumerate(basic_training.FINGER_MIDIS):
						bow_force = self.stable_forces[fmi][force_relative_index]
						self.controller.comment("stable st %i dyn %i finger_midi %.3f"
							% (self.st, self.dyn, finger_midi))

						params = vivi_controller.PhysicalActions()
						params.string_number = self.st
						params.dynamic = self.dyn
						params.finger_position = utils.midi2pos(finger_midi)
						params.bow_force = bow_force
						params.bow_bridge_distance = dynamics.get_distance(self.dyn)
						params.bow_velocity = bow_direction * dynamics.get_velocity(self.dyn)

						self.controller.note(params, STABLE_LENGTH)
						bow_direction *= -1
					self.controller.filesClose()
				self.process_step.emit()

	def get_stable_files_info(self):
		files = self._get_files()

		# 3 notes per file, 9 notes per line
		num_rows = 3*len(files)/9

		# variables about the files
		self.finger_midi_indices = range(3)
		self.forces_initial = []
		self.extras = []
		self.counts = []
		# get info about the files
		for filename in files:
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
		for i in range(num_rows):
			self.notes.append([])
			for j in range(9):
				self.notes[i].append(None)

		for filename in files:
			params, extra, count = dirs.files.get_audio_params_extra(filename)
			force = params.bow_force

			# and setup self.examines
			row = self.num_counts*self.extras.index(extra) + self.counts.index(count)
			col_base = 3*self.forces_initial.index(force)
			for fmi, fm in enumerate(basic_training.FINGER_MIDIS):
				col = col_base+fmi
#				print row, col, fmi, filename
				nac = note_actions_cats.NoteActionsCats()
				nac.load_file(filename[0:-4])
				to_find = "finger_midi %i" % fm
				nac.load_note(to_find)
				stability = self.get_stability(nac.note_cats_means)
				self.notes[row][col] = (nac, stability)


	def _examine_files(self):
		self.get_stable_files_info()

		num_rows = len(self.notes)
		# find "most stable" rows
		candidates = []
		for block in range(num_rows/self.num_counts):
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
				(scipy.stats.gmean(block_vals), self.extras[block], block) )
		candidates.sort()
		#print candidates
		most_stable = candidates[-1][1]
		index = candidates[-1][2]
		return index, most_stable

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

