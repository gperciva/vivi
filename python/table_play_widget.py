#!/usr/bin/env python
""" extends QtGui.QTableWidget with actions: play, delete, retrain, quit """

#pylint: disable=C0103,R0904
# I can't change the overriden method names, nor the Qt naming scheme.

from PyQt4 import QtGui, QtCore

class TablePlayWidget(QtGui.QTableWidget):
	""" extends QtGui.QTableWidget with actions: play, delete, retrain, quit """
	action_play = QtCore.pyqtSignal()
	action_delete = QtCore.pyqtSignal()
	action_retrain = QtCore.pyqtSignal()
	action_quit = QtCore.pyqtSignal()
	select_previous = QtCore.pyqtSignal(int, int, name="select_previous")
	select_new = QtCore.pyqtSignal(int, int, name="select_new")

	def __init__(self, parent):
		""" constructor """
		QtGui.QTableWidget.__init__(self, parent)

		self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
		self.setProperty("showDropIndicator", False)
		self.setDragDropOverwriteMode(False)
		self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

		self.itemSelectionChanged.connect(self._changed)
		self.row_prev = -1
		self.col_prev = -1

	def set_column_names(self, column_names):
		""" sets number and names of columns """
		self.setColumnCount(len(column_names))
		for i, name in enumerate(column_names):
			item = QtGui.QTableWidgetItem()
			self.setHorizontalHeaderItem(i, item)
			self.horizontalHeaderItem(i).setText(name)

	def keyPressEvent(self, event):
		""" override default key event handler """
		try:
			key = chr(event.key())
		except ValueError:
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

	# I can't avoid having the event there
	#pylint: disable=W0613
	def closeEvent(self, event):
		""" override default close event handler """
		self.action_quit.emit()

	def _changed(self):
		""" when changing the selection, emit select_previous
			and select_new signals """
		self.select_previous.emit(self.row_prev, self.col_prev)
		self.row_prev = self.currentRow()
		self.col_prev = self.currentColumn()
		self.select_new.emit(self.currentRow(), self.currentColumn())

