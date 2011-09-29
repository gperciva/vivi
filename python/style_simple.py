#!/usr/bin/env python

import style_base

import vivi_controller
import dynamics
import utils

STACCATO_SHORTEN_MULTIPLIER = 0.7
PORTATO_SHORTEN_MULTIPLIER = 0.9
BREATHE_SHORTEN_MULTIPLIER = 0.5

class StyleSimple(style_base.StyleBase):
	def __init__(self):
		style_base.StyleBase.__init__(self)

	def plan_perform(self, events):
		self.make_notes_durs(events)
		self.add_point_and_click()
		self.basic_physical_begin_end()
		self.do_strings_explicit()
		self.do_dynamics()
		self.do_pizz()
		self.do_ties()
		self.do_staccato_breathe() # before bowing?
		self.do_bowing() # after ties
		self.do_lighten() # do after staccato adds rests

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
			note.begin = vivi_controller.NoteBeginning()
			note.begin.physical.string_number = self.get_string(note.details)
			note.begin.physical.finger_position = self.get_finger_naive(note.details, note.begin.physical.string_number)
			note.end = vivi_controller.NoteEnding()

	def get_string(self, details):
		pitch = float(details[0][1][0])
		return self.get_naive_string(pitch)

	def get_finger_naive(self, details, which_string):
		pitch = float(details[0][1][0])
		return self.get_finger(pitch, which_string)

	def string_text_to_number(self, text):
		if text == 'I':
			return 3
		elif text == 'II':
			return 2
		elif text == 'III':
			return 1
		elif text == 'IV':
			return 0
		else:
			return None

	def do_strings_explicit(self):
		which_string_span = None
		for note in self.notes:
			if not self.is_note(note):
				continue
			text_details = self.get_details(note, "set_string")
			will_stop = False
			if len(text_details) > 0:
				which_string_span = self.string_text_to_number(text_details[0][1])
				if text_details[0][0] == '1':
					will_stop = True
			text_details = self.get_details(note, "text")
			if len(text_details) > 0:
				which_string = self.string_text_to_number(text_details[0][0])
				if which_string is not None:
					self.pitch_string(note, which_string)
			elif which_string_span is not None:
				self.pitch_string(note, which_string_span)
			if will_stop:
				which_string_span = None

	def pitch_string(self, note, which_string):
		pitch = float(note.details[0][1][0])
		finger_semitones = pitch - (55 + 7*which_string)
		position = self.semitones(finger_semitones)
		note.begin.physical.string_number = which_string
		note.begin.physical.finger_position = position


	def do_pizz(self):
		pizz = False
		for note in self.notes:
			if not self.is_note(note):
				continue
			text_details = self.get_details(note, "text")
			if text_details:
				if text_details[0][0] == "pizz.":
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
			note.begin.physical.bow_velocity *= bow_dir
			if note.end.physical.string_number >= 0:
				note.end.physical.bow_velocity *= bow_dir
			slur_details = self.get_details(note, "slur")
			if slur_details:
				if slur_details[0][0] == '-1':
					slur_on = True
				else:
					slur_on = False
			stop_bow = False
			script_details = self.get_details(note, "script")
			if ["staccato"] in script_details:
				stop_bow = True
			if ["portato"] in script_details:
				stop_bow = True
			if slur_on and not stop_bow:
				note.end.keep_bow_velocity = True
			if not slur_on:
				bow_dir *= -1

	def do_lighten(self):
		for note, note_next in self.pair(self.notes):
			if not self.is_note(note):
				continue
			# deliberately set elsewhere, don't change
			if note.end.let_string_vibrate:
				continue
			# before a rest
			if not self.is_note(note_next):
				note.end.lighten_bow_force = True
			if self.is_note(note_next):
				if (note.begin.physical.string_number !=
					note_next.begin.physical.string_number):
					note.end.lighten_bow_force = True

		# last note
		note = self.notes[len(self.notes)-1]
		if self.is_note(note):
			note.end.lighten_bow_force = True

	def do_staccato_breathe(self):
		# make copy of list to allow modifying
		for note in list(self.notes):
			if not self.is_note(note):
				continue
			script_details = self.get_details(note, "script")
			if ["staccato"] in script_details:
				index = self.notes.index(note)
				extra_rest = style_base.Rest(note.duration*(1.0-STACCATO_SHORTEN_MULTIPLIER))
				note.duration *= STACCATO_SHORTEN_MULTIPLIER
				self.notes.insert(index+1, extra_rest)
			if ["portato"] in script_details:
				index = self.notes.index(note)
				extra_rest = style_base.Rest(note.duration*(1.0-PORTATO_SHORTEN_MULTIPLIER))
				note.duration *= PORTATO_SHORTEN_MULTIPLIER
				self.notes.insert(index+1, extra_rest)
		# make copy of list to allow modifying
		for note, note_next in self.pair(list(self.notes)):
			if not self.is_note(note):
				continue
			if not self.is_note(note_next):
				continue
			# TODO: hack because breathe happens on
			# the note after?!?!
			breathe_details = self.get_details(note_next, "breathe")
			if breathe_details:
				index = self.notes.index(note)
				extra_rest = style_base.Rest(note.duration*(1.0-BREATHE_SHORTEN_MULTIPLIER))
				note.duration *= BREATHE_SHORTEN_MULTIPLIER
				self.notes.insert(index+1, extra_rest)
				note.end.lighten_bow_force = False
				note.end.let_string_vibrate = True
				note.end.keep_bow_velocity = True

	def do_dynamics(self):
		current_dynamic = 0 # default to forte
		cresc_goal = -1
		cresc_duration = 0
		cresc_begin = 0
		cresc_into = 0
		for i, note in enumerate(self.notes):
			if not self.is_note(note):
				continue
			dyn = self.get_details(note, "dynamic")
			if dyn:
				current_dynamic = self.dynamic_string_to_float(dyn[0][0])
				cresc_goal = -1
				cresc_duration = 0.0
			cresc_details = self.get_details(note, "cresc")
			if not cresc_details:
				cresc_details = self.get_details(note, "decresc")
			if cresc_details:
				cresc_begin = float(current_dynamic)
				cresc_into = 0.0
				cresc_duration = note.duration
				for later_note in self.notes[i+1:]:
					if not self.is_note(later_note):
						continue
					dyn = self.get_details(later_note, "dynamic")
					if dyn:
						cresc_goal = self.dynamic_string_to_float(dyn[0][0])
						break
					cresc_duration += later_note.duration
			if cresc_goal >= 0:
				current_dynamic = utils.interpolate(
					cresc_into,
					0.0, cresc_begin,
					cresc_duration, cresc_goal)
				cresc_into += note.duration
				end_dynamic = utils.interpolate(
					cresc_into,
					0.0, cresc_begin,
					cresc_duration, cresc_goal)
			self.set_dynamic(note.begin.physical, current_dynamic)
			if cresc_goal >= 0:
				note.end.physical.string_number = note.begin.physical.string_number
				note.end.physical.finger_position = note.begin.physical.finger_position
				self.set_dynamic(note.end.physical, end_dynamic)
				if cresc_into >= cresc_duration:
					cresc_goal = -1

	def set_dynamic(self, physical, dynamic):
		physical.dynamic = dynamic
		physical.bow_bridge_distance = dynamics.get_distance(dynamic)
		physical.bow_force = self.get_simple_force(
			physical.string_number,
			physical.finger_position,
			dynamic)
		physical.bow_velocity = dynamics.get_velocity(dynamic)

	def dynamic_string_to_float(self, dyn):
		if dyn == 'f':
			return 0.0
		elif dyn == 'mf':
			return 1.0
		elif dyn == 'mp':
			return 2.0
		elif dyn == 'p':
			return 3.0
		return None

