import sys, os
from PyQt5 import QtCore, QtWidgets, QtGui

from lib.window import Window

LOG_QT_WARNINGS = True

if not LOG_QT_WARNINGS:
	QtCore.qInstallMessageHandler(lambda x,y,z: None)

if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	QtGui.QFontDatabase.addApplicationFont('interface/HelveticaNeueCyr-Roman.ttf')
	mainWin = Window()
	mainWin.show()
	sys.exit(app.exec_())
