#!/usr/bin/env python

from PyQt4 import QtGui, QtCore

import vivi_defines

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
        self.border_extra = [0,0,0,0]

    def reset(self):
        self.back = QtCore.Qt.white
        self.forces = []
        self.cats = []
        self.mouse_x_begin = -1
        self.mouse_x_end = -1
        self.highlight(False)
        self.border_extra = [0,0,0,0]

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

    def set_border(self, border_extra):
        for i, b in enumerate(border_extra):
            if b==1:
                self.border_extra[i] = 1
            elif b==-1:
                self.border_extra[i] = 0

    def paintEvent(self, event):
        if not self.forces:
            return
        painter = QtGui.QPainter(self)
        pen = painter.pen()

        self.draw_background(painter)
        self.draw_selection(painter)

        maxforce = max(self.forces)

        top_margin = 15
        bottom_margin = 15
        height = self.height()

        left_margin = 10
        right_margin = 10
        xoffset = left_margin
        xscale = (float(self.width() - left_margin - right_margin)
                    / len(self.forces))
        yoffset = height - top_margin
        yscale = (-(height - top_margin - bottom_margin)) / maxforce

        self.draw_force_line(painter, xoffset, xscale, yoffset, yscale)

        for i, cat in enumerate(self.cats):
            x = i*xscale + left_margin
            y = self.forces[i]*yscale + yoffset

            self.arrow(painter, x, y, cat)

    def arrow(self, painter, x, y, cat):
        if cat == vivi_defines.CATEGORY_NULL:
            return
        scale = 0.05*self.height()
        direction = -1 if cat> 0 else 1
        cat_clipped = min( abs(cat)/2.0, 1.0)
        cat_scale = cat_clipped ** 0.3
        pen = painter.pen()

        #red = 255*2*min(cat_clipped, 0.5)
        red = 255*2*abs(cat_clipped - 0.5)
        green = 255*(1 - 2*max(cat_clipped-0.5, 0))
        blue = 0
        #print cat_clipped, '\t', red, '\t', green
        pen.setColor(QtGui.QColor(red, green, blue))
        painter.setPen(pen)
        for left_right in [-1, 1]:
            painter.drawLine(x, y,
                x + scale*left_right*cat_scale,
                y + 3*scale*direction*cat_scale)
        

    def draw_background(self, painter):
        # bad way of drawing the background, but I don't
        # feel like wading through more API docs to find
        # the right way
        painter.fillRect(0, 0, self.width(), self.height(), self.back)

        # draw any extra borders
        if self.border_extra[0]:
            painter.drawLine(0,0,self.width()-1,0)
        if self.border_extra[1]:
            painter.drawLine(self.width()-1,0,self.width()-1,self.height()-1)
        if self.border_extra[2]:
            painter.drawLine(self.width()-1,self.height()-1, 0, self.height()-1)
        if self.border_extra[3]:
            painter.drawLine(0, self.height()-1, 0, 0)


    def draw_force_line(self, painter, xoffset, xscale, yoffset, yscale):
        painter.setPen(QtCore.Qt.black)
        prev_x = xoffset
        prev_y = self.forces[0]*yscale + yoffset
        for i, force in enumerate(self.forces):
            x = i*xscale + xoffset
            y = self.forces[i]*yscale + yoffset
            painter.drawLine(prev_x, prev_y, x, y)
            prev_x = x
            prev_y = y


    def draw_selection(self, painter):
        if self.has_selection():
            width = self.mouse_x_end - self.mouse_x_begin
            painter.fillRect(self.mouse_x_begin, 0, width, self.height()-1,
                QtCore.Qt.yellow)

    def draw_max_force(self, painter):
        painter.setPen(QtCore.Qt.blue)
        maxforce = max(self.forces)
        painter.drawText( 15, 15,
            "Initial force: %.3f" % maxforce)
#        force_bar_height = maxforce / 12.0*self.height()
#        painter.fillRect(2, self.height() - force_bar_height - 4,
#            2, force_bar_height,
#            QtCore.Qt.green)

    def draw_init_force(self, painter):
        painter.setPen(QtCore.Qt.blue)
        maxforce = self.forces[0]
        painter.drawText( 15, 15,
            "Initial force: %.3f" % maxforce)
#        force_bar_height = maxforce / 12.0*self.height()
#        painter.fillRect(2, self.height() - force_bar_height - 4,
#            2, force_bar_height,
#            QtCore.Qt.green)

