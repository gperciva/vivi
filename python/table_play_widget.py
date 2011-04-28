#!/usr/bin/env python

from PyQt4 import QtGui, QtCore

class TablePlayWidget(QtGui.QTableWidget):
	action_play = QtCore.pyqtSignal()
	clear_select = QtCore.pyqtSignal(int, int, name="clear_select")

	def __init__(self, parent, column_names):
		QtGui.QTableWidget.__init__(self, parent)
		self.parent = parent

		self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
		self.setProperty("showDropIndicator", False)
		self.setDragDropOverwriteMode(False)
		self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
		self.setColumnCount(len(column_names))
		self.setRowCount(0)

		self.itemSelectionChanged.connect(self.changed)
		self.prevRow = 0
		self.prevCol = 0

		for i, name in enumerate(column_names):
			item = QtGui.QTableWidgetItem()
			self.setHorizontalHeaderItem(i, item)
			self.horizontalHeaderItem(i).setText(name)

	def keyPressEvent(self, event):
		try:
			key = chr(event.key())
		except:
			QtGui.QTableWidget.keyPressEvent(self, event)
			return
		key = key.lower()
		if key == 'p':
			self.action_play.emit()
		else:
			QtGui.QTableWidget.keyPressEvent(self, event)

	def changed(self):
		if ((self.currentRow != self.prevRow) or
		    (self.currentCol != self.prevCol)):
			self.clear_select.emit(self.prevRow, self.prevCol)

