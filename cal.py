'''
R1 - roboID, vidCnt
R2 - cropT, cropB, cropL, cropR, bBmin, bBmax, bGmin, bGmax, bRmin, bRmax, ... gy, ... gb
R3 - vidNum, vidLen (s)
R4 - ...
'''
import cv2 as cv
import numpy as np
import time
import csv

with open("Data.csv") as configRaw:
	configLoop = csv.reader(configRaw, delimiter=' ')
	config = []
	for row in configLoop:
		config.append(str(row[0]).split(','))
robotDat = config[0][0:2]
fieldDat = config[1]
videoDat = []
for i in range(len(config)):
	if i > 1:
		videoDat.append(config[i][0:2])
print("Robot info:", robotDat)
print("Threshold info:", fieldDat)
print("Video List:", videoDat)

camera = cv.VideoCapture("v4l2src device=/dev/video0 ! image/jpeg, width=1280, height=720 ! jpegdec ! videoconvert ! appsink", cv.CAP_GSTREAMER	)

cv.namedWindow("CROP")
cv.namedWindow("BALL")
cv.namedWindow("YELLOW")
cv.namedWindow("BLUE")
maxCol = 255
minCol = 0
maxCrop = 350
minCrop = 0

def changed(inn):
	return(inn)

#create ball sliders
cv.createTrackbar("B - Blue Min", "BALL", minCol, maxCol, changed)
cv.setTrackbarPos("B - Blue Min", "BALL", int(fieldDat[4]))
cv.createTrackbar("B - Blue Max", "BALL", minCol, maxCol, changed)
cv.setTrackbarPos("B - Blue Max", "BALL", int(fieldDat[5]))
cv.createTrackbar("B - Green Min", "BALL", minCol, maxCol, changed)
cv.setTrackbarPos("B - Green Min", "BALL", int(fieldDat[6]))
cv.createTrackbar("B - Green Max", "BALL", minCol, maxCol, changed)
cv.setTrackbarPos("B - Green Max", "BALL", int(fieldDat[7]))
cv.createTrackbar("B - Red Min", "BALL", minCol, maxCol, changed)
cv.setTrackbarPos("B - Red Min", "BALL", int(fieldDat[8]))
cv.createTrackbar("B - Red Max", "BALL", minCol, maxCol, changed)
cv.setTrackbarPos("B - Red Max", "BALL", int(fieldDat[9]))
#create goal yellow sliders
cv.createTrackbar("GY - Blue Min", "YELLOW", minCol, maxCol, changed)
cv.setTrackbarPos("GY - Blue Min", "YELLOW", int(fieldDat[10]))
cv.createTrackbar("GY - Blue Max", "YELLOW", minCol, maxCol, changed)
cv.setTrackbarPos("GY - Blue Max", "YELLOW", int(fieldDat[11]))
cv.createTrackbar("GY - Green Min", "YELLOW", minCol, maxCol, changed)
cv.setTrackbarPos("GY - Green Min", "YELLOW", int(fieldDat[12]))
cv.createTrackbar("GY - Green Max", "YELLOW", minCol, maxCol, changed)
cv.setTrackbarPos("GY - Green Max", "YELLOW", int(fieldDat[13]))
cv.createTrackbar("GY - Red Min", "YELLOW", minCol, maxCol, changed)
cv.setTrackbarPos("GY - Red Min", "YELLOW", int(fieldDat[14]))
cv.createTrackbar("GY - Red Max", "YELLOW", minCol, maxCol, changed)
cv.setTrackbarPos("GY - Red Max", "YELLOW", int(fieldDat[15]))
#create goal blue sliders
cv.createTrackbar("GB - Blue Min", "BLUE", minCol, maxCol, changed)
cv.setTrackbarPos("GB - Blue Min", "BLUE", int(fieldDat[16]))
cv.createTrackbar("GB - Blue Max", "BLUE", minCol, maxCol, changed)
cv.setTrackbarPos("GB - Blue Max", "BLUE", int(fieldDat[17]))
cv.createTrackbar("GB - Green Min", "BLUE", minCol, maxCol, changed)
cv.setTrackbarPos("GB - Green Min", "BLUE", int(fieldDat[18]))
cv.createTrackbar("GB - Green Max", "BLUE", minCol, maxCol, changed)
cv.setTrackbarPos("GB - Green Max", "BLUE", int(fieldDat[19]))
cv.createTrackbar("GB - Red Min", "BLUE", minCol, maxCol, changed)
cv.setTrackbarPos("GB - Red Min", "BLUE", int(fieldDat[20]))
cv.createTrackbar("GB - Red Max", "BLUE", minCol, maxCol, changed)
cv.setTrackbarPos("GB - Red Max", "BLUE", int(fieldDat[21]))
#create crop sliders
cv.createTrackbar("TOP", "CROP", minCrop, maxCrop, changed)
cv.setTrackbarPos("TOP", "CROP", int(fieldDat[0]))
cv.createTrackbar("BOTTOM", "CROP", minCrop, maxCrop, changed)
cv.setTrackbarPos("BOTTOM", "CROP", int(fieldDat[1]))
cv.createTrackbar("LEFT", "CROP", minCrop, maxCrop, changed)
cv.setTrackbarPos("LEFT", "CROP", int(fieldDat[2]))
cv.createTrackbar("RIGHT", "CROP", minCrop, maxCrop, changed)
cv.setTrackbarPos("RIGHT", "CROP", int(fieldDat[3]))
cv.createTrackbar("Centre X", "CROP", 0, 1280, changed)
cv.setTrackbarPos("Centre X", "CROP", int(fieldDat[22]))
cv.createTrackbar("Centre Y", "CROP", 0, 720, changed)
cv.setTrackbarPos("Centre Y", "CROP", int(fieldDat[23]))

while True:
    ret, im = camera.read()
    while ret:
        blueMinB = cv.getTrackbarPos("B - Blue Min", "BALL")
        blueMaxB = cv.getTrackbarPos("B - Blue Max", "BALL")
        greenMinB = cv.getTrackbarPos("B - Green Min", "BALL")
        greenMaxB = cv.getTrackbarPos("B - Green Max", "BALL")
        redMinB = cv.getTrackbarPos("B - Red Min", "BALL")
        redMaxB = cv.getTrackbarPos("B - Red Max", "BALL")
        ball = cv.inRange(im, (blueMinB, greenMinB, redMinB), (blueMaxB, greenMaxB, redMaxB))
        cv.imshow('Robot: ' + str(robotDat[0]) + ' - Ball', ball)
        blueMinGY = cv.getTrackbarPos("GY - Blue Min", "YELLOW")
        blueMaxGY = cv.getTrackbarPos("GY - Blue Max", "YELLOW")
        greenMinGY = cv.getTrackbarPos("GY - Green Min", "YELLOW")
        greenMaxGY = cv.getTrackbarPos("GY - Green Max", "YELLOW")
        redMinGY = cv.getTrackbarPos("GY - Red Min", "YELLOW")
        redMaxGY = cv.getTrackbarPos("GY - Red Max", "YELLOW")
        goalY = cv.inRange(im, (blueMinGY, greenMinGY, redMinGY), (blueMaxGY, greenMaxGY, redMaxGY))
        cv.imshow('Robot: ' + str(robotDat[0]) + ' - Goal Yellow', goalY)
        blueMinGB = cv.getTrackbarPos("GB - Blue Min", "BLUE")
        blueMaxGB = cv.getTrackbarPos("GB - Blue Max", "BLUE")
        greenMinGB = cv.getTrackbarPos("GB - Green Min", "BLUE")
        greenMaxGB = cv.getTrackbarPos("GB - Green Max", "BLUE")
        redMinGB = cv.getTrackbarPos("GB - Red Min", "BLUE")
        redMaxGB = cv.getTrackbarPos("GB - Red Max", "BLUE")
        goalB = cv.inRange(im, (blueMinGB, greenMinGB, redMinGB), (blueMaxGB, greenMaxGB, redMaxGB))
        cv.imshow('Robot: ' + str(robotDat[0]) + ' - Goal Blue', goalB)
        left = cv.getTrackbarPos("LEFT", "CROP")
        right = cv.getTrackbarPos("RIGHT", "CROP")
        top = cv.getTrackbarPos("TOP", "CROP")
        bottom = cv.getTrackbarPos("BOTTOM", "CROP")
        cenX = cv.getTrackbarPos("Centre X", "CROP")
        cenY = cv.getTrackbarPos("Centre Y", "CROP")
        crop = im[top:(720-bottom), left:(1280-right)]
        cv.circle(crop, (cenX, cenY), 1, (255, 0, 255), 2)
        cv.imshow('Robot: ' + str(robotDat[0]) + ' - Crop', crop)
        fieldDat = [top, bottom, left, right, blueMinB, blueMaxB, greenMinB, greenMaxB, redMinB, redMaxB, blueMinGY, blueMaxGY, greenMinGY, greenMaxGY, redMinGY, redMaxGY, blueMinGB, blueMaxGB, greenMinGB, greenMaxGB, redMinGB, redMaxGB, cenX, cenY]
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    break

with open("Data.csv", "w") as out:
	writer = csv.writer(out)
	writer.writerow(robotDat)
	writer.writerow(fieldDat)
	for row in videoDat:
		writer.writerow(row)
	writer.writerows(configLoop)
camera.release()
cv.destroyAllWindows()