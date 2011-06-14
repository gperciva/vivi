#!/usr/bin/env python
from PyQt4 import QtGui, QtCore
import popplerqt4

class ScoreWidget(QtGui.QLabel):
	note_click = QtCore.pyqtSignal(int, int, name='noteClick')

	def __init__(self, parent):
		QtGui.QLabel.__init__(self)
		parent.setWidget(self)
		self.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
		self.resolution = 108

		self.image_width = 1 # actual value will be set later.
		self.image_height = 1
		self.pdf_links = None

	def load_file(self, pdf_file):
		self.pdf = popplerqt4.Poppler.Document.load(pdf_file)
		self.pdf.RenderHint(1)
		self.pdf.RenderHint(2)
		self.pdf.RenderHint(3)
		self.load_page(0)

	def load_page(self, page_num=0):
		self.page_num = page_num

		self.pdf_page = self.pdf.page(0)
		self.pdf_links = self.pdf_page.links()

		pdf_image = self.pdf_page.renderToImage(
			self.resolution, self.resolution)
		pdf_pixmap = QtGui.QPixmap.fromImage(pdf_image)
		self.setPixmap(pdf_pixmap)
		self.image_width = pdf_pixmap.width()
		self.image_height = pdf_pixmap.height()

	def mousePressEvent(self, event):
		if not self.pdf_links:
			return
		click_point = event.posF()
		click_point.setX( click_point.x() / self.image_width )
		click_point.setY( click_point.y() / self.image_height )
		for link in self.pdf_links:
			area = link.linkArea()
			if area.contains(click_point):
				url = str(link.url()).split(':')
				lily_line = int(url[2])
				lily_col = int(url[3])
				self.note_click.emit(lily_line, lily_col)
				break

