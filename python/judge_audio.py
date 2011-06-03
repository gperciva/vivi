#!/usr/bin/env python

from PyQt4 import QtGui, QtCore
import judge_audio_gui

NUM_CATEGORIES = 6 # including "unknown"
import utils

class JudgeAudio(QtGui.QFrame):
	judged_cat = QtCore.pyqtSignal(int, name='judged_cat')

	def __init__(self, main_layout):
		QtGui.QFrame.__init__(self)
		self.ui = judge_audio_gui.Ui_Frame()
		self.ui.setupUi(self)
		self.main_layout = main_layout
		self.use_layout = self.main_layout
		self.display(show=False)

		self.buttons = QtGui.QButtonGroup(self)
		for widget in self.ui.groupBox.findChildren(QtGui.QPushButton):
			self.buttons.addButton(widget)
		self.buttons.buttonClicked.connect(self.clicked)


	### basic GUI framework
	def display(self, parent=None, position=-1, show=True, main=False):
		if main:
			self.use_layout = self.main_layout
		elif parent:
			self.use_layout = parent
		if show:
			self.use_layout.insertWidget(position, self)
			self.show()
			self.setFocus()
		else:
			self.clearFocus()
			self.hide()
			if self.parent():
				self.parent().layout().removeWidget(self)
				if self.use_layout != self.main_layout:
					self.parent().table_focus()
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
		elif (key == 'q'):
			self.user_key(9)
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
		elif key == 8:
			utils.play(self.train_filename+'.wav')
		elif key == 9:
			self.judged_cat.emit(-1)

