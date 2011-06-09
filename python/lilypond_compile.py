#!/usr/bin/env python
import os
import glob
from PyQt4 import QtCore

STATE_COMPILE_LILYPOND = 1
LILYPOND_COMMAND = "lilypond -dinclude-settings=event-listener.ly %s"

class LilyPondCompile(QtCore.QThread):
	process_step = QtCore.pyqtSignal()
	done = QtCore.pyqtSignal()
	def __init__(self):
		QtCore.QThread.__init__(self)

		self.mutex = QtCore.QMutex()
		self.condition = QtCore.QWaitCondition()
		self.state = 0
		self.start()

	def lily_file_needs_compile(self, ly_file):
		self.ly_basename = os.path.splitext(ly_file)[0]
		if not os.path.isfile(self.ly_basename+'.pdf'):
			return True
		return False

	def run(self):
		while True:
			self.mutex.lock()
			self.condition.wait(self.mutex)
			if self.state == STATE_COMPILE_LILYPOND:
				self.call_lilypond_thread()
			self.mutex.unlock()

	def call_lilypond(self):
		self.state = STATE_COMPILE_LILYPOND
		self.condition.wakeOne()
		return 2

	def remove_old_files(self, dirname):
		for extension in ['*.notes', '*.pdf', '*.midi']:
			map(os.remove,
				glob.glob(os.path.join(dirname, extension)))

	def call_lilypond_thread(self):
		origdir = os.path.abspath(os.path.curdir)
		dirname = os.path.dirname(self.ly_basename)
		lily_file = os.path.basename(self.ly_basename+'.ly')

		self.remove_old_files(dirname)
		self.process_step.emit()
		# make new files
		os.chdir(dirname)
		cmd = LILYPOND_COMMAND % lily_file
		os.system(cmd)
		os.chdir(origdir)
		self.process_step.emit()
		self.done.emit()


