#!/usr/bin/env python

from PyQt4 import QtGui, QtCore
import judge_audio_gui

NUM_CATEGORIES = 6 # including "unknown"
import utils

class JudgeAudio(QtGui.QFrame):
	judged_cat = QtCore.pyqtSignal(int, name='judged_cat')

	def __init__(self, mainlayout):
		QtGui.QFrame.__init__(self)
		self.ui = judge_audio_gui.Ui_Frame()
		self.ui.setupUi(self)
		self.mainlayout = mainlayout
		self.display(show=False)

		self.buttons = QtGui.QButtonGroup(self)
		for widget in self.ui.groupBox.findChildren(QtGui.QPushButton):
			self.buttons.addButton(widget)
		self.buttons.buttonClicked.connect(self.clicked)


	### basic GUI framework

	def display(self, parent=None, position=-1, show=True):
		if show:
			if parent:
				parent.insertWidget(position, self)
			else:
				self.mainlayout.addWidget(self)
			self.show()
			self.setFocus()
		else:
			self.clearFocus()
			self.hide()
			if self.parent():
				self.parent().layout().removeWidget(self)
			self.setParent(None)

	def clicked(self, event):
		self.user_key(int(event.objectName()[11]))

	def keyPressEvent(self, event):
		try:
			key = chr(event.key())
		except:
			QtGui.QFrame.keyPressEvent(self, event)
			return
		key = key.lower()
		if (key >= '0') and (key <= '9'):
			self.user_key(int(key))
		else:
			QtGui.QFrame.keyPressEvent(self, event)


	### actual code
	def user_judge(self, train_filename):
		self.train_filename = train_filename
		self.display()
		utils.play(self.train_filename+'.wav')

	def user_key(self, key):
		if (key > 0) and (key <= NUM_CATEGORIES):
			self.judged_cat.emit(key)
#			self.display(show=False)
		elif key == 8:
			utils.play(self.train_filename)
		elif key == 9:
			self.judged_cat.emit(-1)
#			self.display(show=False)

