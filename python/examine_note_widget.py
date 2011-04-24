#!/usr/bin/python

from PyQt4 import QtGui, QtCore

import utils
import shared

import examine_note
import note_plot

class ExamineNoteWidget():
	#def __init__(self, parent):
	def __init__(self):
		#self.note_layout = note_layout
		#self.note_label = self.note_layout.itemAt(0).widget()
		self.note_plot = note_plot.NotePlot()
		#parent.layout().addWidget(self.note_plot, 1)
		#self.note_layout.addWidget(self.note_plot, 1)

		self.examine_note = examine_note.ExamineNote()
		self.got_zoom = False

	def load_file(self, filename):
		self.examine_note.load_file(filename)
		# FIXME: debug only
		self.note_plot.set_data(
			self.examine_note.note_forces,
			self.examine_note.note_cats_out,
		)

	def load_note(self, lily_line, lily_col):
		status = self.examine_note.load_note(lily_line, lily_col)
		if status:
			self.note_plot.set_data(
				self.examine_note.note_forces,
				self.examine_note.note_cats_out,
		#		self.examine_note.note_cats_in
				)
		else:
			self.note_label.setText("Not a rehearsed note!")
		return status

	def showHelp(self, text):
		self.note_label.setText(text)

	def show_note_info(self):
		disp = ''
		disp += "Note: st %i\tfinger %.3f\t\t\t" %(
			self.examine_note.note_st,
			self.examine_note.note_finger)
		disp += "  pos %.3f\tvel %.3f\n" %(
			self.examine_note.note_pos,
			self.examine_note.note_vel)

#		disp += "\n"
#		disp += utils.visualize_cats(
#			self.examine_note.note_cats_out, 20)
#		disp += "\n"
#		disp += utils.visualize_cats(
#			self.examine_note.note_cats_in, 20)
#		disp += "\n"
#
#		disp += "forces (unsorted):"
#		for i in range(len(self.examine_note.note_forces)):
#			f = self.examine_note.note_forces[i]
#			if (i % 16) == 0:
#				disp += '\n'
#			disp += "  %.2f" % (f)
		#disp += '\n'
		#disp += "median force: %.3f" % self.examine_note.note_force_median
		self.note_label.setText(disp)

	def opinion(self, cat):
		self.examine_note.opinion(cat)

	def play(self):
		print "examine note widget play", self.examine_note.wavfile
		if self.note_plot.has_selection():
			print "has selection"
			start, dur = self.get_zoom_seconds()
			#print "zoom in on: ", self.examine_note.wavfile
			utils.play(self.examine_note.wavfile,
				start, dur)
		else:
			utils.play(self.examine_note.wavfile)

	def get_zoom_seconds(self):
		start, dur = self.note_plot.get_selection()
		self.got_zoom = True
		return self.examine_note.get_seconds(start, dur)

	def get_zoom(self):
		start, dur = self.get_zoom_seconds()
		st = self.examine_note.note_st
		filename = self.examine_note.make_zoom_file(start, dur)
		return st, self.examine_note.level, filename

	def get_zoom_bare(self):
		start, dur = self.get_zoom_seconds()
		filename = self.examine_note.make_zoom_file(start, dur)
		return filename

