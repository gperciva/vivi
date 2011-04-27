from PyQt4 import QtGui, QtCore

import plot_actions

class PlotMain(plot_actions.PlotActions):
	def __init__(self):
		plot_actions.PlotActions.__init__(self)

	def paintEvent(self, event):
		if not self.forces:
			return
		plot_actions.PlotActions.paintEvent(self, event)

		painter = QtGui.QPainter(self)

		maxforce = max(self.forces)
		painter.drawText( 15, self.height()-5,
			"Max force: %.3f" % maxforce)
		force_bar_height = maxforce / 12.0*self.height()
		painter.fillRect(2, self.height() - force_bar_height - 4,
			2, force_bar_height,
			QtCore.Qt.green)



