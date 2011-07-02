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

import glob
import os.path

# 50 ms = 8.6 hops
# 52.2 ms = 9 hops
# 100 ms = 17.2 hops
HOPS_SETTLE = int( 0.5 * 44100.0/256.0)
#HOPS_DAMPEN = 8
#HOPS_WAIT   = int( 0.05 * 44100.0/256.0)
HOPS_DAMPEN = 8
HOPS_WAIT   = 20

DAMPEN_NOTE_SECONDS = 0.5
DAMPEN_WAIT_SECONDS = 28.0/44100.0*256.0

class TaskDampen(task_base.TaskBase):

	def __init__(self, st, dyn, controller, emit):
		task_base.TaskBase.__init__(self, st, dyn, controller, emit,
			"dampen")
		self.STEPS = 8
		self.REPS = 5

		self.initial_force = None

		self.ears = self.controller.getEars(self.st, self.dyn)
		self.hops = HOPS_SETTLE + HOPS_DAMPEN + HOPS_WAIT
		self.rmss = vivi_controller.doubleArray(self.hops)

	def steps_full(self):
		return 2*(self.STEPS * self.REPS)

	def set_K(self, K):
		self.controller.set_stable_K(self.st, self.dyn, K)

	def set_initial_force(self, force):
		self.initial_force = force

	def _make_files(self):
		self._setup_controller()

		for damp in self.test_range:
			self.controller.set_dampen(self.st, self.dyn, damp)
			for count in range(1, self.REPS+1):

				params = vivi_controller.PhysicalActions()
				params.string_number = self.st
				params.dynamic = self.dyn
				params.finger_position = 0.0
				params.bow_force = self.initial_force
				params.bow_bridge_distance = dynamics.get_distance(self.dyn)
				params.bow_velocity = dynamics.get_velocity(self.dyn)

				filename = dirs.files.make_dampen_filename(
					self.taskname, 
					vivi_types.AudioParams(self.st, self.dyn,
						dynamics.get_distance(self.dyn),
						params.bow_force,
						dynamics.get_velocity(self.dyn)),
					damp, count)
				begin = vivi_controller.NoteBeginning()
				end = vivi_controller.NoteEnding()
				end.lighten_bow_force = True
				self.controller.filesNew(filename)
				self.controller.note(params, DAMPEN_NOTE_SECONDS, begin, end)
				self.controller.rest(DAMPEN_WAIT_SECONDS)
				self.controller.filesClose()
				self.process_step.emit()
		return

	def get_file_info(self):
		files = self._get_files()
		files.sort()
		#print files
#		print "examining files"

		self.extras = []
		self.counts = []
		for filename in files:
			params, extra, count = dirs.files.get_audio_params_extra(filename)
			if not extra in self.extras:
				self.extras.append(extra)
			if not count in self.counts:
				self.counts.append(count)

		# just to be safe
		self.extras.sort()
		self.counts.sort()

		num_rows = len(self.extras)
		num_cols = len(self.counts)

		self.notes = []
		for i in range(num_rows):
			self.notes.append([])
			for j in range(num_cols):
				self.notes[i].append(None)

		for filename in files:
			params, extra, count = dirs.files.get_audio_params_extra(filename)
			row = self.extras.index(extra)
			col = self.counts.index(count)
			self.notes[row][col] = filename


	def _examine_files(self):
		self.get_file_info()

		candidates = []
		for row, dampen in enumerate(self.extras):
			costs = []
			for col, count in enumerate(self.counts):
				filename = self.notes[row][col]
				self.ears.get_rms_from_file(self.hops,
					filename, self.rmss)
				total = 0.0
				total_damp = 0.0
				total_wait = 0.0
				for i in range(HOPS_DAMPEN):
					value = self.rmss[HOPS_SETTLE+i]
					total_damp += value
				for i in range(HOPS_WAIT):
					value = self.rmss[HOPS_SETTLE+HOPS_DAMPEN+i]
					total_wait += value
				total = total_damp + total_wait
				#costs.append(total_wait)
				costs.append(total)
			cost = scipy.stats.mean(costs)
			print dampen,
			#print dampen, '\t', "%.3f"%cost, '\t',
			for x in costs:
				print "%.3f" % x,
			print
			#print ["%.3f" % x for x in costs]
			candidates.append( 
				(cost, dampen, row) )
		candidates.sort()
		#print candidates
		answer = candidates[0][1]
		index = candidates[0][2]

		return index, answer

# FIXME: oh god ick debug only
#	def calculate_full(self):
#		""" does a full (re)calculation of the task """
#		self._init_range()
#		self._remove_previous_files()
#		self._make_files()
#		first_answer_index, first_answer = self._examine_files()
#		second_answer = first_answer
##		self._zoom_range(first_answer_index)
##		self._make_files()
#		# TODO: second_answer_index is not trustworthy!
##		second_answer_index, second_answer = self._examine_files()
#		return second_answer

