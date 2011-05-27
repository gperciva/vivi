#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
import examine_widget_gui

import glob

import utils
import shared

import examine_note_widget
import table_play_widget

# FIXME: temp for debugging
import scipy


class ExamineAutoWidget(QtGui.QFrame):
	select_note = QtCore.pyqtSignal()

	def __init__(self, parent):
		QtGui.QFrame.__init__(self, parent, QtCore.Qt.Window)

		### setup GUI
		self.ui = examine_widget_gui.Ui_Frame()
		self.ui.setupUi(self)

		self.st = None
		self.dyn = None


	def examine(self, type, st, dyn):
		self.st = st
		self.dyn = dyn

		text = utils.st_to_text(self.st) + " string "
		self.ui.string_label.setText(text)

		text = utils.dyn_to_text(self.dyn)
		self.ui.dyn_label.setText(text)


		if type == "stable":
			self.setup_stable()
			self.ui.examine_type_label.setText("stable")

		self.show()


	def setup_stable(self):
		files = shared.files.get_stable_files(self.st, self.dyn)

		# 3 notes per file, 9 notes per line
		num_rows = 3*len(files)/9

		# initialize 2d array
		self.examines = []
		for i in range(num_rows):
			self.examines.append([])
			for j in range(9):
				examine = examine_note_widget.ExamineNoteWidget(
					examine_note_widget.PLOT_STABLE)
				self.examines[i].append(examine)

		# variables about the files
		finger_midi_indices= range(3)
		self.forces_initial = []
		self.extras = []
		self.counts = []

		# get info about the files
		for filename in files:
			params, extra, count = shared.files.get_audio_params_extra(filename)
			force = params.bow_force
			if not force in self.forces_initial:
				self.forces_initial.append(force)
			if not extra in self.extras:
				self.extras.append(extra)
			if not count in self.counts:
				self.counts.append(count)

		num_counts = len(self.counts)

		for filename in files:
			params, extra, count = shared.files.get_audio_params_extra(filename)
			force = params.bow_force
			# and setup self.examines
			row = num_counts*self.extras.index(extra) + self.counts.index(count)
			col_base = 3*self.forces_initial.index(force)
			for fmi in finger_midi_indices:
				col = col_base+fmi
#				print row, col, fmi, filename
				print filename
				self.examines[row][col].load_file(filename[0:-4])
				to_find = "finger_midi_index %i" % fmi
				self.examines[row][col].load_note(to_find)

		# setup table and gui
		self.table = table_play_widget.TablePlayWidget(self, [
			str("Low: %.3f" % self.forces_initial[0]),
			"low 4", "low 7",
			str("Middle: %.3f" % self.forces_initial[1]),
			"mid 4", "mid 7",
			str("High: %.3f" % self.forces_initial[2]),
			"high 4", "high 7",
			])
		# clear previous widget if exists
		if self.ui.verticalLayout.count() == 2:
			self.ui.verticalLayout.takeAt(1)

		self.ui.verticalLayout.addWidget(self.table)

		self.table.action_play.connect(self.table_play)
		self.table.select_previous.connect(self.clear_select)
		self.table.select_new.connect(self.select_plot)


		self.table.clearContents()
		self.table.setRowCount(num_rows)

		for i in range(num_rows):
			item = QtGui.QTableWidgetItem()
			mod = i % num_counts + 1
			item.setText(str("%.2f-%i" % (self.extras[i/num_counts], mod)))
			self.table.setVerticalHeaderItem(i, item)


		# populate table
		for row in range(num_rows):
			for col in range(9):
				self.table.setCellWidget(row, col,
					self.examines[row][col].plot_actions)
				self.table.setRowHeight(row, 50.0)
				if col % 3 == 0 and col > 0:
					self.examines[row][col].plot_actions.set_border([0,0,0,1])
				if col % 3 == 2 and col < 8:
					self.examines[row][col].plot_actions.set_border([0,1,0,0])
				if row % num_counts == 0 and row > 0:
					self.examines[row][col].plot_actions.set_border([1,0,0,0])
				if row % num_counts == (num_counts-1) and row < num_rows:
					self.examines[row][col].plot_actions.set_border([0,0,1,0])

		# find "most stable" rows
		print "stables:"
		for block in range(num_rows/num_counts):
			block_vals = []
			for col_block in range(3):
				vals = []
				for count in range(num_counts):
					cvs = []
					for col_i in range(3):
						row = num_counts*block + count
						col = 3*col_block+col_i
						cv = self.examines[row][col].plot_actions.stability
						cvs.append(cv)
					vals.append( scipy.median(cvs) )
			#	row_stable = self.examines[row][0].plot_actions.stability
				#print vals
				row_stable = scipy.mean(vals)
				block_vals.append(row_stable)
			print block, "%.3f" % scipy.mean(block_vals)

		return
		# FIXME: move this somewhere else
		for i in range(num_rows):
			values = []
			muls = 1.0
			for j in range(9):
				val = self.examines[i][j].plot_actions.stability
				mul = 1.0 - val
				muls *= mul
				values.append(val)
			print ("%.3f\t%.3f\t%.3f" % (
				scipy.mean(values), scipy.median(values), mul
			))
			if i%3 == 2:
				print

		#self.setFocus()
		self.show()


	def table_play(self):
		row = self.table.currentRow()
		col = self.table.currentColumn()
		#print "table_play:", row, col
		if row >= 0 and col >= 0:
			self.examines[row][col].play()

	def table_train(self):
		row = self.table.currentRow()
		col = self.table.currentColumn()
#		print "table train:", row, col
#		if row >= 0:
#			filename = self.examines[row][col].get_zoom_bare()
#			print "train ", filename
			#self.examine.load_file(wavfile)
			#self.string_train.set_note_label(self.ui.note_label)
			#self.string_train.retrain(self.st, self.dyn, wavfile)

	def clear_select(self, row, col):
		self.examines[row][col].plot_actions.clear_selection()
		self.examines[row][col].plot_actions.highlight(False)

	def select_plot(self, row, col):
		self.examines[row][col].plot_actions.highlight(True)
		#print self.examines[row][col].examine_note.basename
		self.select_note.emit()

	def get_selected_filename(self):
		row = self.table.currentRow()
		col = self.table.currentColumn()
		if row >= 0 and col >= 0:
			examine = self.examines[row][col]
			return examine.examine_note.basename, examine.examine_note.note_text
		return None

#	def keyPressEvent(self, event):
#		print "examine note auto, key event:", event
		#QtGui.QFrame.keyPressEvent(self.parent, event)
		#self.parent.keyPressEvent(event)
		#QtCore.QCoreApplication.sendEvent(event)

