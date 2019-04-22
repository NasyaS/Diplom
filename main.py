import sys, os

import numpy as np
import PIL.ExifTags
from PIL import Image, ImageDraw
from PyQt5 import QtWidgets, QtGui

import cv2
from window import Window

if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	QtGui.QFontDatabase.addApplicationFont('interface/12948.otf')
	mainWin = Window()
	mainWin.show()
	sys.exit(app.exec_())
