#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
import examine_auto_gui

import glob

import utils
import shared

import examine_note_widget
import coll_table

class ExamineAutoWidget(QtGui.QFrame):

	def __init__(self):
		QtGui.QFrame.__init__(self)

		### setup GUI
		self.ui = examine_auto_gui.Ui_Frame()
		self.ui.setupUi(self)

		self.st = None
		self.dyn = None
		

	def examine(self, type, st, dyn):
		self.st = st
		self.dyn = dyn
		self.ui.label.setText("Examining: type %s   string %i   dynamic %i"
			% (type, st, dyn))

		if type == "stable":
			self.setup_stable()
			
		self.show()


	def setup_stable(self):
		bbd = shared.dyns.get_distance(self.dyn)
		bv = shared.dyns.get_velocity(self.dyn)
		files = glob.glob("auto/stable_%i_0.000_%.3f_?????_%.3f_*.wav"
			% (self.st, bbd, bv))
		files.sort()

		self.data = {}
		# TODO: really bad abuse of dictionaries
		for i, datum in enumerate(files):
			params, extra, count = shared.files.get_audio_params_extra(datum)
			if not params.bow_force in self.data:
				self.data[params.bow_force] = {}
			bf = self.data[params.bow_force]
			if not extra in bf:
				bf[extra] = []
			counts = bf[extra]
			counts.append(datum)

		forces_initial = self.data.keys()
		forces_initial.sort()

		self.table = coll_table.CollTable(self, [
			str("Low: %.3f" % forces_initial[0]),
			"", "",
			str("Middle: %.3f" % forces_initial[1]),
			"", "",
			str("High: %.3f" % forces_initial[2]),
			"", "",
			])
		self.ui.verticalLayout.addWidget(self.table)
		self.setFocusPolicy(QtCore.Qt.StrongFocus)

		self.table.action_play.connect(self.table_play)
		self.table.action_train.connect(self.table_train)
		self.table.clear_select.connect(self.clear_select)
		self.table.select_cell.connect(self.select_plot)

		num_rows = len(files)/3
		self.table.clearContents()
		self.table.setRowCount(num_rows)
		self.examines = [None]*num_rows
		for i in range(num_rows):
			self.examines[i] = []

		# TODO: really bad abuse of dictionaries
		keys_bf = self.data.keys()
		keys_bf.sort()
		for i, bf in enumerate(keys_bf):
			keys_extra = self.data[bf].keys()
			keys_extra.sort()
			for j, extra in enumerate(keys_extra):
				counts = self.data[bf][extra]

				for k, filename in enumerate(counts):
					for fm in range(3):
						examine = examine_note_widget.ExamineNoteWidget()
						examine.load_file(filename)
						to_find = "finger_midi_index %i" % fm
						examine.load_note(to_find)
						col = 3*i+fm
						row = 3*j+k
						#print row, col
						self.table.setCellWidget(row, col, examine.plot_actions)
						self.table.setRowHeight(row, 600.0/9)

						self.examines[row].append(examine)

		self.setFocus()
		self.show()


	def table_play(self):
		row = self.table.currentRow()
		col = self.table.currentColumn()
		print "table_play:", row, col
		if row >= 0:
			self.examines[row][col].play()

	def table_train(self):
		row = self.table.currentRow()
		col = self.table.currentColumn()
		print "table train:", row, col
		if row >= 0:
			filename = self.examines[row][col].get_zoom_bare()
			print "train ", filename
			#self.examine.load_file(wavfile)
			#self.string_train.set_note_label(self.ui.note_label)
			#self.string_train.retrain(self.st, self.dyn, wavfile)

	def clear_select(self, row, col):
		self.examines[row][col].plot_actions.clear_selection()
		self.examines[row][col].plot_actions.highlight(False)

	def select_plot(self, row, col):
		self.examines[row][col].plot_actions.highlight(True)

