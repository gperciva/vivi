#!/usr/bin/env python

from PyQt4 import QtCore
import performer

STATE_NULL = 0
STATE_RENDER_MUSIC = 1
STATE_PLAYING = 2

class PerformerFeeder(QtCore.QThread):
	process_step = QtCore.pyqtSignal()
	done = QtCore.pyqtSignal()

	def __init__(self):
		QtCore.QThread.__init__(self)
		self.performer = performer.Performer()
		self.audio_filename = None
		self.performer.process_step.connect(self.process_step)

		self.mutex = QtCore.QMutex()
		self.condition = QtCore.QWaitCondition()
		self.state = STATE_NULL
		self.start()

	def run(self):
		while True:
			self.mutex.lock()
			self.condition.wait(self.mutex)
			if self.state == STATE_RENDER_MUSIC:
				self.perform_thread()
			if self.state == STATE_PLAYING:
				self.play_thread()
			self.state = STATE_NULL
			self.done.emit()
			self.mutex.unlock()

	def load_file(self, filenames):
		# FIXME: only one staff per performer; do polyphony how?
		filename = filenames[0]
		self.performer.load_file(filename)

	def play(self):
		self.state = STATE_PLAYING
		self.condition.wakeOne()
		return self.performer.steps()

	def play_music(self):
		self.state = STATE_RENDER_MUSIC
		self.condition.wakeOne()
		# TODO: is this the number of steps to expect?
		return self.performer.steps()

	def perform_thread(self):
		self.performer.play_music()

	def play_thread(self):
		self.performer.play()


