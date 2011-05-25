from PyQt4 import QtGui, QtCore

import plot_actions

# FIXME: shouldn't be here
import shared
import math

class PlotStable(plot_actions.PlotActions):
	def __init__(self):
		plot_actions.PlotActions.__init__(self)
		self.stability = 0.0
		self.areas = []

	def set_stability(self, stability):
		self.stability = stability
		self.cats_means = self.calc_stable_areas(self.cats)	

		self.stability = self.get_stability(self.cats_means)

	def calc_stable_areas(self, cats):
		# get cat_means
		cats_means = []
		length = shared.vivi_controller.CATS_MEAN_LENGTH
		filt = [-1] * length
		filt_index = 0
		for c in cats:
			filt[filt_index] = c
			filt_index += 1
			if filt_index == length:
				filt_index = 0
			if -1 in filt:
				cats_means.append(-1)
			else:
				mean = float(sum(filt)) / length
				mean = int(round(mean))
				cats_means.append(mean)
		return cats_means

	def get_stability(self,cats):
		direction = 1
		areas = []
		area = []
		zeros = 1
		for cat in cats:
			if cat < 0:
				continue
			err = 2-cat
			if err == 0:
				continue
			if err * direction > 0:
				area.append(err)
			else:
				if area:
					areas.append(area)
				area = []
				area.append(err)
				direction = math.copysign(1, err)
				zeros += 1
		if area:
			areas.append(area)
		stable = 1.0
		for a in areas:
			area_fitness = 1.0 / math.sqrt(len(a))
			stable *= area_fitness
#		return zeros
		return stable


	def paintEvent(self, event):
		if not self.forces:
			return
		plot_actions.PlotActions.paintEvent(self, event)

		painter = QtGui.QPainter(self)

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


		for i, cat in enumerate(self.cats_means):
			x = i*xscale + left_margin
			y = self.forces[i]*yscale + yoffset
			if cat < 2:
				y += 0.1*self.height()
			if cat > 2:
				y += -0.1*self.height()

			if (cat == 0) or (cat == 4):
				direction = (2-cat)/2
				painter.setPen(QtCore.Qt.yellow)
				self.arrow(painter, x, y, direction)
			if (cat == 1) or (cat == 3):
				direction = 2-cat
				painter.setPen(QtCore.Qt.green)
				self.arrow(painter, x, y, direction)

		painter.setPen(QtCore.Qt.darkRed)
		painter.drawText( 50, self.height()-5,
			"%.3f" % self.stability)


