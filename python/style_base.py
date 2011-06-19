#!/usr/bin/env python

import dirs

import vivi_controller
import dynamics
import controller_params

import basic_training # for FINGER_MIDIS
import utils

class Note():
	def __init__(self, params=None, duration=0, pizz=False,
			begin=None, end=None):
		self.params = params
		self.duration = duration
		self.pizz = pizz
		self.begin = begin
		self.end = end
class Rest():
	def __init__(self, duration=0):
		self.duration = duration

class StyleBase():

	def __init__(self):
		self.notes = None
		self.events = None

		self.controller_params = []
		for st in range(4):
			st_controllers = []
			# FIXME: debug only
			for dyn in range(1):
				dyn_filename = dirs.files.get_dyn_vivi_filename(st, dyn)
				st_controllers.append(controller_params.ControllerParams(dyn_filename))
			self.controller_params.append(st_controllers)
		self.reload_params()

		self.tempo = 60.0

	def reload_params(self):
		for st in range(4):
			for dyn in range(1):
				self.controller_params[st][dyn].load_file()

	def plan_perform(self, events):
		self.events = events
		self.basic_notes()
		self.ties()
		self.alternate_bowing() # after ties

	def basic_notes(self):
		self.notes = []
		pizz = False
		for event in self.events:
			# must process tempo events before note!
			for details in event.details:
				if details[0] == 'tempo':
					self.tempo_from_lilytempo(details[1][0])
			duration = self.calc_duration(event.duration)
			if event.details[0][0] == 'rest':
				rest = Rest(duration)
				self.notes.append(rest)
				continue
			# TODO: icky, functionalify this ?
			for d in event.details:	
				if d[0] == 'text':
					if d[1][0] == 'pizz':
						pizz = True
					if d[1][0] == 'arco':
						pizz = False
			params = self.simple_params(event)
			begin = vivi_controller.NoteBeginning()
			end = vivi_controller.NoteEnding()
			note = Note(params, duration, pizz, begin, end)
			self.notes.append(note)

	def ties(self):
		for i, event in enumerate(self.events):
			for details in event.details:
				if details[0] == 'tie':
					self.notes[i].end.continue_next_note = True
					self.notes[i+1].begin.continue_previous_note = True

	def alternate_bowing(self):
		bow_dir = 1
		# TODO: totally naive right now; no slurs
		for i, event in enumerate(self.events):
			self.notes[i].params.bow_velocity *= bow_dir
			if not self.notes[i].end.continue_next_note:
				bow_dir *= -1

	def tempo_from_lilytempo(self, tempo):
		self.tempo = float(tempo) / 4.0

	def calc_duration(self, dur):
		seconds = 4.0 * (60.0 / self.tempo) * dur
		return seconds

	def simple_params(self, event):
		pitch = float(event.details[0][1][0])
		params = vivi_controller.PhysicalActions()
		params.string_number, params.finger_position = self.get_finger_naive(pitch)
		# FIXME: only dyn 0
		params.dynamic = 0
		params.bow_bridge_distance = dynamics.get_distance(0)
		# FIXME: only dyn 0, no force interpolation
		params.bow_force = self.get_simple_force(
			params.string_number, params.finger_position)
		params.bow_velocity = dynamics.get_velocity(0)
		return params

	def get_simple_force(self, st, finger_position):
		# TODO: this function is icky
		low_index = 0
		high_index = 0
		# ASSUME: FINGER_MIDIS is already sorted
		fm = utils.pos2midi(finger_position)
		for i, val in enumerate(basic_training.FINGER_MIDIS):
			if fm >= val:
				low_index = i
				high_index = i+1
		if high_index >= len(basic_training.FINGER_MIDIS):
			high_index = len(basic_training.FINGER_MIDIS) - 1
		force = utils.interpolate(fm,
			basic_training.FINGER_MIDIS[low_index],
			self.controller_params[st][0].get_attack_force(low_index),
			basic_training.FINGER_MIDIS[high_index],
			self.controller_params[st][0].get_attack_force(high_index))
		return force

	def get_finger_naive(self,pitch):
		which_string = self.get_naive_string(pitch)
		finger_semitones = pitch - (55 + 7*which_string)
		position = self.semitones(finger_semitones)
		return which_string, position

	def get_naive_string(self,pitch):
		if (pitch < 62):
			return 0
		elif (pitch < 69):
			return 1
		elif (pitch < 76):
			return 2
		else:
			return 3

	def semitones(self, num):
		return 1.0 - 1.0 / (1.05946309**num)


