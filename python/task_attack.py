#!/usr/bin/env python

import os
import math

import scipy

import shared
import vivi_controller
import utils

import note_actions_cats

FORCE_STEPS = 5
REPS = 3

ATTACK_LENGTH = 0.75


class TaskAttack():

	def __init__(self, st, dyn, controller):
		self.st = st
		self.dyn = dyn
		self.controller = controller

		self.best_attack = 0.0 # a "null" value


	def set_emit(self, emit):
		self.process_step = emit

	def get_attack(self, force_min, force_max):
		print "find attack between ", force_min, force_max
		self.remove_previous_files()
		self.make_attack_files()
		return [1.7, 1.3, 0.8]

	def remove_previous_files(self):
		oldfiles = shared.files.get_stable_files(self.st, self.dyn)
		for filename in oldfiles:
			os.remove(filename)

	def make_attack_files(self):
		print "making attack files"
		for i in range(FORCE_STEPS*REPS):
			self.process_step.emit()
		return

		mpl_filename = shared.files.get_mpl_filename(
			self.st, 'main', self.dyn)
		self.controller.load_ears_training(self.st, self.dyn,
			mpl_filename)


		for K in scipy.linspace(ATTACK_MIN, ATTACK_MAX, ATTACK_STEPS):
			# TODO: start counting at 1 due to "if 0" in training_dir
			for count in range(1,ATTACK_REPS+1):
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

						self.controller.note(params, K, ATTACK_LENGTH)

						bow_direction *= -1
					self.controller.filesClose()
					self.process_step.emit()

	def get_attack_files_info(self):
		self.files = shared.files.get_attack_files(self.st, self.dyn)
		print self.files

