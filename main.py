import sys

import numpy as np
from PIL import Image, ImageDraw 
import PIL.ExifTags
from PyQt5 import QtWidgets

import cv2
from window import Window


def calculate():
    img = Image.open('photo1.jpg')

    print(img.info['dpi'][0])
    image = cv2.imread('photo1.jpg')
    height = np.size(image, 0)
    width = np.size(image, 1)

    #константы
    size_matrix =np.array([6.16,4.62]) #размерматрицы

    # print("Размер матрицы = "+str(size_matrix[0])+" x "+str(size_matrix[1])+" мм ")
    # print("Ввести высоту здания")
    h_build = input()
    # print("Высота реальная = "+str(h_build)+" м")

    FocalLength = 5.4	
    # print("Фокусное расстояние = "+str(FocalLength)+" мм, что равно = " + str(FocalLength/1000) +" м ")

    Len_line = 1500
    # print("Длина отрезка = "+str(Len_line)+" пикс.")

    # print (f"Высота изобр. ="+str(height)+" пикс.")
    # print ("Ширина изобр. = "+str(width)+" пикс.")

    size_on_matrix = (np.max(size_matrix)*Len_line)/np.max(([height,width]))
    # print("Размер объекта на матрице = "+str(size_on_matrix)+" мм, что равно = " + str(size_on_matrix/1000) +" м ")

    dist = FocalLength*((int(h_build)/size_on_matrix)+1)
    # print ("Расстояние до объекта  = "+str(dist)+" метров!!!!!!!")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = Window()
    mainWin.show()

    sys.exit(app.exec_())


