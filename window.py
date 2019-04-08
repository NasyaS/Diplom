import math
import sys

import numpy as np
from PIL import ExifTags, Image, ImageDraw
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize, Qt, pyqtSlot
from PyQt5.QtGui import QBrush, QPen, QPixmap
from PyQt5.QtWidgets import (QFileDialog, QGraphicsPixmapItem, QGraphicsScene,
                             QLabel, QMainWindow, QPushButton)
from PyQt5.uic import loadUi

import cv2
import qosm
from qosm.common import QOSM


class Window(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.count = 0
        self.canvas_coords = []
        self.drawingEnabled = False
        self.states = {0: "Режим разметки", 1: "Режим просмотра"}
        self.setMinimumSize(QSize(800, 500))
        loadUi(r'ui.ui', self)
        self.canvas_sz = (self.canvas.geometry().width(),
                          self.canvas.geometry().height())
        self.cord_x = 0
        self.cord_y = 0

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

    def load_image(self, file_name):
        self.canvas.resize(*self.canvas_sz)
        file = QPixmap(file_name)
        self.origin_sz = (file.size().width(), file.size().height())
        self.pixmap = file.scaledToHeight(self.canvas.geometry().height())
        if self.pixmap.size().width() < self.canvas.geometry().width():
            self.canvas.resize(self.pixmap.size())
        self.scene = QGraphicsScene(
            0, 0, self.pixmap.size().width(), self.pixmap.size().height())
        self.scene.addItem(QGraphicsPixmapItem(self.pixmap))
        self.canvas.setScene(self.scene)
        self.canvas.show()
        self.canvas.mousePressEvent = self.drawmode

    def drawmode(self, event):
        if not self.drawingEnabled:
            return
        x, y = event.x()+self.canvas.horizontalScrollBar().sliderPosition(), event.y() + \
            self.canvas.verticalScrollBar().sliderPosition()
        self.canvas_coords.append((x, y))
        self.scene.addEllipse(x-1.5, y-1.5, 3, 3,
                              QPen(QtCore.Qt.red), QtCore.Qt.red)
        if len(self.canvas_coords) < 2:
            return
        self.scene.addLine(
            *self.canvas_coords[1], *self.canvas_coords[0], QPen(QtCore.Qt.red))
        def scale(w, h): return np.array(
            (w*self.origin_sz[0]/self.pixmap.size().width(), h*self.origin_sz[1]/self.pixmap.size().height()))
        M1, M2 = [scale(*item) for item in self.canvas_coords]
        self.Len_line = np.linalg.norm(M2-M1)
        self.canvas_coords = []
        self.drawingEnabled = False
        self.mark.setText(self.states[self.drawingEnabled])

    @pyqtSlot()
    def on_mark_clicked(self):
        self.drawingEnabled = False if self.drawingEnabled else True
        self.mark.setText(self.states[self.drawingEnabled])

    @pyqtSlot()
    def on_clear_clicked(self):
        self.scene.clear()
        self.scene.addItem(QGraphicsPixmapItem(self.pixmap))
        self.canvas_coords = []

    def onMarkerRClick(self, key, lat, lng):
        if self.checkBox.isChecked():
            self.view.removeMarker(key)

    @pyqtSlot()
    def on_btnpath_clicked(self):
        temp = QFileDialog.getOpenFileName(
            self, 'Open file', '', 'Images (*.png *.jpg *jpeg)')[0]
        self.path.setText(temp)
        self.filePath = temp
        self.load_image(temp)

    def onMapLClick(self, latitude, longitude):
        print(latitude, longitude)
        if self.checkBox.isChecked():
            self.count += 1
            self.view.addMarker("My mark "+str(self.count), latitude, longitude, **dict(
                icon="http://maps.gstatic.com/mapfiles/ridefinder-images/mm_20_gray.png",
                draggable=True,
                title=u"mark n "+str(self.count)))

    @pyqtSlot()
    def on_go_clicked(self):
        self.calc()
        self.cord_x, self.cord_y = self.view.get_coord()
        print(self.cord_x, self.cord_y)
        self.view.addCircle(self.cord_x, self.cord_y,
                            self.distance-self.distance*0.05)
        self.view.addCircle(self.cord_x, self.cord_y,
                            self.distance+self.distance*0.05)
        self.panMap(self.cord_x, self.cord_y)

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

        self.dist.setText(str(self.distance))
