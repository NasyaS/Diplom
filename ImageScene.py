from PIL import ExifTags, Image
from PyQt5.QtGui import QBrush, QPen, QPixmap
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsScene
from PyQt5 import QtCore
from PyQt5.QtCore import QSize, Qt
import numpy as np


class ImageScene():
	def __init__(self):
		self.full = False
		self.drawing = False
		self.go_enbl = False
		self.path = ''
		self.height = []
		self.coords = []
		self.lenl = []
		self.comboindex = 0
		img = QPixmap('interface/start.png')
		self.current = QGraphicsScene(0, 0, img.size().width(), img.size().height())
		self.current.addItem(QGraphicsPixmapItem(img))

	def clear(self):
		self.current.clear()
		self.current.addItem(QGraphicsPixmapItem(self.pixmap))
		self.coords = []
		self.lenl = []
		self.full = False
		self.go_enbl = False

	def setHeight(self, height, index):
		self.height = height
		self.comboindex = index

	def getSize(self):
		try:
			a, b = (self.pixmap.size().width(), self.pixmap.size().height()+10)
		except:
			a, b = 595, 611
		finally: return (a, b)

	def getsize(self):
		return list(self.sz)

	def patent_size(self, x, y):
		self.sz = (x, y)

	def get_lenline(self):
		scale = lambda w, h: np.array((w*self.sz[0]/self.pixmap.size().width(), h*self.sz[1]/self.pixmap.size().height()))
		M1, M2 = [scale(*item) for item in self.coords]
		self.coords = []
		self.full = False
		self.lenl.append(np.linalg.norm(M2-M1))
		print(self.lenl)

	def load(self, path, canvas, combo):
		image = Image.open(path)
		file = QPixmap(path)
		self.patent_size(file.size().width(), file.size().height())
		self.pixmap = file.scaledToHeight(canvas.geometry().height()-10)
		if self.pixmap.size().width() < canvas.geometry().width():
			canvas.resize(self.pixmap.size())
		self.path = path
		self.current = QGraphicsScene(0, 0, self.pixmap.size().width(), self.pixmap.size().height())
		self.current.addItem(QGraphicsPixmapItem(self.pixmap))
		self.drawing = True
		self.exif = {
			ExifTags.TAGS[k]: v
			for k, v in image._getexif().items()
			if k in ExifTags.TAGS
		}
		index = combo.findText(self.exif['Model'], QtCore.Qt.MatchFixedString)
		if index >= 0: combo.setCurrentIndex(index)

	def addPoint(self, x, y):
		Pen = QtCore.Qt.red if not self.lenl else QtCore.Qt.green
		self.coords.append((x,y))
		if len(self.coords) == 2: self.full = True
		self.current.addEllipse(x-2.5, y-2.5, 5, 5, QPen(Pen), Pen)

	def connect(self):
		Pen = QtCore.Qt.red if not self.lenl else QtCore.Qt.green
		self.current.addLine(*self.coords[1], *self.coords[0], QPen(Pen, 3, Qt.SolidLine, Qt.SquareCap, Qt.RoundJoin))
		self.get_lenline()
		self.go_enbl = True


