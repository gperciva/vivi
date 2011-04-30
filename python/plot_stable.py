from PyQt4 import QtGui, QtCore

import plot_actions

class PlotStable(plot_actions.PlotActions):
	def __init__(self):
		plot_actions.PlotActions.__init__(self)

	def set_stability(self, stability):
		self.stability = stability

	def paintEvent(self, event):
		if not self.forces:
			return
		plot_actions.PlotActions.paintEvent(self, event)

		painter = QtGui.QPainter(self)

		painter.setPen(QtCore.Qt.darkRed)
		painter.drawText( 30, self.height()-5,
			"%.3f" % self.stability)



