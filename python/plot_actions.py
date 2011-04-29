#!/usr/bin/env python

from PyQt4 import QtGui, QtCore

class PlotActions(QtGui.QWidget):
	def __init__(self):
		QtGui.QWidget.__init__(self)
		self.setAutoFillBackground(True)
		self.setPalette(QtGui.QPalette( QtCore.Qt.white) )
		self.back = QtCore.Qt.white
		self.forces = []
		self.cats = []
		self.mouse_x_begin = -1
		self.mouse_x_end = -1
		self.highlight(False)

	def set_data(self, forces, cats):
		self.forces = [x[1] for x in forces]
		self.cats = [x[1] for x in cats]
		self.mouse_x_begin = -1
		self.mouse_x_end = -1
		self.update()

	def mousePressEvent(self, event):
		self.mouse_x_begin = event.x()
		self.mouse_x_end = -1
		QtGui.QWidget.mousePressEvent(self, event)

	def mouseMoveEvent(self, event):
		self.mouse_x_end = event.x()
		QtGui.QWidget.mousePressEvent(self, event)
		self.update()

	def mouseReleaseEvent(self, event):
		self.mouse_x_end = event.x()
		selected = abs(self.mouse_x_begin - self.mouse_x_end)
		rel_length = float(selected) / self.width()
		if rel_length < 0.05:
			self.mouse_x_begin = -1
			self.mouse_x_end = -1
		QtGui.QWidget.mousePressEvent(self, event)
		self.update()

	def clear_selection(self):
		self.mouse_x_begin = -1
		self.mouse_x_end = -1
		self.update()

	def get_selection(self):
		start = (min(self.mouse_x_begin, self.mouse_x_end)
			/ float(self.width()))
		duration = float(abs(self.mouse_x_begin - self.mouse_x_end)
			/ float(self.width()))
		return start, duration

	def has_selection(self):
		if ((self.mouse_x_begin >= 0) and
		    (self.mouse_x_end >= 0)):
			return True
		return False

	def highlight(self, do_highlight):
		if do_highlight:
			self.back = QtCore.Qt.white
		else:
			self.back = QtCore.Qt.lightGray
		self.update()

	def paintEvent(self, event):
		if not self.forces:
			return
		painter = QtGui.QPainter(self)
		# bad way of drawing the background, but I don't
		# feel like wading through more API docs to find
		# the right way
		painter.fillRect(1, 1, self.width()-1, self.height()-1, self.back)

		if self.has_selection():
			self.mouseDraw(painter)

		maxforce = max(self.forces)

		top_margin = 10
		bottom_margin = 10
		height = self.height()

		left_margin = 10
		right_margin = 10
		xscale = (float(self.width() - left_margin - right_margin)
					/ len(self.forces))
		yoffset = height - top_margin
		yscale = (-(height - top_margin - bottom_margin)) / maxforce

		prev_x = left_margin
		prev_y = self.forces[0]*yscale + yoffset
		for i, force in enumerate(self.forces):
			x = i*xscale + left_margin
			y = self.forces[i]*yscale + yoffset
			painter.setPen(QtCore.Qt.black)
			painter.drawLine(prev_x, prev_y, x, y)
			prev_x = x
			prev_y = y

		for i, cat in enumerate(self.cats):
			x = i*xscale + left_margin
			y = self.forces[i]*yscale + yoffset

			if (cat == 0) or (cat == 4):
				direction = (2-cat)/2
				painter.setPen(QtCore.Qt.red)
				self.arrow(painter, x, y, direction)
			if (cat == 1) or (cat == 3):
				direction = 2-cat
				painter.setPen(QtCore.Qt.blue)
				self.arrow(painter, x, y, direction)
			prev_x = x
			prev_y = y

	def arrow(self, painter, x, y, direction):
		painter.drawLine(x, y, x+2, y+direction*10)
		painter.drawLine(x, y, x-2, y+direction*10)


	def mouseDraw(self, painter):
		width = self.mouse_x_end - self.mouse_x_begin
		painter.fillRect(self.mouse_x_begin, 0,
			width, self.height()-1,
			QtCore.Qt.yellow)


