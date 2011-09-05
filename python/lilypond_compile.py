#!/usr/bin/env python
import os
import shutil
import glob
from PyQt4 import QtCore

import subprocess
import filecmp

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

	def lily_file_needs_compile(self, ly_filename_orig):
		#self.ly_filename = os.path.abspath(ly_filename)
		self.ly_filename = os.path.join(dirs.files.get_music_dir(),
			ly_filename_orig)
		self.ly_basename = os.path.splitext(self.ly_filename)[0]
		self.ly_dirname = os.path.dirname(self.ly_filename)
		self.ly_dirname_orig = os.path.abspath(
			os.path.dirname(ly_filename_orig))
		if not os.path.isdir(self.ly_dirname):
			os.makedirs(self.ly_dirname)
		if (os.path.isfile(self.ly_filename) and
			filecmp.cmp(ly_filename_orig, self.ly_filename)):
			return False
		shutil.copy(ly_filename_orig, self.ly_filename)
		return True

	def remove_old_files(self, basename):
		for extension in ['*.notes', '*.pdf', '*.midi', '*.log']:
			map(os.remove,
				glob.glob(basename+extension))

	def call_lilypond_thread(self):
		origdir = os.path.abspath(os.path.curdir)
		self.remove_old_files(self.ly_basename)

		self.process_step.emit()

		logfile = open(self.ly_basename+'.log', 'w')
		# make new files
		cmd = LILYPOND_COMMAND % (
			self.ly_dirname_orig,
			self.ly_dirname,
			self.ly_filename)
		cmd = cmd.split()
		p = subprocess.Popen(cmd, stdout=logfile,
			stderr=logfile)
		p.wait()
		logfile.close()
		
		self.process_step.emit()
		self.done.emit()

	def get_filename_pdf(self):
		return os.path.join(dirs.files.get_music_dir(),
			self.ly_basename+'.pdf')

	def get_filename_notes(self):
		notes_files = glob.glob(
			os.path.join(dirs.files.get_music_dir(),
			self.ly_basename+"*.notes"))
		return notes_files

