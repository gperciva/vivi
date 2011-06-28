#!/usr/bin/env python

import dirs

import vivi_controller
import dynamics
import controller_params

import basic_training # for FINGER_MIDIS
import utils

class Note():
	def __init__(self, physical=None, duration=0, pizz=False,
			begin=None, end=None, point_and_click=None,
			details=None):
		self.physical = physical
		self.duration = duration
		self.pizz = pizz
		self.begin = begin
		self.end = end
		self.point_and_click = point_and_click
		self.details = details
class Rest():
	def __init__(self, duration=0):
		self.duration = duration

class StyleBase():

	def __init__(self):
		self.notes = None
		self.last_seconds = 0.0

		self.controller_params = []
		for st in range(4):
			st_controllers = []
			# FIXME: debug only
			for dyn in range(1):
				dyn_filename = dirs.files.get_dyn_vivi_filename(st, dyn)
				st_controllers.append(controller_params.ControllerParams(dyn_filename))
			self.controller_params.append(st_controllers)
		self.reload_params()


	def reload_params(self):
		for st in range(4):
			for dyn in range(1):
				self.controller_params[st][dyn].load_file()

	def plan_perform(self, events):
		self.make_notes_durs(events)
		self.add_point_and_click()
		self.basic_physical_begin_end()
		self.do_pizz()
		self.do_ties()
		self.do_bowing() # after ties
		self.do_lighten() # do after staccato adds rests

	def get_details(self, note, text):
		for detail in note.details:
			if detail[0] == text:
				return detail[1]
		return None

	@staticmethod
	def pair(values):
		return zip(values[:-1], values[1:])



	def make_notes_durs(self, events):
		self.notes = []
		tempo_bpm = 60.0
		self.last_seconds = 0.0
		for event in events:
			tempo_details = self.get_details(event, "tempo")
			if tempo_details:
				tempo_bpm = float(tempo_details[0]) / 4.0
			seconds = 4.0 * (60.0 / tempo_bpm) * event.duration
			if event.details[0][0] == 'rest':
				rest = Rest(duration=seconds)
				self.notes.append(rest)
			elif event.details[0][0] == 'note':
				note = Note(duration=seconds,
					details=event.details)
				self.notes.append(note)
			self.last_seconds += seconds

	def add_point_and_click(self):
		for note in self.notes:
			if isinstance(note, Rest):
				continue
			point_and_click = "point_and_click %s %s" % (
				note.details[0][1][4],
				note.details[0][1][5])
			note.point_and_click = point_and_click

	def basic_physical_begin_end(self):
		for note in self.notes:
			if isinstance(note, Rest):
				continue
			note.physical = self.simple_params(note.details)
			note.begin = vivi_controller.NoteBeginning()
			note.end = vivi_controller.NoteEnding()

	def do_pizz(self):
		pizz = False
		for note in self.notes:
			if isinstance(note, Rest):
				continue
			text_details = self.get_details(note, "text")
			if text_details:
				if text_details[0] == "pizz":
					pizz = True
				elif text_details[0] == "arco":
					pizz = False
			note.pizz = pizz

	def do_ties(self):
		for note, note_next in self.pair(self.notes):
			if isinstance(note, Rest) or isinstance(note_next, Rest):
				continue
			tie_details = self.get_details(note, "tie")
			# tie_details is [] which is non-existant but not None
			if tie_details is not None:
				note.end.keep_bow_velocity = True
				note_next.begin.ignore_finger = True
				note_next.begin.keep_bow_force = True

	def do_bowing(self):
		bow_dir = 1
		slur_on = False
		for note in self.notes:
			if isinstance(note, Rest):
				continue
			note.physical.bow_velocity *= bow_dir
			slur_details = self.get_details(note, "slur")
			if slur_details:
				if slur_details[0] == '-1':
					slur_on = True
				else:
					slur_on = False
			if slur_on:
				note.end.keep_bow_velocity = True
			if not note.end.keep_bow_velocity:
				bow_dir *= -1

	def do_lighten(self):
		for note, note_next in self.pair(self.notes):
			# before a rest
			if isinstance(note, Note) and isinstance(note_next, Rest):
				note.end.lighten_bow_force = True
			if isinstance(note, Note) and isinstance(note_next, Note):
				if (note.physical.string_number !=
					note_next.physical.string_number):
					note.end.lighten_bow_force = True
			if isinstance(note, Note):
				breathe_details = self.get_details(note, "breathe")
				if breathe_details:
					note.end.lighten_bow_force = False
					note.end.let_string_vibrate = True
		# last note
		note = self.notes[len(self.notes)-1]
		if isinstance(note, Note):
			note.end.lighten_bow_force = True

	def calc_duration(self, dur):
		seconds = 4.0 * (60.0 / self.tempo) * dur
		return seconds

	def simple_params(self, details):
		pitch = float(details[0][1][0])
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


