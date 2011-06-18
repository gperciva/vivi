#!/usr/bin/env python
""" Console verison of Vivi, the Virtual Violinist. """

import sys

import vivi_controller
import dirs

from PyQt4 import QtCore

import shared

import performer_feeder

class ViviConsole(QtCore.QCoreApplication):
	""" Console version of Vivi, the Virtual Violinist. """
	def __init__(self,
			training_dirname, cache_dirname, final_dirname,
			ly_filename, skill):
		self.app = QtCore.QCoreApplication(sys.argv)
		QtCore.QCoreApplication.__init__(self, sys.argv)

		## setup shared
		dirs.files = dirs.ViviDirs(
			training_dirname, cache_dirname, final_dirname)
		self.setup_music()

		self.load_ly_file(ly_filename)

	def setup_music(self):
		shared.lily = shared.lilypond_compile.LilyPondCompile()
		shared.lily.process_step.connect(self.process_step)
		shared.lily.done.connect(self.finished_ly_compile)

		shared.music = shared.music_events.MusicEvents()

		self.performer_feeder = performer_feeder.PerformerFeeder()
		self.performer_feeder.process_step.connect(self.process_step)
		self.performer_feeder.done.connect(self.rehearse_done)

	def load_ly_file(self, ly_filename):
		self.ly_basename = ly_filename[:-3]
		if shared.lily.lily_file_needs_compile(ly_filename):
			print "Generating lilypond",
			shared.lily.call_lilypond()
		else:
			self.finished_ly_compile()

	def finished_ly_compile(self):
		print
		self.performer_feeder.load_file(shared.lily.get_filename_notes())
		self.rehearse()

	def process_step(self):
		# prevents from adding a space
		sys.stdout.write('.')
		sys.stdout.flush()

	def rehearse(self):
		print "Generating audio",
		steps = self.performer_feeder.play_music()

	def rehearse_done(self):
		print
		self.app.quit()

