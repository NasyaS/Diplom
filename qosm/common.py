import functools, json, sys, os, socket, decorator

from PyQt5 import QtCore, QtGui, QtNetwork, QtWebChannel, QtWidgets #QJsonArray, QJsonValue
from PyQt5.QtCore import QObject, QSize, Qt, QUrl, pyqtSignal, pyqtSlot, QJsonValue
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkDiskCache
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import (QWebEnginePage, QWebEngineScript,
                                      QWebEngineView)
from PyQt5.QtWidgets import QLabel, QMainWindow, QPushButton
from PyQt5.uic import loadUi

doTrace = False

path = os.path.abspath(__file__)[:-9]


@decorator.decorator
def trace(function, *args, **k):
    """Decorates a function by tracing the begining and
    end of the function execution, if doTrace global is True"""

    if doTrace:
        print("> " + function.__name__, args, k)
    result = function(*args, **k)
    if doTrace:
        print("< " + function.__name__, args, k, "->", result)
    return result


class _LoggedPage(QWebEnginePage):
    @trace
    def javaScriptConsoleMessage(self, msg, line, source):
        print('JS: %s line %d: %s' % (source, line, msg))


class QOSM(QWebEngineView):
    mapMoved = pyqtSignal(float, float)
    mapClicked = pyqtSignal(float, float)
    mapRightClicked = pyqtSignal(float, float)
    mapDoubleClicked = pyqtSignal(float, float)

    markerMoved = pyqtSignal(str, float, float)
    markerClicked = pyqtSignal(str, float, float)
    markerDoubleClicked = pyqtSignal(str, float, float)
    markerRightClicked = pyqtSignal(str, float, float)

    connectionErr = pyqtSignal()


    def __init__(self, parent):
        super(QOSM, self).__init__(parent)
        self.markersCount = 0
        self.creature = []
        self.manager = QNetworkAccessManager()
        self.cache = QNetworkDiskCache()
        self.cache.setCacheDirectory("cache")
        self.manager.setCache(self.cache)
        self.channel = QtWebChannel.QWebChannel(self)
        self.channel.registerObject("qOSMap", self)
        self.page().setWebChannel(self.channel)
        with open(path+'index.html') as f:
            HTML = f.read()
        self.setHtml(HTML)
        self.loadFinished.connect(self.onLoadFinished)

    def checkConnection(self):
        Remote = "openstreetmap.ru"
        try:
            host = socket.gethostbyname(Remote)
            s = socket.create_connection((host, 80), 2)
        except:
            self.connectionErr.emit()


    def onLoadFinished(self):
        with open(path+'qwebchannel.js') as f:
            run_channel = f.read()
        with open(path+'script.js') as f:
            JS = f.read()
        with open(path+'circle_disk.js') as f:
            CL = f.read()
        self.page().runJavaScript(run_channel)
        self.page().runJavaScript(CL)
        self.page().runJavaScript(JS)
        self.page().runJavaScript("initialize()")


    def clear(self):
        self.markersCount = 0
        self.creature = []
        self.page().runJavaScript("osm_clear()")    	

    def waitUntilReady(self):
        while not self.initialized:
            QApplication.processEvents()

    def runScript(self, script):
        return self.page().runJavaScript(script)

    def centerAt(self, latitude, longitude):
        self.page().runJavaScript("osm_setCenter({}, {})".format(latitude, longitude))

    def setZoom(self, zoom):
        self.page().runJavaScript("osm_setZoom({})".format(zoom))

    def getCoords(self):
        return self.creature

    def center(self):
        center = self.page().runJavaScript("osm_getCenter()")
        return center['lat'], center['lng']

    def addMarker(self, key, latitude, longitude, **extra):
        self.markersCount+=1
        self.creature.append([key, latitude, longitude])
        return self.page().runJavaScript("osm_addMarker(key={!r},"
                                         "latitude= {}, "
                                         "longitude= {}, {});".format(key, latitude, longitude, json.dumps(extra)))

    def removefakes(self, skey):
        return self.page().runJavaScript("osm_rmfakes({})".format(skey))

    def removeMarker(self, key):
        return self.page().runJavaScript("osm_deleteMarker(key={!r});".format(key))

    def addCircle(self, radius, key):
        for item in self.creature:
            if item[0] == key: item.append(radius)
        return self.page().runJavaScript("osm_addCircle({},key={!r})".format(radius, key))

    def removeCircles(self):
        return self.page().runJavaScript("osm_rmCircles({})".format(self.markersCount))

    def moveMarker(self, key, latitude, longitude):
        self.page().runJavaScript("osm_moveMarker(key={!r},"
                                  "latitude= {}, "
                                  "longitude= {});".format(key, latitude, longitude))

    def positionMarker(self, key):
        return tuple(self.page().runJavaScript("osm_posMarker(key={!r});".format(key)))


# ----------marker signals

    @pyqtSlot(str, float, float)
    def markerIsMoved(self, key, lat, lng):
        for item in self.creature:
            if item[0] == key:
                item[1], item[2] = lat, lng
        self.markerMoved.emit(key, lat, lng)

    @pyqtSlot(str, float, float)
    def markerIsClicked(self, key, lat, lng):
        self.markerClicked.emit(key, lat, lng)

    @pyqtSlot(str, float, float)
    def markerIsDBClicked(self, key, lat, lng):
        self.markerDoubleClicked.emit(key, lat, lng)

    @pyqtSlot(str, float, float)
    def markerIsRClicked(self, key, lat, lng):
        self.markerRightClicked.emit(key, lat, lng)


# -----------map signals

    @pyqtSlot(float, float)
    def mapIsMoved(self, lat, lng):
        self.mapMoved.emit(lat, lng)

    @pyqtSlot(float, float)
    def mapIsClicked(self, lat, lng):
        self.mapClicked.emit(lat, lng)

    @pyqtSlot(float, float)
    def mapIsDoubleClicked(self, lat, lng):
        self.mapDoubleClicked.emit(lat, lng)

    @pyqtSlot(float, float)
    def mapIsRightClicked(self, lat, lng):
        self.mapRightClicked.emit(lat, lng)
