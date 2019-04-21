import math
import sys

import numpy as np
from PIL import ExifTags, Image, ImageDraw
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize, Qt, pyqtSlot
from PyQt5.QtGui import QBrush, QPen, QPixmap
from PyQt5.QtWidgets import (QFileDialog, QGraphicsPixmapItem, QTableWidgetItem, QGraphicsScene,
							 QLabel, QMainWindow, QPushButton)
from PyQt5.uic import loadUi

import cv2
import qosm
from qosm.common import QOSM
from ImageScene import ImageScene


class Window(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)
		self.count = 0
		self.drawingEnabled = False
		self.scenes = {}
		self.setMinimumSize(QSize(800, 500))
		loadUi(r'ui.ui', self)
		self.init_scene('1')
		self.add.clicked.connect(self.add_clicked)
		self.one.clicked.connect(self.set_scene)
		self.imgs_l.setAlignment(Qt.AlignLeft)
		self.canvas_sz = (self.canvas.geometry().width(),
						  self.canvas.geometry().height())
		self.canvas.mousePressEvent = self.drawmode
		self.canvas.dropEvent = self.dropmode
		self.canvas.dragEnterEvent = self.dEE
		self.canvas.dragMoveEvent = self.dME
		self.filePath = ''
		self.matrixList = {

			'23.1x15.4': 23.1,
			'6.16x4.14': 6.16,
			# matrix size : max size of matrix size
			'Redmi (3.93x2.95)': 3.93
		}
		self.building_height = 0  # visota zdania
		self.distance = 0
		self.focalLength = 0
		self.matrix.addItems(self.matrixList.keys())
		self.view.mapClicked.connect(self.onMapLClick)
		self.init_table()

	def init_table(self):
		self.tableWidget.setColumnCount(2)
		self.tableWidget.setHorizontalHeaderLabels(['Номер', 'Расстояние'])
		self.tableWidget.insertRow(self.tableWidget.rowCount());
		self.tableWidget.setItem(self.tableWidget.rowCount()-1, 0, QTableWidgetItem('1'));
		self.tableWidget.setItem(self.tableWidget.rowCount()-1, 1, QTableWidgetItem('Test Data'));

	def init_scene(self, num):
		self.scene = ImageScene()
		self.canvas.setScene(self.scene.current)
		self.scenes[num] = self.scene

		
	def load_image(self, file_name):
		self.canvas.resize(*self.canvas_sz)
		file = QPixmap(file_name)
		self.scene.patent_size(file.size().width(), file.size().height())
		self.pixmap = file.scaledToHeight(self.canvas.geometry().height())
		if self.pixmap.size().width() < self.canvas.geometry().width():
			self.canvas.resize(self.pixmap.size())
		self.scene.load(self.pixmap, file_name)
		self.canvas.setScene(self.scene.current)
		self.canvas.setRenderHint(QtGui.QPainter.HighQualityAntialiasing, True)
		self.canvas.show()
		self.drawingEnabled = True

	def dEE(self, event):
		if event.mimeData().hasUrls:
			event.accept()
		else:
			event.ignore()

	def dME(self, event):
		if event.mimeData().hasUrls:
			event.setDropAction(QtCore.Qt.CopyAction)
			event.accept()
		else:
			event.ignore()

	def castling(self):
		self.imgs_l.removeWidget(self.add)
		self.add.deleteLater()
		self.add = QPushButton('+', objectName = 'add', clicked = self.add_clicked)
		self.add.setMinimumSize(30, 30)
		self.add.setMaximumSize(30, 30)
		self.imgs_l.addWidget(self.add)

	def set_scene(self):
		sender = self.sender()
		self.scene = self.scenes[sender.text()]
		self.canvas.setScene(self.scene.current)
		self.path.setText(self.scene.path)

	def add_clicked(self):
		if len(self.scenes) > 9: return
		temp = QPushButton(str(len(self.scenes)+1), clicked = self.set_scene)
		temp.setMinimumSize(60, 30)
		temp.setMaximumSize(60, 30)
		self.imgs_l.addWidget(temp)
		self.castling()
		self.init_scene(str(len(self.scenes)+1))

	def dropmode(self, event):
		print('accept')
		if event.mimeData().hasUrls:
			event.setDropAction(QtCore.Qt.CopyAction)
			event.accept()
			for url in event.mimeData().urls():
				temp = str(url.toLocalFile())
			self.path.setText(temp)
			self.filePath = temp
			self.load_image(temp)  
		else:
			event.ignore()

	def drawmode(self, event):
		if not self.drawingEnabled: self.open_dialog()
		x, y = event.x()+self.canvas.horizontalScrollBar().sliderPosition(), event.y() + \
			self.canvas.verticalScrollBar().sliderPosition()
		self.scene.addPoint(x,y)
		if not self.scene.full: return
		self.scene.connect()
		self.Len_line = self.scene.get_distance()

	@pyqtSlot()
	def on_clear_clicked(self):
		self.scene.clear()

	def onMarkerRClick(self, key, lat, lng):
		if self.checkBox.isChecked():
			self.view.removeMarker(key)

	def open_dialog(self):
		temp = QFileDialog.getOpenFileName(
			self, 'Open file', '', 'Images (*.png *.jpg *jpeg)')[0]
		self.path.setText(temp)
		self.filePath = temp
		self.load_image(temp)

	def onMapLClick(self, latitude, longitude):
		print(latitude, longitude)
		self.cord_x, self.cord_y = latitude, longitude
		self.count += 1
		self.view.addMarker("Mark "+str(self.count), latitude, longitude)

	@pyqtSlot()
	def on_go_clicked(self):
		self.calc()

	def panMap(self, lat, lng,):
		frame = self.view.page()
		frame.runJavaScript('mymap.panTo(L.latLng({}, {}));'.format(lat, lng))

	def calc(self):
		image = Image.open(self.filePath)
		print(self.filePath)

		exif = {
			ExifTags.TAGS[k]: v
			for k, v in image._getexif().items()
			if k in ExifTags.TAGS
		}
		print(exif)

		width, height = image.size
		print(width)
		print(height)

		self.focalLength = exif['FocalLength'][0]/exif['FocalLength'][1]

		size_on_matrix = (self.matrixList[self.matrix.currentText(
		)]*self.Len_line)/np.max(([height, width]))

		self.building_height = float(self.height.text())

		self.distance = self.focalLength * \
			((self.building_height/size_on_matrix)+1)

		print(self.distance, self.distance*0.1)

		self.view.addCircle(self.distance)

		self.dist.setText(str(self.distance))
