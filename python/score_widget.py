#!/usr/bin/env python
from PyQt4 import QtGui, QtCore
import popplerqt4

PAGE_TURN_MARGIN_PIXELS = 20

class ScoreWidget(QtGui.QLabel):
    note_click = QtCore.pyqtSignal(int, int, name='noteClick')

    def __init__(self):
        QtGui.QLabel.__init__(self)
        self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.resolution = 108

        self.image_width = 1 # actual value will be set later.
        self.image_height = 1
        self.pdf_links = None
        self.selected = None
        self.pdf = None

    def load_file(self, pdf_file):
        self.pdf = popplerqt4.Poppler.Document.load(pdf_file)
        self.pdf.setRenderHint(1)
        self.pdf.setRenderHint(2)
        self.pdf.setRenderHint(4)

        self.selected = None
        self.current_page = 0
        self.load_page()

    def load_page(self, page_num=None):
        if page_num is not None:
            self.current_page = page_num

        self.pdf_page = self.pdf.page(self.current_page)
        self.pdf_links = self.pdf_page.links()

        pdf_image = self.pdf_page.renderToImage(
            self.resolution, self.resolution)
        pdf_pixmap = QtGui.QPixmap.fromImage(pdf_image)
        self.setPixmap(pdf_pixmap)
        self.image_width = pdf_pixmap.width()
        self.image_height = pdf_pixmap.height()

    def can_back_page(self):
        return self.current_page > 0

    def can_next_page(self):
        return self.current_page < (self.pdf.numPages() - 1)

    def back_page(self):
        if self.can_back_page():
            self.load_page(self.current_page - 1)
            # TODO: ick, bad abstraction
            self.parent().parent().ensureVisible(0,0);

    def next_page(self):
        if self.can_next_page():
            self.load_page(self.current_page + 1)
            # TODO: ick, bad abstraction
            self.parent().parent().ensureVisible(0,0);

    def mousePressEvent(self, event):
        if not self.pdf_links:
            return
        click_point = event.posF()
        if click_point.x() < PAGE_TURN_MARGIN_PIXELS:
            self.back_page()
            return
        if click_point.x() > self.width() - PAGE_TURN_MARGIN_PIXELS:
            self.next_page()
            return
        click_point.setX( click_point.x() / self.image_width )
        click_point.setY( click_point.y() / self.image_height )
        for link in self.pdf_links:
            area = link.linkArea()
            if area.contains(click_point):
                url = str(link.url()).split(':')
                lily_line = int(url[2])
                lily_col = int(url[3])
                self.note_click.emit(lily_line, lily_col)
                self.selected = area
                self.update()
                break

    def draw_page_arrow(self, painter, x, direction):
        painter.fillRect( x, 0,
            PAGE_TURN_MARGIN_PIXELS, self.height()-1,
            QtGui.QColor("lightBlue"))
        for i in range(int(self.height() / 200)):
            y = i*200+100
            painter.fillRect(
                x + 5, y, PAGE_TURN_MARGIN_PIXELS-10, 3,
                QtGui.QColor("Blue"))
            ax = x + (PAGE_TURN_MARGIN_PIXELS/2 -
                direction*(PAGE_TURN_MARGIN_PIXELS/2))
            painter.fillRect(
                ax + 5*direction, y-5, 2, 13,
                QtGui.QColor("Blue"))

    def paintEvent(self, event):
        QtGui.QLabel.paintEvent(self, event)
        if not self.pdf:
            return
        painter = QtGui.QPainter(self)
        if self.can_back_page():
            self.draw_page_arrow(painter, 0, -1)
        if self.can_next_page():
            self.draw_page_arrow(painter, self.width()-PAGE_TURN_MARGIN_PIXELS, 1)

        if self.selected is not None:
            # TODO: I'm sure this can be done with a single function
            x_offset = 5
            y_offset = 12
            x = self.image_width * self.selected.x() - x_offset
            width = self.image_width * self.selected.width() + 2.5*x_offset
            y = self.image_height * self.selected.y() - y_offset
            height = self.image_height * self.selected.height() + 2*y_offset
            color = QtGui.QColor("yellow")
            color.setAlpha(200)
            painter.fillRect( x, y, width, height, color)


