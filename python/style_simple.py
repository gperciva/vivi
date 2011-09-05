#!/usr/bin/env python

import style_base

import vivi_controller
import dynamics


class StyleSimple(style_base.StyleBase):
	def __init__(self):
		style_base.StyleBase.__init__(self)

	def plan_perform(self, events):
		self.make_notes_durs(events)
		self.add_point_and_click()
		self.basic_physical_begin_end()
		self.do_dynamics()
		self.do_pizz()
		self.do_ties()
		self.do_bowing() # after ties
		self.do_lighten() # do after staccato adds rests
		self.do_staccato() # do after lighten? TODO: maybe

	def make_notes_durs(self, events):
		self.notes = []
		tempo_bpm = 60.0
		self.last_seconds = 0.0
		for event in events:
			tempo_details = self.get_details(event, "tempo")
			if tempo_details:
				tempo_bpm = float(tempo_details[0][0]) / 4.0
			seconds = 4.0 * (60.0 / tempo_bpm) * event.duration
			if event.details[0][0] == 'rest':
				rest = style_base.Rest(duration=seconds)
				self.notes.append(rest)
			elif event.details[0][0] == 'note':
				note = style_base.Note(duration=seconds,
					details=event.details)
				self.notes.append(note)
			self.last_seconds += seconds

	def add_point_and_click(self):
		for note in self.notes:
			if not self.is_note(note):
				continue
			point_and_click = "point_and_click %s %s" % (
				note.details[0][1][4],
				note.details[0][1][5])
			note.point_and_click = point_and_click

	def basic_physical_begin_end(self):
		for note in self.notes:
			if not self.is_note(note):
				continue
			note.physical = self.simple_params(note.details)
			note.begin = vivi_controller.NoteBeginning()
			note.end = vivi_controller.NoteEnding()

	def do_pizz(self):
		pizz = False
		for note in self.notes:
			if not self.is_note(note):
				continue
			text_details = self.get_details(note, "text")
			if text_details:
				if text_details[0][0] == "pizz":
					pizz = True
				elif text_details[0][0] == "arco":
					pizz = False
			note.pizz = pizz

	def do_ties(self):
		for note, note_next in self.pair(self.notes):
			if not self.is_note(note) or not self.is_note(note_next):
				continue
			tie_details = self.get_details(note, "tie")
			# tie_details is [] which is non-existant but not None
			if len(tie_details) > 0:
				note.end.keep_bow_velocity = True
				note_next.begin.ignore_finger = True
				note_next.begin.keep_bow_force = True

	def do_bowing(self):
		bow_dir = 1
		slur_on = False
		for note in self.notes:
			if not self.is_note(note):
				continue
			note.physical.bow_velocity *= bow_dir
			slur_details = self.get_details(note, "slur")
			if slur_details:
				if slur_details[0][0] == '-1':
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
			if self.is_note(note) and not self.is_note(note_next):
				note.end.lighten_bow_force = True
			if self.is_note(note) and self.is_note(note_next):
				if (note.physical.string_number !=
					note_next.physical.string_number):
					note.end.lighten_bow_force = True
			if self.is_note(note):
				breathe_details = self.get_details(note, "breathe")
				if breathe_details:
					note.end.lighten_bow_force = False
					note.end.let_string_vibrate = True
		# last note
		note = self.notes[len(self.notes)-1]
		if self.is_note(note):
			note.end.lighten_bow_force = True

	def do_staccato(self):
		for note in self.notes:
			if not self.is_note(note):
				continue
			script_details = self.get_details(note, "script")
#			if ["staccato"] in script_details:
#				note.end.lighten_bow_force = False

	def do_dynamics(self):
		current_dynamic = 0 # default to forte
		for note in self.notes:
			if not self.is_note(note):
				continue
			dyn = self.get_details(note, "dynamic")
			if dyn:
				current_dynamic = self.dynamic_string_to_float(dyn[0][0])
			note.physical.dynamic = current_dynamic
			note.physical.bow_bridge_distance = dynamics.get_distance(current_dynamic)
			note.physical.bow_force = self.get_simple_force(
				note.physical.string_number,
				note.physical.finger_position,
				current_dynamic)
			note.physical.bow_velocity = dynamics.get_velocity(current_dynamic)

	def dynamic_string_to_float(self, dyn):
		if dyn == 'f':
			return 0
		elif dyn == 'mf':
			return 1
		elif dyn == 'mp':
			return 2
		elif dyn == 'p':
			return 3
		return 0

