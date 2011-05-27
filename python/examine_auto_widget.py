#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
import examine_widget_gui

import glob

import utils
import shared

import examine_note_widget
import table_play_widget

# FIXME: temp for debugging
import scipy.stats


class ExamineAutoWidget(QtGui.QFrame):
	select_note = QtCore.pyqtSignal()

	def __init__(self, parent):
		QtGui.QFrame.__init__(self, parent, QtCore.Qt.Window)

		### setup GUI
		self.ui = examine_widget_gui.Ui_Frame()
		self.ui.setupUi(self)

		self.st = None
		self.dyn = None


	def examine(self, type, st, dyn, task_stable):
		self.st = st
		self.dyn = dyn

		self.task_stable = task_stable

		text = utils.st_to_text(self.st) + " string "
		self.ui.string_label.setText(text)

		text = utils.dyn_to_text(self.dyn)
		self.ui.dyn_label.setText(text)


		if type == "stable":
			self.setup_stable()
			self.ui.examine_type_label.setText("stable")

		self.show()


	def setup_stable(self):
		if not self.task_stable.examines:
			self.task_stable.get_stable_files_info()

		### CUT
		# setup table and gui
		self.table = table_play_widget.TablePlayWidget(self, [
			str("Low: %.3f" % self.task_stable.forces_initial[0]),
			"low 4", "low 7",
			str("Middle: %.3f" % self.task_stable.forces_initial[1]),
			"mid 4", "mid 7",
			str("High: %.3f" % self.task_stable.forces_initial[2]),
			"high 4", "high 7",
			])
		# clear previous widget if exists
		if self.ui.verticalLayout.count() == 2:
			self.ui.verticalLayout.takeAt(1)

		self.ui.verticalLayout.addWidget(self.table)

		self.table.action_play.connect(self.table_play)
		self.table.select_previous.connect(self.clear_select)
		self.table.select_new.connect(self.select_plot)


		num_rows = self.task_stable.num_rows
		num_counts = self.task_stable.num_counts

		self.table.clearContents()
		self.table.setRowCount(num_rows)

		for i in range(num_rows):
			item = QtGui.QTableWidgetItem()
			mod = i % num_counts + 1
			item.setText(str("%.2f-%i" % (self.task_stable.extras[i/num_counts], mod)))
			self.table.setVerticalHeaderItem(i, item)

		self.examines = self.task_stable.examines

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

