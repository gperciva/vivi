#!/usr/bin/env python

from PyQt4 import QtGui, QtCore
import utils

class CollTable(QtGui.QTableWidget):
	action_play = QtCore.pyqtSignal()
	action_train = QtCore.pyqtSignal()
	action_info = QtCore.pyqtSignal()

	def __init__(self, parent):
		QtGui.QTableWidget.__init__(self, parent)
		self.parent = parent

		self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
		self.setProperty("showDropIndicator", False)
		self.setDragDropOverwriteMode(False)
		self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
		self.setObjectName("table")
		self.setColumnCount(2)
		self.setRowCount(0)

		item = QtGui.QTableWidgetItem()
		self.setHorizontalHeaderItem(0, item)
		item = QtGui.QTableWidgetItem()
		self.setHorizontalHeaderItem(1, item)

		self.horizontalHeaderItem(0).setText(QtGui.QApplication.translate("Dialog", "Opinion", None, QtGui.QApplication.UnicodeUTF8))
		self.horizontalHeaderItem(1).setText(QtGui.QApplication.translate("Dialog", "Predicted", None, QtGui.QApplication.UnicodeUTF8))

		self.setColumnWidth(0, 70)
		self.setColumnWidth(1, 430)

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


