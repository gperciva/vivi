#!/usr/bin/env python
import os
import shutil
import glob
from PyQt4 import QtCore

import dirs

STATE_COMPILE_LILYPOND = 1
LILYPOND_COMMAND = "lilypond \
  -I %s \
  -dinclude-settings=event-listener.ly \
  -o %s \
  %s"
#  -dinclude-settings=reduce-whitespace.ly \

class LilyPondCompile(QtCore.QThread):
	process_step = QtCore.pyqtSignal()
	done = QtCore.pyqtSignal()
	def __init__(self):
		QtCore.QThread.__init__(self)

		# TODO: clean this up
		self.ly_filename = None
		self.ly_basename = None

		self.mutex = QtCore.QMutex()
		self.condition = QtCore.QWaitCondition()
		self.state = 0
		self.start()

	def lily_file_needs_compile(self, ly_file):
		self.ly_basename = os.path.splitext(ly_file)[0]
		self.ly_filename = os.path.basename(self.ly_basename)
		ly_filename = os.path.splitext(
			os.path.basename(ly_file))[0]
		# TODO: what about identical filenames in
		# different directories?
		outfilename = os.path.join(dirs.files.get_music_dir(),
					ly_filename+'.pdf')
		if not os.path.isfile(outfilename):
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
		#dirname = os.path.dirname(self.ly_basename)
		dirname = "ly"

		#self.remove_old_files(dirname)
		self.remove_old_files(dirs.files.get_music_dir())
		self.process_step.emit()
		# make new files
		cmd = LILYPOND_COMMAND % (
			os.path.abspath(dirname),
			dirs.files.get_music_dir(),
			self.ly_filename+'.ly')
		os.system(cmd)
		self.process_step.emit()
		self.done.emit()

	def get_filename_pdf(self):
		return os.path.join(dirs.files.get_music_dir(),
			self.ly_filename+'.pdf')

	def get_filename_notes(self):
		notes_files = glob.glob(
			os.path.join(dirs.files.get_music_dir(),
			self.ly_filename+"*.notes"))
		return notes_files

