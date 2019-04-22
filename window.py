import math, sys, json

import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize, Qt, pyqtSlot
from PyQt5.QtGui import QBrush, QPen, QPixmap
from PyQt5.QtWidgets import (QFileDialog, QGraphicsPixmapItem, QTableWidgetItem, QGraphicsScene,
							 QLabel, QMainWindow, QPushButton, QDialog)
from PyQt5.uic import loadUi

import cv2
import qosm
from qosm.common import QOSM
from ImageScene import ImageScene
from TableModel import tableModel

#For debug only, delete later
DEBUG = True

class AddDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        loadUi('AddDialog.ui', self)

class Window(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)
		loadUi(r'ui.ui', self)
		self.createSignals()
		self.scenes = {}
		self.init_scene('1')
		self.loadjson()
		self.imgs_l.setAlignment(Qt.AlignLeft)
		self.canvas_sz = (self.canvas.geometry().width(), self.canvas.geometry().height())
		self.model = tableModel(self.tableWidget, 2, ['Номер', 'Расстояние'])

###### Signals and Slots Block

	def createSignals(self):
		self.add.clicked.connect(self.add_clicked)
		self.one.clicked.connect(self.set_scene)
		self.go.clicked.connect(self.calc)
		self.canvas.mousePressEvent = self.drawmode
		self.canvas.dropEvent = self.dropmode
		self.canvas.dragEnterEvent = self.dEE
		self.canvas.dragMoveEvent = self.dME
		self.view.mapClicked.connect(self.onMapLClick)

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

	def dropmode(self, event):
		if event.mimeData().hasUrls:
			event.setDropAction(QtCore.Qt.CopyAction)
			event.accept()
			for url in event.mimeData().urls():
				temp = str(url.toLocalFile())
			self.load_image(temp)  
		else:
			event.ignore()

	def drawmode(self, event):
		if not self.scene.drawing: self.open_dialog(); return
		x, y = event.x()+self.canvas.horizontalScrollBar().sliderPosition(), event.y() + \
			self.canvas.verticalScrollBar().sliderPosition()
		self.scene.addPoint(x,y)
		if not self.scene.full: return
		self.scene.connect()

	def onMapLClick(self, latitude, longitude):
		if self.view.markersCount < len(self.scenes):
			self.view.addMarker("Mark "+str(self.view.markersCount+1), latitude, longitude)

	def add_clicked(self):
		if len(self.scenes) > 9: return
		temp = QPushButton(str(len(self.scenes)+1), clicked = self.set_scene)
		for each in self.findChildren(QtWidgets.QPushButton): 
			each.setEnabled(True)
		temp.setEnabled(False)
		temp.setMinimumSize(60, 30)
		temp.setMaximumSize(60, 30)
		self.imgs_l.addWidget(temp)
		self.castling()
		self.init_scene(str(len(self.scenes)+1))

	def open_dialog(self):
		temp = QFileDialog.getOpenFileName(
			self, 'Open file', '', 'Images (*.png *.jpg *jpeg)')[0]
		self.load_image(temp)

	@pyqtSlot()
	def on_clear_clicked(self):
		self.scene.clear()

	@pyqtSlot()
	def on_addButton_clicked(self):
		self.dialog = AddDialog()
		self.dialog.show()
		self.dialog.accepted.connect(self.accept)
		self.dialog.exec_()

	def accept(self):
		newkey = self.dialog.newName.text()
		newvalue = float(self.dialog.newSize.text())
		with open('data.json') as f:
			data = json.loads(f.read())
		if not newkey in data:
			data[newkey] = newvalue
		print(data)
		with open('data.json', 'w') as f:
			json.dump(data, f)
		self.loadjson()

###### Interface Manipulations Block

	def loadjson(self):
		self.matrix.clear()
		with open('data.json') as f:
			self.matrixList = json.loads(f.read())
		self.matrix.addItems(self.matrixList.keys())

	def init_scene(self, num):
		self.scene = ImageScene()
		self.canvas.setScene(self.scene.current)
		self.scenes[num] = self.scene

	def load_image(self, file_name):
		self.canvas.resize(*self.canvas_sz)
		self.scene.load(file_name, self.canvas)
		self.path.setText(file_name)
		self.canvas.setScene(self.scene.current)
		self.canvas.setRenderHint(QtGui.QPainter.HighQualityAntialiasing, True)
		self.canvas.show()

	def castling(self):
		self.imgs_l.removeWidget(self.add)
		self.add.deleteLater()
		self.add = QPushButton('+', objectName = 'add', clicked = self.add_clicked)
		self.add.setMinimumSize(30, 30)
		self.add.setMaximumSize(30, 30)
		self.imgs_l.addWidget(self.add)

	def set_scene(self):
		sender = self.sender()
		for each in self.findChildren(QtWidgets.QPushButton): 
			each.setEnabled(True)
		sender.setEnabled(False)
		self.scene = self.scenes[sender.text()]
		self.canvas.setScene(self.scene.current)
		self.path.setText(self.scene.path)

###### Calculation Block

	def calc(self):
		print(len(self.scenes))
		for key in self.scenes:

			if DEBUG:
				obj = self.scenes[key]
				print(obj.path,'\n', obj.exif,'\n', obj.getsize()) #For debug only, delete later

			focalLength = self.scenes[key].exif['FocalLength'][0]/self.scenes[key].exif['FocalLength'][1]
			building_height = float(self.height.text())
			size_on_matrix = (self.matrixList[self.matrix.currentText()]*self.scenes[key].get_lenline())/np.max((self.scenes[key].getsize()))
			distance = focalLength * \
			((building_height/size_on_matrix)+1)
			self.view.addCircle(distance, "Mark "+key)
			self.model.insert([key, distance])
