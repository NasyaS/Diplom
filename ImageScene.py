from PyQt5.QtGui import QBrush, QPen, QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsScene
from PyQt5 import QtCore
from PyQt5.QtCore import QSize, Qt
import numpy as np


class ImageScene():
	def __init__(self):
		self.full = False
		self.drawing = False
		self.path = ''
		self.coords = []
		img = QPixmap('start.png')
		self.current = QGraphicsScene(0, 0, img.size().width(), img.size().height())
		self.current.addItem(QGraphicsPixmapItem(img))

	def clear(self):
		self.current.clear()
		self.current.addItem(QGraphicsPixmapItem(self.pixmap))
		self.coords = []
		self.full = False

	def patent_size(self, x, y):
		self.sz = (x, y)

	def get_lenline(self):
		scale = lambda w, h: np.array((w*self.sz[0]/self.pixmap.size().width(), h*self.sz[1]/self.pixmap.size().height()))
		M1, M2 = [scale(*item) for item in self.coords]
		self.coords = []
		self.full = False
		return np.linalg.norm(M2-M1)

	def load(self, pixmap, path):
		self.pixmap, self.path = pixmap, path
		self.current = QGraphicsScene(0, 0, self.pixmap.size().width(), self.pixmap.size().height())
		self.current.addItem(QGraphicsPixmapItem(self.pixmap))
		self.drawing = True

	def addPoint(self, x, y):
		self.coords.append((x,y))
		if len(self.coords) == 2: self.full = True
		self.current.addEllipse(x-2.5, y-2.5, 5, 5, QPen(QtCore.Qt.red), QtCore.Qt.red)

	def connect(self):
		self.current.addLine(*self.coords[1], *self.coords[0], QPen(QtCore.Qt.red, 3, Qt.SolidLine, Qt.SquareCap, Qt.RoundJoin))
