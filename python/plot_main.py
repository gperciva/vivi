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
        self.draw_max_force(painter)


