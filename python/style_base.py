#!/usr/bin/env python


import vivi_controller
import dynamics

class Note():
	def __init__(self, params=None, duration=0):
		self.params = params
		self.duration = duration

class StyleBase():

	def __init__(self):
		self.notes = None
		self.events = None

	def plan_perform(self, events):
		self.events = events
		self.notes = []

		for event in self.events:
			if event.details[0][0] == 'rest':
				continue
			params = self.simple_params(event)
			note = Note(params=params, duration=event.duration)
			self.notes.append(note)

	def simple_params(self, event):
		pitch = float(event.details[0][1][0])
		params = vivi_controller.PhysicalActions()
		params.string_number, params.finger_position = self.get_finger_naive(pitch)
		params.dynamic = 0
		params.bow_bridge_distance = dynamics.get_distance(0)
		params.bow_force = 1.0
		params.bow_velocity = dynamics.get_velocity(0)
		return params


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


