#!/usr/bin/env python

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
		self._setup_controller()
		self.current_st = None

	def _setup_controller(self):
		for st in range(4):
			for dyn in range(1):
				mpl_filename = dirs.files.get_mpl_filename(st, 'main', dyn)
				if not os.path.exists(mpl_filename):
					mpl_filename = None
				self.controller.load_ears_training(st, dyn,
					mpl_filename)

	def load_file(self, filename):
		self.notation.load_file(filename)
		self.style.plan_perform(self.notation.events)

	def steps(self):
		return len(self.style.notes)

	def play_music(self):
		self.controller.filesNew("audio")
#		self.controller.reset()
	
		for note in self.style.notes:
			self._render_note(note)
			self.process_step.emit()

		self.controller.filesClose()

	def _render_note(self, note):
		self.controller.note(note.params, note.duration)


