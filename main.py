import sys, os
from PyQt5 import QtWidgets, QtGui

import cv2
from window import Window

if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	QtGui.QFontDatabase.addApplicationFont('interface/HelveticaNeueCyr-Roman.ttf')
	mainWin = Window()
	mainWin.show()
	sys.exit(app.exec_())
