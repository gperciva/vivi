#!/usr/bin/env python

from PyQt4 import QtGui, QtCore

class TablePlayWidget(QtGui.QTableWidget):
	action_play = QtCore.pyqtSignal()
	action_delete = QtCore.pyqtSignal()
	action_retrain = QtCore.pyqtSignal()
	action_quit = QtCore.pyqtSignal()
	select_previous = QtCore.pyqtSignal(int, int, name="select_previous")
	select_new = QtCore.pyqtSignal(int, int, name="select_new")

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
		elif key == 't':
			self.action_retrain.emit()
		elif key == 'd':
			self.action_delete.emit()
		elif key == 'q':
			self.closeEvent(None)
		else:
			QtGui.QTableWidget.keyPressEvent(self, event)

	def closeEvent(self, event):
		self.action_quit.emit()

	def changed(self):
		self.select_previous.emit(self.prevRow, self.prevCol)
		self.prevRow = self.currentRow()
		self.prevCol = self.currentColumn()
		self.select_new.emit(self.currentRow(), self.currentColumn())

