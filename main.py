import sys, os
from PyQt5 import QtCore, QtWidgets, QtGui

import cv2
from window import Window

LOG_QT_WARNINGS = False

def qt_message_handler(mode, context, message):
	if mode == QtCore.QtInfoMsg:
		mode = 'INFO'
	elif mode == QtCore.QtWarningMsg:
		mode = 'WARNING'
	elif mode == QtCore.QtCriticalMsg:
		mode = 'CRITICAL'
	elif mode == QtCore.QtFatalMsg:
		mode = 'FATAL'
	else:
		mode = 'DEBUG'
	if LOG_QT_WARNINGS:
		print('qt_message_handler: line: %d, func: %s(), file: %s' % (
			  context.line, context.function, context.file))
		print('  %s: %s\n' % (mode, message))

QtCore.qInstallMessageHandler(qt_message_handler)

if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	QtGui.QFontDatabase.addApplicationFont('interface/HelveticaNeueCyr-Roman.ttf')
	mainWin = Window()
	mainWin.show()
	sys.exit(app.exec_())
