#!/usr/bin/env python

from PyQt4 import QtGui, QtCore
import examine_widget_gui
import check_coll
import table_play_widget

import utils
import shared

class CompareColl(QtGui.QFrame):
	row_delete = QtCore.pyqtSignal(str, name="row_delete")
	row_retrain = QtCore.pyqtSignal(str, name="row_retrain")
	
	def __init__(self):
		QtGui.QFrame.__init__(self)
		# set up GUI
		self.ui = examine_widget_gui.Ui_Frame()
		self.ui.setupUi(self)

		self.check_coll = check_coll.CheckColl()

		self.table = table_play_widget.TablePlayWidget(self,
			["cat", "stars"])
		self.table.setColumnWidth(0, 40)
		self.table.setColumnWidth(1, 360)

		self.ui.verticalLayout.addWidget(self.table)

		self.setFocusPolicy(QtCore.Qt.StrongFocus)

		self.table.action_play.connect(self.table_play)
		self.table.action_delete.connect(self.table_row_delete)
		self.table.action_retrain.connect(self.table_row_retrain)
		self.table.action_quit.connect(self.table_quit)
		self.table.itemSelectionChanged.connect(self.selection_changed)
		self.ui.button_play.clicked.connect(self.table_play)

		# add extra buttons
		button = QtGui.QPushButton("re&train")
		self.ui.examine_commands.insertWidget(1, button)
		button.clicked.connect(self.table_row_retrain)
		button = QtGui.QPushButton("&delete")
		self.ui.examine_commands.insertWidget(2, button)
		button.clicked.connect(self.table_row_delete)


	def display(self):
		text = utils.st_to_text(self.st) + " string "
		self.ui.string_label.setText(text)

		text = utils.dyn_to_text(self.dyn)
		self.ui.dyn_label.setText(text)

		self.ui.examine_type_label.setText("collection")

	def compare(self, st, dyn, accuracy, coll):
		self.st = st
		self.dyn = dyn
		self.accuracy = accuracy
		self.display()

		self.check_coll.check(coll, self.st, self.dyn)
		self.data = list(self.check_coll.data)

		self.table.clearContents()
		self.table.setRowCount(len(self.data))
		for i, datum in enumerate(self.data):
			table_item = QtGui.QTableWidgetItem(datum[0])
			table_item.setTextAlignment(QtCore.Qt.AlignCenter)
			self.table.setItem(i, 0, table_item)
			table_item = QtGui.QTableWidgetItem(datum[1])
			table_item.setFont(QtGui.QFont("Andale Mono", 7))
			self.table.setItem(i, 1, table_item)
		self.table_focus()

	def table_focus(self):
		self.table.setFocus()
		self.show()

	def table_play(self):
		row = self.table.currentRow()
		if row >= 0:
			wavfile = self.data[row][2]
			utils.play(wavfile)

	def get_selected_filename(self):
		row = self.table.currentRow()
		col = self.table.currentColumn()

	def get_selected_filename(self):
		row = self.table.currentRow()
		wavfilename = self.data[row][2]
		filename = wavfilename[0:-4] # remove .wav
		return filename

	def selection_changed(self):
		filename = self.get_selected_filename()
		shared.examine_main.load_file(filename)
		shared.examine_main.load_note("")

	def table_row_delete(self):
		filename = self.get_selected_filename()
		row = self.table.currentRow()
		self.table.removeRow(row)
		self.data.pop(row)
		self.row_delete.emit(filename)

	def table_row_retrain(self):
		# TODO: update display with new category
		filename = self.get_selected_filename()
		self.row_retrain.emit(filename)

	def table_quit(self):
		shared.examine_main.reset()
		self.close()

