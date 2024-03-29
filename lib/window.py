import os, sys, json, cv2, base64, numpy as np

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize, Qt, pyqtSlot, QTimer, QPropertyAnimation, QRect, QDir
from PyQt5.QtGui import QBrush, QPen, QPixmap
from PyQt5.QtWidgets import (QFileDialog, QGraphicsPixmapItem, QTableWidgetItem, QGraphicsView, QGraphicsScene, QDialogButtonBox,
							 QLabel, QMainWindow, QPushButton, QDialog)
from PyQt5.uic import loadUi
from io import BytesIO
from PIL import Image
from PIL.ImageQt import ImageQt

from qosm.common import QOSM
from lib.mathlogic import distance
from lib.ImageScene import ImageScene
from lib.TableModel import tableModel
from lib.AddDialog import AddDialog

#For debug only, delete later
DEBUG = False

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
		self.model = tableModel(self.tableWidget, 2, ['Номер', 'Расстояние (м)'], "Расстояние от места сьёмки до ориентира")
		self.tableWidget.horizontalHeader().setStretchLastSection(True)
		self.matrix.setView(QtWidgets.QListView())
		self.canvas.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.canvas.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.canvas_2.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.canvas_2.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.verticalLayout_3.addWidget(self.groupBox_2)
		self.groupBox_2.setVisible(False)
		self.tabWidget.currentChanged.connect(self.onTabChange)
		self.checkscene = ImageScene()
		self.canvas_2.setScene(self.checkscene.current)
		self.setGroupVis(False)
		self.view.checkConnection()
		self.tabWidget.setCurrentIndex(0)

###### Signals and Slots Block

	def createSignals(self):
		self.add.clicked.connect(self.add_clicked)
		self.one.clicked.connect(self.set_scene)
		self.go.clicked.connect(self.calc)
		self.canvas.mousePressEvent = self.drawmode
		self.canvas.dropEvent = self.dropmode
		self.canvas.dragEnterEvent = self.dEE
		self.canvas.dragMoveEvent = self.dME
		self.canvas_2.mousePressEvent = self.drawmode2
		self.canvas_2.dropEvent = self.dropmode2
		self.canvas_2.dragEnterEvent = self.dEE
		self.canvas_2.dragMoveEvent = self.dME
		self.view.mapClicked.connect(self.onMapLClick)
		self.view.connectionErr.connect(self.noncon)

	def noncon(self):
		self.throwerror("Ошибка подключения к интернету")

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
			self.load_image(temp, self.scene, self.canvas, self.path)  
		else:
			event.ignore()

	def dropmode2(self, event):
		if event.mimeData().hasUrls:
			event.setDropAction(QtCore.Qt.CopyAction)
			event.accept()
			for url in event.mimeData().urls():
				temp = str(url.toLocalFile())
			self.load_image(temp, self.checkscene, self.canvas_2, self.path_2, 0)
			self.check.setEnabled(True)
		else:
			event.ignore()

	def drawmode2(self, event):
		QF = QFileDialog()
		QF.setDirectory(QDir(os.environ.get('systemdrive')+"/Users/"+os.environ.get('username')+"/Pictures")) 
		temp = QF.getOpenFileName(self, 'Open file', '', 'Images (*.png *.jpg *jpeg)')[0]
		if not temp: return
		self.load_image(temp, self.checkscene, self.canvas_2, self.path_2, 0)
		self.check.setEnabled(True)

	def drawmode(self, event):
		if not self.scene.drawing: self.open_dialog(); return
		x, y = event.x()+self.canvas.horizontalScrollBar().sliderPosition(), event.y() + \
			self.canvas.verticalScrollBar().sliderPosition()
		if len(self.scene.lenl) == 2: self.scene.clear() 
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
		self.canvas_2.setGeometry(0,0,*self.canvas_sz)
		self.path.clear()
		self.path_2.clear()
		self.scenes = {}
		self.init_scene('1')
		self.checkscene = ImageScene()
		self.canvas_2.setScene(self.checkscene.current)
		self.check.setEnabled(False)
				

	def open_dialog(self):
		QF = QFileDialog()
		QF.setDirectory(QDir(os.environ.get('systemdrive')+"/Users/"+os.environ.get('username')+"/Pictures")) 
		temp = QF.getOpenFileName(self, 'Open file', '', 'Images (*.png *.jpg *jpeg)')[0]
		if temp: self.load_image(temp, self.scene, self.canvas, self.path)

	@pyqtSlot()
	def on_clear_clicked(self):
		self.scene.clear()

	@pyqtSlot()
	def on_addButton_clicked(self):
		self.dialog = AddDialog()
		self.dialog.show()
		self.dialog.accepted.connect(self.accept)
		self.dialog.exec_()

	@pyqtSlot()
	def on_save_clicked(self):
		coords, saves = self.view.getCoords(), ""
		for item in coords:
			for jtem in item:
				saves+=str(jtem)+':'
			saves+='\n'
		temp = QFileDialog.getSaveFileName(self, 'Save file', '', 'Osm Files (*.osm)')[0]
		if not temp: return
		with open(temp, "w") as f:
			f.write(saves)

	@pyqtSlot()
	def on_load_clicked(self):
		temp = QFileDialog.getOpenFileName(self, 'Open file', '', 'Osm Files (*.osm)')[0]
		if not temp: return
		with open(temp) as f:
			file = f.read()
		file = file.split('\n')
		result = []
		for item in file: result.append(item.split(':'))
		cnt = 1
		if file[0] == '': return self.throwerror("Файл пуст")
		self.view.clear()
		self.model.clear()
		for item in result:
			if item[0] == '': continue
			self.view.addMarker(item[0], float(item[1]), float(item[2]))
			if item[3] != '':
				self.view.addCircle(float(item[3]), item[0])
				self.model.insert([str(cnt),float(item[3])])
			cnt+=1
		result.remove([""])
		res = np.mean((np.array(result).T[1:3]).astype(float), axis = 1)
		self.view.centerAt(*res)
		self.tabWidget.setCurrentIndex(2)

	@pyqtSlot()
	def on_check_clicked(self):
		lat, lng = self.checkscene.getLatLng()
		if lat and lng:
			self.tabWidget.setCurrentIndex(2)
			self.view.addMarker("check", lat, lng)
			self.view.centerAt(lat, lng)
			self.lat.setText(str(lat))
			self.lng.setText(str(lng))
		else:
			self.throwerror("GPS теги не обнаружены")

	@pyqtSlot()
	def on_how_clicked(self):
		if self.how.text() == "x":
			self.img.setGeometry(QRect(0,0,1,1))
			self.setGroupVis(False)
			self.how.setText("?")
		else:
			self.how.setText("x")
			with open("data/docs.bin") as f:
				string = f.read()
			image = Image.open(BytesIO(base64.b64decode(string)))
			qim = ImageQt(image)
			self.curInd = 0
			pix = QtGui.QPixmap.fromImage(qim)
			self.img.setGeometry(QRect(0,0, 6230, 730))
			self.img.setPixmap(pix)
			self.left.setGeometry(QRect(10, 340, 24, 100))
			self.right.setGeometry(QRect(855, 340, 24, 100))
			self.setGroupVis(True)

	@pyqtSlot()
	def on_right_clicked(self):
		if self.curInd != 6:
			self.ranim = QPropertyAnimation(self.img, b"geometry")
			self.ranim.setDuration(500)
			self.ranim.setStartValue(QRect(-self.curInd*890, 0, 6230, 730))
			self.ranim.setEndValue(QRect(-self.curInd*890-890, 0, 6230, 730))
			self.ranim.start()
			self.curInd+=1

	@pyqtSlot()
	def on_left_clicked(self):
		if self.curInd != 0:
			self.lanim = QPropertyAnimation(self.img, b"geometry")
			self.lanim.setDuration(500)
			self.lanim.setStartValue(QRect(-self.curInd*890, 0, 6230, 730))
			self.lanim.setEndValue(QRect(-self.curInd*890+890, 0, 6230, 730))
			self.lanim.start()
			self.curInd-=1

	def accept(self):
		newkey = self.dialog.newName.text()
		newvalue = self.dialog.newSize_l.text()+'x'+self.dialog.newSize_r.text()
		with open('data/data.json') as f:
			data = json.loads(f.read())
		if not newkey in data:
			data[newkey] = newvalue
		with open('data/data.json', 'w') as f:
			json.dump(data, f)
		self.loadjson()

	def onTabChange(self, i):
		if i == 2: self.view.checkConnection()
		if i != 0:
			self.groupBox.setVisible(False)
			self.groupBox_2.setVisible(True)
		else:
			self.groupBox_2.setVisible(False)
			self.groupBox.setVisible(True)

	def keyPressEvent(self, event):
		if event.key() == QtCore.Qt.Key_Delete:
			self.scene.clear()

###### Interface Manipulations Block

	def setGroupVis(self, val):
		self.left.setVisible(val)
		self.right.setVisible(val)
		self.img.setVisible(val)

	def throwerror(self, error):
		self.err_label.setText("Ошибка: "+error)
		self.a_start()

	def a_start(self):
		self.anim = QPropertyAnimation(self.frame, b"geometry")
		self.anim.setDuration(500)
		self.anim.setStartValue(QRect(10, 730, 861, 31))
		self.anim.setEndValue(QRect(10, 696, 861, 31))
		self.anim.start()
		self.timer = QTimer()
		self.timer.timeout.connect(self.a_end)
		self.timer.start(2000)

	def a_end(self):
		self.timer.stop()
		self.anim1 = QPropertyAnimation(self.frame, b"geometry")
		self.anim1.setDuration(500)
		self.anim1.setStartValue(QRect(10, 696, 861, 31))
		self.anim1.setEndValue(QRect(10, 730, 861, 31))
		self.anim1.start()

	def setblock(self, val):
		self.addButton.setEnabled(not val)
		self.clear.setEnabled(not val)
		self.matrix.setEnabled(not val)
		self.height.setEnabled(not val)

	def loadjson(self):
		self.matrix.clear()
		with open('data/data.json') as f:
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


	def load_image(self, file_name, scene, canvas, path, noblock = 1):
		canvas.resize(*self.canvas_sz)
		scene.load(file_name, canvas, self.matrix)
		file_name = file_name.split('/')
		path.setText(file_name[len(file_name)-1])
		if scene.getSize()[0] > self.canvas_sz[0]:
			canvas.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
		canvas.setScene(scene.current)
		canvas.setRenderHint(QtGui.QPainter.HighQualityAntialiasing, True)
		canvas.show()
		if noblock: self.setblock(False)

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
		file_name = self.scene.path.split('/')
		self.path.setText(file_name[len(file_name)-1])

	def checkmarkers(self):
		counter = 0
		for key in self.scenes:
			if self.scenes[key].good(): counter+=1
		return counter

###### Calculation Block

	def calc(self):
		self.tabWidget.setCurrentIndex(2)
		self.scene.setHeight(self.height.value(), self.matrix.currentIndex())
		self.view.removeCircles()
		self.view.removefakes(len(self.scenes))
		self.model.clear()

		if self.checkmarkers() > self.view.markersCount:
			return self.throwerror("Не хватает маркеров")

		for key in self.scenes:
			if not self.scenes[key].good():
				self.throwerror("Не готова сцена "+key)
				continue
			if not self.scenes[key].exif:
				self.throwerror("Не найден exif файл в сцене "+key)
				continue
				
			if DEBUG:
				obj = self.scenes[key]
				print(obj.path,'\n', obj.exif,'\n', obj.getsize()) #For debug only, delete later

			dist = distance(self.scenes[key], self.matrixList[self.matrix.itemText(self.scenes[key].comboindex)].split('x'))

			self.view.addCircle(dist, "Mark "+key)
			self.model.insert([key, np.round(dist,3)])
