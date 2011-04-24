#!/usr/bin/env python

from PyQt4 import QtGui, QtCore
import utils

class CollTable(QtGui.QTableWidget):
	action_play = QtCore.pyqtSignal()
	action_train = QtCore.pyqtSignal()
	action_info = QtCore.pyqtSignal()
	clear_select = QtCore.pyqtSignal(int, int, name="clear_select")
	select_cell = QtCore.pyqtSignal(int, int, name="select_cell")

	def __init__(self, parent, column_names):
		QtGui.QTableWidget.__init__(self, parent)
		self.parent = parent

		self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
		self.setProperty("showDropIndicator", False)
		self.setDragDropOverwriteMode(False)
		self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
		self.setObjectName("table")
		self.setColumnCount(len(column_names))
		self.setRowCount(0)

		self.itemSelectionChanged.connect(self.changed)
		self.prevRow = 0
		self.prevCol = 0


		for i, name in enumerate(column_names):
			item = QtGui.QTableWidgetItem()
			self.setHorizontalHeaderItem(i, item)
			self.horizontalHeaderItem(i).setText(name)
			# not relevant to names, but oh well
			self.setColumnWidth(i, 400)
		# isn't working?
		#self.resizeRowsToContents()

	def keyPressEvent(self, event):
		try:
			key = chr(event.key())
		except:
			QtGui.QTableWidget.keyPressEvent(self, event)
			return
		key = key.lower()
		if key == 't':
			self.action_train.emit()
		elif key == 'p':
			self.action_play.emit()
		elif key == 'i':
			self.action_info.emit()
		else:
			self.parent.keyPressEvent(event)
		QtGui.QTableWidget.keyPressEvent(self, event)

	def changed(self):
		if ((self.currentRow != self.prevRow) or
		    (self.currentCol != self.prevCol)):
			self.clear_select.emit(self.prevRow, self.prevCol)
		self.prevRow = self.currentRow()
		self.prevCol = self.currentColumn()
		self.select_cell.emit(self.currentRow(), self.currentColumn())

