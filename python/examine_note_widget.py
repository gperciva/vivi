#!/usr/bin/python

from PyQt4 import QtGui, QtCore

import utils
import shared

import examine_note
import plot_actions
import plot_main

PLOT_ACTIONS = 1
PLOT_MAIN = 2

class ExamineNoteWidget():
	#def __init__(self, parent):
	def __init__(self, plot_type=PLOT_ACTIONS):
		#self.note_layout = note_layout
		#self.note_label = self.note_layout.itemAt(0).widget()
		if plot_type==PLOT_MAIN:
			self.plot_actions = plot_main.PlotMain()
		else:
			self.plot_actions = plot_actions.PlotActions()
		#parent.layout().addWidget(self.plot_actions, 1)
		#self.note_layout.addWidget(self.plot_actions, 1)

		self.examine_note = examine_note.ExamineNote()
		self.got_zoom = False

	def load_file(self, filename):
		self.examine_note.load_file(filename)

	def load_note(self, text):
		status = self.examine_note.load_note(text)
		if status:
			self.plot_actions.set_data(
				self.examine_note.note_forces,
				self.examine_note.note_cats,
				)
		else:
			self.note_label.setText("Not a rehearsed note!")
		return status

	def play(self):
		print "examine note widget play", self.examine_note.basename
		if not self.examine_note.basename:
			return
		if self.plot_actions.has_selection():
			print "has selection"
			start, dur = self.get_zoom_seconds()
			#print "zoom in on: ", self.examine_note.wavfile
			#utils.play(self.examine_note.wavfile,
			#	start, dur)
		else:
			start = self.examine_note.note_start
			dur = self.examine_note.note_length
		utils.play(self.examine_note.basename+'.wav',
			start, dur)

	def get_zoom_seconds(self):
		start, dur = self.plot_actions.get_selection()
		self.got_zoom = True
		return self.examine_note.get_seconds(start, dur)

	def get_zoom(self):
		start, dur = self.get_zoom_seconds()
		st = self.examine_note.note_st
		dyn = int(round(self.examine_note.note_dyn))
		filename = self.examine_note.make_zoom_file(start, dur)
		return st, dyn, filename

	def get_zoom_bare(self):
		start, dur = self.get_zoom_seconds()
		filename = self.examine_note.make_zoom_file(start, dur)
		return filename

