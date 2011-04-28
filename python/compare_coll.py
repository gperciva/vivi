#!/usr/bin/env python

from PyQt4 import QtGui, QtCore
import examine_widget_gui
import check_coll
import table_play_widget

import utils
import shared

class CompareColl(QtGui.QFrame):
	def __init__(self):
		QtGui.QFrame.__init__(self)
		self.ui = examine_widget_gui.Ui_Frame()
		self.ui.setupUi(self)

#		self.levels = levels.levels()

#		self.colls = [None, None, None, None]
		self.check_coll = check_coll.CheckColl()
		#for item in ["all", "outer", "inner", "mixed"]:
		#for item in ["outer", "inner"]:
		#	self.ui.cats_type_box.addItem(item)

##		self.ui.check_collection_button.clicked.connect(self.show_string)
#		self.ui.basic_train_button.clicked.connect(self.basic_train)
		self.table = table_play_widget.TablePlayWidget(self,
			["cat", "stars"])
		self.table.setColumnWidth(0, 40)
		self.table.setColumnWidth(1, 360)

		self.ui.verticalLayout.addWidget(
			self.table)

		self.setFocusPolicy(QtCore.Qt.StrongFocus)

		self.table.action_play.connect(self.table_play)
		self.table.itemSelectionChanged.connect(self.selection_changed)

	def set_string_train(self, string_train):
		self.string_train = string_train

	def display(self):
		text = utils.st_to_text(self.st)
		label = text+" string"
		text = utils.dyn_to_text(self.dyn)
		label += "  " + text
		self.ui.label.setText(str(label + "%.2f%%"%(self.accuracy)))

	def compare(self, st, dyn, accuracy, coll, ears):
		self.st = st
		self.dyn = dyn
		self.accuracy = accuracy
		self.display()

		self.check_coll.check(coll, self.st, self.dyn, ears)
		self.data = list(self.check_coll.data)

		self.table.clearContents()
		self.table.setRowCount(len(self.data))
		for i, datum in enumerate(self.data):
			table_item = QtGui.QTableWidgetItem(datum[0])
			table_item.setTextAlignment(QtCore.Qt.AlignCenter)
			self.table.setItem(i, 0, table_item)
			table_item = QtGui.QTableWidgetItem(datum[1])
			table_item.setFont(QtGui.QFont("Andale Mono",7))
			self.table.setItem(i, 1, table_item)
		self.setFocus()
		self.show()



#	def set_coll(self, i, coll):
#		self.colls[i] = coll
#
#	def check(self, check_st, inner, coll):
#		self.st = check_st
#		self.inner = inner
#		self.coll = coll
#
#		self.table.clearContents()
#		self.table.setRowCount(0)
#		self.show()
#		self.setFocus()
#		self.show_string()
#
#	def show_string(self):
#		self.check_coll.check(self.coll, self.st, self.inner)
#
#		self.table.setRowCount(len(self.check_coll.data))
#		for i, datum in enumerate(self.check_coll.data):
#			table_item = QtGui.QTableWidgetItem(datum[0])
#			self.table.setItem(i, 0, table_item)
#			table_item = QtGui.QTableWidgetItem(datum[1])
#			table_item.setFont(QtGui.QFont("Andale Mono"))
#			self.table.setItem(i, 1, table_item)
#
#	def basic_train(self):
#		self.string_train.set_note_label(self.ui.note_label)
#		self.string_train.basic_train()
#		self.setFocus()

	def table_play(self):
		row = self.table.currentRow()
		if row >= 0:
			wavfile = self.data[row][2]
			utils.play(wavfile)

	def table_delete_row(self):
		row = self.table.currentRow()
		if row >= 0:
			wavfile = self.data[row][2]
			self.table.removeRow(row)
			self.string_train.delete_file(self.st, self.dyn, wavfile)

#	def table_info(self):
#		row = self.table.currentRow()
#		if row >= 0:
#			wavfile = self.check_coll.get_filename(row)
#			self.ui.note_label.setText(wavfile)


	def keyPressEvent(self, event):
		try:
			key = chr(event.key())
		except:
			QtGui.QFrame.keyPressEvent(self, event)
			return
		key = key.lower()
#		if key == 'h':
#			disp = "help"
#			self.note_label.setText(disp)
		if key == 't':
			self.table_train()
		elif key == 'p':
			self.table_play()
		elif key == 'd':
			self.table_delete_row()
		else:
			QtGui.QFrame.keyPressEvent(self, event)

	def get_selected_filename(self):
		row = self.table.currentRow()
		col = self.table.currentColumn()

	def selection_changed(self):
		print "new selection"
		row = self.table.currentRow()
		col = self.table.currentColumn()
		wavfile = self.data[row][2]
		shared.examine_main.load_file(wavfile)
		shared.examine_main.load_note("")


