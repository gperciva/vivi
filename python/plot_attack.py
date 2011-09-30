from PyQt4 import QtGui, QtCore

import plot_actions

# FIXME: shouldn't be here
import shared
import math

class PlotAttack(plot_actions.PlotActions):
	def __init__(self):
		plot_actions.PlotActions.__init__(self)
		self.stability = 0.0
		self.areas = []

	def set_stability(self, stability, cats_means):
		self.stability = stability
		self.cats_means = cats_means

	def paintEvent(self, event):
		if not self.forces:
			return
		painter = QtGui.QPainter(self)
#		plot_actions.PlotActions.paintEvent(self, event)

		self.draw_background(painter)
		self.draw_selection(painter)

		maxforce = max(self.forces)
		top_margin = 10
		bottom_margin = 10
		height = self.height()
		left_margin = 10
		right_margin = 10
		xoffset = left_margin
		xscale = (float(self.width() - left_margin - right_margin)
					/ len(self.forces))
		yoffset = height - top_margin
		yscale = (-(height - top_margin - bottom_margin)) / maxforce

		self.draw_force_line(painter, xoffset, xscale, yoffset, yscale)

		for i, cat in enumerate(self.cats_means):
			x = i*xscale + left_margin
			y = self.forces[i]*yscale + yoffset
			self.arrow(painter, x, y, cat)
		painter.setPen(QtCore.Qt.darkRed)
		painter.drawText( 50, self.height()-5,
			"%.3f" % self.stability)

		#self.draw_max_force(painter)
#		self.draw_init_force(painter)

