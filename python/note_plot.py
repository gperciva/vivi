#!/usr/bin/env python

from PyQt4 import QtGui, QtCore

class NotePlot(QtGui.QWidget):
	def __init__(self):
		QtGui.QWidget.__init__(self)
		self.setAutoFillBackground(True)
		self.setPalette(QtGui.QPalette( QtCore.Qt.white) )
		self.setMinimumHeight(100)
		self.forces = []
		self.mouse_x_begin = -1
		self.mouse_x_end = -1

	def set_data(self, forces, cats_out):
		self.forces = forces
		self.cats_out = cats_out
		self.mouse_x_begin = -1
		self.mouse_x_end = -1
		self.update()

	def mousePressEvent(self, event):
		self.mouse_x_begin = event.x()
		self.mouse_x_end = -1

	def mouseMoveEvent(self, event):
		self.mouse_x_end = event.x()
		self.update()

	def mouseReleaseEvent(self, event):
		self.mouse_x_end = event.x()
		selected = abs(self.mouse_x_begin - self.mouse_x_end)
		rel_length = float(selected) / self.width()
		if rel_length < 0.05:
			self.mouse_x_begin = -1
			self.mouse_x_end = -1
		self.update()

	def clear_selection(self):
		self.mouse_x_begin = -1
		self.mouse_x_end = -1

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

	def paintEvent(self, event):
		painter = QtGui.QPainter(self)
		if not self.forces:
			return

		if self.has_selection():
			self.mouseDraw(painter)

		maxforce = max(self.forces)

		top_margin = 10
		bottom_margin = 10
		height = self.height()

		xoffset = 0
		xscale = (self.width() - 0) / len(self.forces)
		yoffset = height - top_margin
		yscale = (-(height - top_margin - bottom_margin)) / maxforce

		painter.drawText( 15, self.height()-5,
			"Max force: %.3f" % maxforce)
		force_bar_height = maxforce / 12.0*height
		painter.fillRect(5, height - force_bar_height - 4,
			5, force_bar_height,
			QtCore.Qt.green)

		prev_x = 0
		prev_y = self.forces[0]*yscale + yoffset
		for i, force in enumerate(self.forces):
			cat_out = self.cats_out[i]

			x = i*xscale + xoffset
			y = self.forces[i]*yscale + yoffset
			painter.setPen(QtCore.Qt.black)
			painter.drawLine(prev_x, prev_y, x, y)
			prev_x = x
			prev_y = y

			if (cat_out == 0) or (cat_out == 4):
				direction = (2-cat_out)/2
				painter.setPen(QtCore.Qt.red)
				self.arrow(painter, x, y, direction)
			if (cat_out == 1) or (cat_out == 3):
				direction = 2-cat_out
				painter.setPen(QtCore.Qt.blue)
				self.arrow(painter, x, y, direction)

#			if (cat_out == 0) or (cat_out == 2):
#				direction = 1-cat_out
#				painter.setPen(QtCore.Qt.red)
#				self.arrow(painter, x, y, direction)
#			elif (cat_in == 0) or (cat_in == 2):
#				direction = 1-cat_in
#				painter.setPen(QtCore.Qt.blue)
#				self.arrow(painter, x, y, direction)

	def arrow(self, painter, x, y, direction):
		painter.drawLine(x, y, x+2, y+direction*10)
		painter.drawLine(x, y, x-2, y+direction*10)


	def mouseDraw(self, painter):
		width = self.mouse_x_end - self.mouse_x_begin
		painter.fillRect(self.mouse_x_begin, 0,
			width, self.height()-1,
			QtCore.Qt.yellow)


