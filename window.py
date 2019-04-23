import math, sys, json

import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize, Qt, pyqtSlot
from PyQt5.QtGui import QBrush, QPen, QPixmap
from PyQt5.QtWidgets import (QFileDialog, QGraphicsPixmapItem, QTableWidgetItem, QGraphicsScene, QDialogButtonBox,
							 QLabel, QMainWindow, QPushButton, QDialog)
from PyQt5.uic import loadUi

import cv2
import qosm
from qosm.common import QOSM
from ImageScene import ImageScene
from TableModel import tableModel
from AddDialog import AddDialog

#For debug only, delete later
DEBUG = True

class Window(QMainWindow):

	def __init__(self):
		QMainWindow.__init__(self)
		loadUi('interface/ui.ui', self)
		with open('interface/main.css') as f:
			ss = f.read()
			self.setStyleSheet(ss)
			self.tabPhoto.setStyleSheet(ss)
		self.createSignals()
		self.scenes = {}
		self.init_scene('1')
		self.loadjson()
		self.imgs_l.setAlignment(Qt.AlignLeft)
		self.canvas_sz = (self.canvas.geometry().width(), self.canvas.geometry().height())
		self.model = tableModel(self.tableWidget, 2, ['Номер', 'Расстояние'])
		self.tableWidget.horizontalHeader().setStretchLastSection(True);
		self.matrix.setView(QtWidgets.QListView())
		self.canvas.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.canvas.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

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
		self.go.setEnabled(True)

	def onMapLClick(self, latitude, longitude):
		if self.view.markersCount < len(self.scenes):
			self.view.addMarker("Mark "+str(self.view.markersCount+1), latitude, longitude)

	def add_clicked(self):
		if len(self.scenes) > 9: return
		temp = QPushButton(str(len(self.scenes)+1), clicked = self.set_scene)
		toEnbl = [str(i) for i in range(1,11,1)]
		for each in self.findChildren(QtWidgets.QPushButton):
			if each.text() in toEnbl: 
				each.setEnabled(True)
		temp.setEnabled(False)
		temp.setMinimumSize(60, 30)
		temp.setMaximumSize(60, 30)
		with open('interface/Special.css') as f:
			temp.setStyleSheet(f.read())
		self.imgs_l.addWidget(temp)
		self.castling()
		self.scene.setHeight(self.height.value(), self.matrix.currentIndex())
		self.canvas.setGeometry(0,0,*self.canvas_sz)
		self.init_scene(str(len(self.scenes)+1))

	pyqtSlot()
	def on_destroy_clicked(self):
		self.view.clear()
		self.height.setValue(0)
		self.matrix.setCurrentIndex(0)
		self.model.clear()
		self.setblock(True)
		toDel = [str(i) for i in range(2,11,1)]
		list_ = self.findChildren(QtWidgets.QPushButton)
		for item in list_:
			if item.text() in toDel:
				self.imgs_l.removeWidget(item)
				item.deleteLater()
		self.one.setEnabled(False)
		self.go.setEnabled(False)
		self.canvas.setGeometry(0,0,*self.canvas_sz)
		self.path.clear()
		self.scenes = {}
		self.init_scene('1')
				

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
		newvalue = self.dialog.newSize_l.text()+'x'+self.dialog.newSize_r.text()
		with open('data.json') as f:
			data = json.loads(f.read())
		if not newkey in data:
			data[newkey] = newvalue
		print(data)
		with open('data.json', 'w') as f:
			json.dump(data, f)
		self.loadjson()

###### Interface Manipulations Block

	def setblock(self, val):
		self.addButton.setEnabled(not val)
		self.clear.setEnabled(not val)
		self.matrix.setEnabled(not val)
		self.height.setEnabled(not val)

	def loadjson(self):
		self.matrix.clear()
		with open('data.json') as f:
			self.matrixList = json.loads(f.read())
		self.matrix.addItems(self.matrixList.keys())

	def init_scene(self, num):
		self.height.setValue(0)
		self.matrix.setCurrentIndex(0)
		self.setblock(True)
		self.go.setEnabled(False)
		self.canvas.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.scene = ImageScene()
		self.canvas.setScene(self.scene.current)
		self.scenes[num] = self.scene


	def load_image(self, file_name):
		self.canvas.resize(*self.canvas_sz)
		self.scene.load(file_name, self.canvas, self.matrix)
		self.path.setText(file_name)
		if self.scene.getSize()[0] > self.canvas_sz[0]:
			self.canvas.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
		self.canvas.setScene(self.scene.current)
		self.canvas.setRenderHint(QtGui.QPainter.HighQualityAntialiasing, True)
		self.canvas.show()
		self.setblock(False)

	def castling(self):
		self.imgs_l.removeWidget(self.add)
		self.add.deleteLater()
		self.add = QPushButton('+', objectName = 'add', clicked = self.add_clicked)
		self.add.setMinimumSize(30, 30)
		self.add.setMaximumSize(30, 30)
		self.imgs_l.addWidget(self.add)

	def set_scene(self):
		self.scene.setHeight(self.height.value(), self.matrix.currentIndex())
		sender = self.sender()
		for each in self.findChildren(QtWidgets.QPushButton): 
			each.setEnabled(True)
		sender.setEnabled(False)
		self.scene = self.scenes[sender.text()]
		self.canvas.setScene(self.scene.current)
		if self.scene.drawing: self.setblock(False)
		else: self.setblock(True)
		if self.scene.go_enbl: self.go.setEnabled(True)
		else: self.go.setEnabled(False)
		if self.scene.getSize()[0] > self.canvas_sz[0]:
			self.canvas.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
			self.canvas.setGeometry(0,0, *self.canvas_sz)
		else:
			self.canvas.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
			self.canvas.setGeometry(0,0, *self.scene.getSize())
		self.height.setValue(self.scene.height)
		self.matrix.setCurrentIndex(self.scene.comboindex)
		self.path.setText(self.scene.path)

###### Calculation Block

	def calc(self):
		self.scene.setHeight(self.height.value(), self.matrix.currentIndex())
		self.view.removeCircles()
		self.model.clear()

		for key in self.scenes:

			if DEBUG:
				obj = self.scenes[key]
				print(obj.path,'\n', obj.exif,'\n', obj.getsize()) #For debug only, delete later

			focalLength = self.scenes[key].exif['FocalLength'][0]/self.scenes[key].exif['FocalLength'][1]
			size_on_matrix = (np.max(list(map(float, self.matrixList[self.matrix.itemText(self.scenes[key].comboindex)].split('x'))))*self.scenes[key].lenl)/np.max((self.scenes[key].getsize()))
			distance = focalLength * \
			((self.scenes[key].height/size_on_matrix)+1)
			self.view.addCircle(distance, "Mark "+key)
			self.model.insert([key, np.round(distance,3)])
