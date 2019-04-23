from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize, Qt, pyqtSlot
from PyQt5.QtGui import QBrush, QPen, QPixmap
from PyQt5.QtWidgets import (QFileDialog, QGraphicsPixmapItem, QTableWidgetItem, QGraphicsScene, QDialogButtonBox,
							 QLabel, QMainWindow, QPushButton, QDialog)
from PyQt5.uic import loadUi

class AddDialog(QDialog):
	leftClick = False;
	X, Y, X2, Y2 = 0, 0, 0, 0
	def __init__(self):
		QDialog.__init__(self)
		loadUi('interface/AddDialog.ui', self)
		self.setWindowFlags(Qt.SplashScreen);
		ok = QPushButton('Oк', objectName = 'Ok')
		cancel = QPushButton('Отмена', objectName = 'Cancel')
		self.buttonBox.addButton(ok, QDialogButtonBox.AcceptRole);
		self.buttonBox.addButton(cancel, QDialogButtonBox.RejectRole);
		with open('interface/dialogs.css') as f:
			self.setStyleSheet(f.read())

	def mouseMoveEvent(self, event):
		super(AddDialog, self).mouseMoveEvent(event)
		if self.leftClick == True: 
		    self.move(event.globalPos().x()-self.X-self.X2,event.globalPos().y()-self.Y-self.Y2)

	def mousePressEvent(self, event):
		super(AddDialog, self).mousePressEvent(event)
		if event.button() == QtCore.Qt.LeftButton:
			self.leftClick = True
			self.X=event.pos().x()
			self.Y=event.pos().y()

	def mouseReleaseEvent(self, event):
		super(AddDialog, self).mouseReleaseEvent(event)
		self.leftClick = False