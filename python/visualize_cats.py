#!/usr/bin/env python

from PyQt4 import QtGui, QtCore

import vivi_defines

class VisualizeCats(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setAutoFillBackground(True)
        self.setPalette(QtGui.QPalette( QtCore.Qt.white) )
        self.highlight(False)

    def set_data(self, user_cat, cats):
        self.user_cat = user_cat
        self.cats = cats
        self.update()

    def highlight(self, do_highlight):
        if do_highlight:
            self.back = QtCore.Qt.lightGray
        else:
            self.back = QtCore.Qt.white
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        pen = painter.pen()

        # bad way of drawing the background, but I don't
        # feel like wading through more API docs to find
        # the right way
        painter.fillRect(0, 0, self.width(), self.height(), self.back)

        x_center = self.width() / 2.0
        x_scale = self.width() / float(vivi_defines.CATEGORIES_NUMBER + 1)

        # draw actual user category
        pen.setColor(QtCore.Qt.blue)
        pen.setWidth(1)
        painter.setPen(pen)
        for i in range(len(self.cats)):
            y = i * self.height() / float(len(self.cats))
            x = int(x_center + self.user_cat * x_scale)
            #if self.user_cat == vivi_defines.CATEGORY_WEIRD:
            #    x = int(x_center)
            painter.drawPoint(x,y)

        # draw predicted cat
        for i, cat in enumerate(self.cats):
            y = i * self.height() / len(self.cats)
            x = int(x_center + cat * x_scale)
            if x < 0:
                x = 0
            elif x >= self.width():
                x = self.width() - 1

            #if cat == vivi_defines.CATEGORY_WEIRD:
            #    x = int(x_center)

            delta = abs(cat - self.user_cat) / 0.5
            delta_clipped = min(delta, 1.0)
            pen.setColor(QtGui.QColor(
                255*delta_clipped, 255*(1-delta_clipped), 0))
            pen.setWidth(delta_clipped*3)
            painter.setPen(pen)
            painter.drawPoint(x,y)

