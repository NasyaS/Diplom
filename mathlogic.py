import numpy as np


def focalLength(exiflength):
	return exiflength[0]/exiflength[1]


def matrixsize(matrix, linelength, canvsize):
	return (np.max(list(map(float, matrix)))*linelength)/np.max(canvsize)

def process(object, matrix, msize, h = False):
	height = 1.65 if h else object.height 
	return focalLength(object.exif['FocalLength']) * \
	((height/msize)+1)

def distance(object, matrix):
	if len(object.lenl) == 1:
		msz = matrixsize(matrix, object.lenl[0], object.getsize())
		return process(object, matrix, msz)
	else:
		msz1, msz2 = matrixsize(matrix, object.lenl[0], object.getsize()), matrixsize(matrix, object.lenl[1], object.getsize())
		return process(object, matrix, msz1) - process(object, matrix, msz2, h = True)

	