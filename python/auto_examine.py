#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
import auto_examine_gui

import glob

import utils

import examine_note_widget
import coll_table

# TODO: fix name
class AutoExamine(QtGui.QFrame):

	def __init__(self):
		QtGui.QFrame.__init__(self)

		### setup GUI
		self.ui = auto_examine_gui.Ui_Frame()
		self.ui.setupUi(self)
		self.show()


		self.files = glob.glob("auto/stable_*.wav")
		self.files.sort()
#		print self.files
		self.data = map(
			lambda(x): (0, x[5:], x),
			self.files)

		self.examine = examine_note_widget.ExamineNoteWidget(self)

		self.table = coll_table.CollTable(self)
		self.ui.verticalLayout.insertWidget(
			self.ui.verticalLayout.count()-1,
			self.table, 1)
		self.setFocusPolicy(QtCore.Qt.StrongFocus)

		self.table.action_play.connect(self.table_play)
		self.table.action_train.connect(self.table_train)

		self.table.clearContents()
		self.table.setRowCount(len(self.data))
		for i, datum in enumerate(self.data):
			table_item = QtGui.QTableWidgetItem(datum[0])
			table_item.setTextAlignment(QtCore.Qt.AlignCenter)
			self.table.setItem(i, 0, table_item)
			table_item = QtGui.QTableWidgetItem(datum[1])
			table_item.setFont(QtGui.QFont("Andale Mono"))
			self.table.setItem(i, 1, table_item)
		self.setFocus()
		self.show()


	def table_play(self):
		row = self.table.currentRow()
		if row >= 0:
			wavfile = self.data[row][2]
			print "playing", wavfile
			utils.play(wavfile)

	def table_train(self):
		row = self.table.currentRow()
		if row >= 0:
			wavfile = self.data[row][2]
			self.examine.load_file(wavfile)
			#self.string_train.set_note_label(self.ui.note_label)
			#self.string_train.retrain(self.st, self.dyn, wavfile)


