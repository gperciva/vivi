#!/usr/bin/env python

DEBUG_PARAMS = 0

import sys
# TODO: hack for current build system.
sys.path.append('python/')
sys.path.append('build/python/')
sys.path.append('build/swig/')

from PyQt4 import QtCore
import os.path

import vivi_controller
import music_events
import dynamics
import dirs
import style_base
import utils

EXTRA_FINAL_REST = 0.5

class Performer(QtCore.QObject):
	process_step = QtCore.pyqtSignal()

	def __init__(self):
		QtCore.QObject.__init__(self)
		self.notation = music_events.MusicEvents()
		self.style = style_base.StyleBase()
		self.controller = vivi_controller.ViviController()
		if not dirs.files:
			dirs.files = dirs.ViviDirs(
				"train/", "/tmp/vivi-cache/", "final/")
		self.current_st = None

	def _setup_controller(self):
		for st in range(4):
			# FIXME: debug only
			for dyn in range(1):
				mpl_filename = dirs.files.get_mpl_filename(st, 'main', dyn)
				if not os.path.exists(mpl_filename):
					mpl_filename = None
				self.controller.load_ears_training(st, dyn,
					mpl_filename)
				self.controller.set_stable_K(st, dyn,
					self.style.controller_params[st][dyn].stable_K)

	def play(self):
		utils.play(self.audio_filename + ".wav")

	def load_file(self, filename):
		self.notation.load_file(filename)
		self.style.plan_perform(self.notation.events)
		self.audio_filename = filename.replace(".notes", "")

	def steps(self):
		return len(self.style.notes)

	def play_music(self):
		self._setup_controller()
		self.controller.filesNew(self.audio_filename)

		for note in self.style.notes:
			if isinstance(note, style_base.Note):
				self._render_note(note)
			elif isinstance(note, style_base.Rest):
				self._render_rest(note)
			else:
				print "Error: unknown event"
			self.process_step.emit()
		self.controller.rest(EXTRA_FINAL_REST)

		self.controller.filesClose()

	def _render_note(self, note):
		if note.pizz:
			self.controller.pizz(note.params, note.duration)
		else:
			if DEBUG_PARAMS:
				print "---"
				note.begin.print_params()
				note.end.print_params()
			self.controller.note(note.params, note.duration,
				note.begin, note.end)

	def _render_rest(self, note):
		self.controller.rest(note.duration)

	def get_duration(self):
		return self.style.last_seconds

