#!/usr/bin/env python

from PyQt4 import QtCore
import performer
import utils

STATE_NULL = 0
STATE_RENDER_MUSIC = 1

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
			self.state = STATE_NULL
			self.done.emit()
			self.mutex.unlock()

	def load_file(self, filename):
		self.performer.load_file(filename)

	def play(self):
		utils.play(self.audio_filename)

	def play_music(self):
		self.state = STATE_RENDER_MUSIC
		self.condition.wakeOne()
		# TODO: is this the number of steps to expect?
		return self.performer.steps()

	def perform_thread(self):
		print "performing..."
		self.performer.play_music()
		print "... done"
		self.audio_filename = "audio.wav"

if __name__ == "__main__":
	app = QtCore.QCoreApplication([])
	foo = PerformerFeeder()
	foo.done.connect(app.quit)
	foo.load_file(["ly/example-input-unnamed-staff.notes"])
	foo.play_music()
	app.exec_()


