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
DAMPEN_NOTE_SECONDS = 0.25
DAMPEN_WAIT_SECONDS = 0.25

HOPS_DAMPEN = 8
HOPS_SETTLE = int( DAMPEN_NOTE_SECONDS * 44100.0/256.0) - HOPS_DAMPEN
HOPS_WAIT   = int( DAMPEN_WAIT_SECONDS * 44100.0/256.0) + HOPS_DAMPEN - 1


class TaskDampen(task_base.TaskBase):

	def __init__(self, st, dyn, controller, emit):
		task_base.TaskBase.__init__(self, st, dyn, controller, emit,
			"dampen")
		self.STEPS = 6
		self.REPS = 4

		self.notes = None
		self.initial_force = None

		self.ears = self.controller.getEars(self.st, self.dyn)
		self.hops = HOPS_SETTLE + HOPS_DAMPEN + HOPS_WAIT

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

				begin = vivi_controller.NoteBeginning()
				begin.physical.string_number = self.st
				begin.physical.dynamic = self.dyn
				begin.physical.finger_position = 0.0
				begin.physical.bow_force = self.initial_force
				begin.physical.bow_bridge_distance = dynamics.get_distance(self.dyn)
				begin.physical.bow_velocity = dynamics.get_velocity(self.dyn)

				filename = dirs.files.make_dampen_filename(
					self.taskname, 
					vivi_types.AudioParams(self.st, self.dyn,
						dynamics.get_distance(self.dyn),
						begin.physical.bow_force,
						dynamics.get_velocity(self.dyn)),
					damp, count)
				end = vivi_controller.NoteEnding()
				end.lighten_bow_force = True
				self.controller.filesNew(filename)
				self.controller.note(begin, DAMPEN_NOTE_SECONDS, end)
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

			nac = note_actions_cats.NoteActionsCats()
			nac.load_file(filename[0:-4])
			nac.load_note("note", full=True)
			self.notes[row][col] = (nac, 0, filename)


	def _examine_files(self):
		self.get_file_info()

		rmss = vivi_controller.doubleArray(self.hops)
		candidates = []
		for row, dampen in enumerate(self.extras):
			costs = []
			for col, count in enumerate(self.counts):
				filename = self.notes[row][col][2]
				self.ears.get_rms_from_file(self.hops,
					filename, rmss)
				total = 0.0
				total_damp = 0.0
				total_wait = 0.0
				prev = rmss[HOPS_SETTLE-1]
				for i in range(HOPS_DAMPEN):
					value = rmss[HOPS_SETTLE+i]
					total_damp += value
				for i in range(HOPS_WAIT):
					value = rmss[HOPS_SETTLE+HOPS_DAMPEN+i]
					total_wait += value
#				total = total_damp + total_wait
				total = total_wait

				self.notes[row][col] = (self.notes[row][col][0], total, filename)

				#costs.append(total_wait)
				costs.append(total)
			cost = scipy.stats.gmean(costs)
			#print dampen,
			#print dampen, '\t', "%.3f"%cost, '\t',
			#for x in costs:
			#	print "%.3f" % x,
			#print
			#print ["%.3f" % x for x in costs]
			candidates.append( 
				(cost, dampen, row) )
		candidates.sort()
		#print candidates
		answer = candidates[0][1]
		index = candidates[0][2]

		return index, answer

	def get_dampen_files_info(self):
		self._examine_files()



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

