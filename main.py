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
import math
import serial

#            bx   bY   gyX  gyY  gbX  gbY
idPackets = ['"', '#', '$', '%', '&', "*"]

#--Config Values--
saveFPS = 15
arduino = serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=0.1)
debugElements = False
FPSterminal = False
debug = False
displayTracks = False
ballBox = 60
addShit = 45
goalShit = 45
minCrop = 2

with open("/home/epsilon6-1/Ep6_Open_2023_LP/Data.csv") as configRaw:
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

videoName = "DebugSave" + str(int(robotDat[1]) + 1) + ".avi"
robotDat[1] = int(robotDat[1]) + 1
print("vid:", videoName)
camera = cv.VideoCapture("v4l2src device=/dev/video0 ! image/jpeg, width=1280, height=720 ! jpegdec ! videoconvert ! appsink", cv.CAP_GSTREAMER	)
# if saveFPS > 0:
# 	out = cv.VideoWriter(videoName ,cv.VideoWriter_fourcc('X','V','I','D'), saveFPS, ((1280-int(fieldDat[2])-int(fieldDat[3])), (720-int(fieldDat[0])-int(fieldDat[1]))))

font = cv.FONT_HERSHEY_SIMPLEX
fps = 0
blank = np.zeros((1, 1))

endTime = time.time()
textTime = 0
showTime = 1
prevStart = 0
prevRead = 0

if saveFPS > 0:
	saveFreq = 1/saveFPS
prevSave = time.time()

#thresholds
gyMax = np.array((int(fieldDat[11]), int(fieldDat[13]), int(fieldDat[15])))
gyMin = np.array((int(fieldDat[10]), int(fieldDat[12]), int(fieldDat[14])))
gbMax = np.array((int(fieldDat[17]), int(fieldDat[19]), int(fieldDat[21])))
gbMin = np.array((int(fieldDat[16]), int(fieldDat[18]), int(fieldDat[20])))
bMax =  np.array((int(fieldDat[5]), int(fieldDat[7]), int(fieldDat[9])))
bMin =  np.array((int(fieldDat[4]), int(fieldDat[6]), int(fieldDat[8])))
blank = np.zeros((1,1))
cenX = 360
cenY = 360
connectivity = 4
bY = False
bX = False
vidStart = time.time()

#previous coords
prevBallX = 0
prevBallY = 0
prevYellowX = 0
prevYellowY = 0
prevBlueX = 0
prevBlueY = 0

while True:
	startTime = time.time()
	ret, raw = camera.read()
	im = raw[int(fieldDat[0]):(720-int(fieldDat[1])), int(fieldDat[2]):(1280-int(fieldDat[3]))]
	imCenX = math.ceil(len(im[0])/2)-1
	imCenY = math.ceil(len(im)/2)-1
	frameTime = startTime-prevStart
	if debugElements:
		cv.putText(im, "fps: " + str(int(1/frameTime)), (5, 30), font, 1, (255, 255, 255), 2, cv.LINE_AA)
	if FPSterminal:
		print(str(int(1/frameTime)))
	if displayTracks:
		cv.imshow('Ball', maskB)
	bStatMax = 0
	bAct = 0
	if prevStart != 0:
		bTop = bY-ballBox
		if bTop < 0:
			bTop = 0
		bBot = bY+ballBox
		if bBot >= len(im):
			bBot = len(im)-1
		bLef = bX-ballBox
		if bLef < 0:
			bLef = 0
		bRig = bX+ballBox
		if bRig >= len(im[0]):
			bRig = len(im[0])-1
		ballCheck = cv.inRange(im[bTop:bBot, bLef:bRig], bMin, bMax)
		bNum, bLab, bStat, bCent = cv.connectedComponentsWithStats(ballCheck, connectivity, cv.CV_32S)
		for i in range(1, len(bStat)):
			if bStat[i][4] > bStatMax:
				bStatMax = bStat[i][4]
				bAct = i
		if bAct > 0 and bStat[bAct][4] > minCrop:
			bX, bY = (int(bCent[bAct][0])+bLef, int(bCent[bAct][1])+bTop)
		else:
			bAct = 0
	if bAct == 0:
		if prevBallX != 0 & prevBallY != 0:
			bTop = prevBallY-addShit
			if bTop < 0:
				bTop = 0
			bBot = prevBallY+addShit
			if bBot >= len(im):
				bBot = len(im)-1
			bLef = prevBallX-addShit
			if bLef < 0:
				bLef = 0
			bRig = prevBallX+addShit
			if bRig >= len(im[0]):
				bRig = len(im[0])-1
		else:
			bTop = 0
			bBot = 720
			bLef = 0
			bRig = 1280
		maskB = cv.inRange(im[bTop:bBot, bLef:bRig], bMin, bMax)
		bNum, bLab, bStat, bCent = cv.connectedComponentsWithStats(maskB, connectivity, cv.CV_32S)
		for i in range(1, len(bStat)):
			if bStat[i][4] > bStatMax:
				bStatMax = bStat[i][4]
				bAct = i
		if bAct > 0 and bStat[bAct][4] > minCrop:
			bX, bY = (int(bCent[bAct][0]), int(bCent[bAct][1]))
		else:
			bAct = 0
			bX, bY = (cenX, cenY)
	if prevYellowX != 0 & prevYellowY != 0:
		gyTop = prevYellowY-goalShit
		if gyTop < 0:
			gyTop = 0
		gyBot = prevYellowY+goalShit
		if gyBot >= len(im):
			gyBot = len(im)-1
		gyLef = 0
		gyRig = 1280
	else:
		gyTop = 0
		gyBot = 720
		gyLef = 0
		gyRig = 1280
	maskGY = cv.inRange(im, gyMin, gyMax)
	if displayTracks:
		cv.imshow('Yellow Goal', maskGY)
	gyNum, gyLab, gyStat, gyCent = cv.connectedComponentsWithStats(maskGY, connectivity, cv.CV_32S)
	gyStatMax = 0
	gyAct = 0
	for i in range(1, len(gyStat)):
		if gyStat[i][4] > gyStatMax:
			gyStatMax = gyStat[i][4]
			gyAct = i
	if gyAct > 0:
		gyX, gyY = (int(gyCent[gyAct][0]), int(gyCent[gyAct][1]))
	else:
		gyX, gyY = (cenX, cenY)
	if prevBlueX != 0 & prevBlueY != 0:
		gbTop = prevBlueY-goalShit
		if gbTop < 0:
			gbTop = 0
		gbBot = prevBlueY+goalShit
		if gbBot >= len(im):
			gbBot = len(im)-1
		gbLef = 0
		gbRig = 1280
	else:
		gbTop = 0
		gbBot = 720
		gbLef = 0
		gbRig = 1280
	maskGB = cv.inRange(im[gbTop:gbBot, gbLef:gbRig], gbMin, gbMax)
	if displayTracks:
		cv.imshow('Blue Goal', maskGB)
	gbNum, gbLab, gbStat, gbCent = cv.connectedComponentsWithStats(maskGB, connectivity, cv.CV_32S)
	gbStatMax = 0
	gbAct = 0
	for i in range(1, len(gbStat)):
		if gbStat[i][4] > gbStatMax:
			gbStatMax = gbStat[i][4]
			gbAct = i
	if gbAct > 0:
		gbX, gbY = (int(gbCent[gbAct][0]), int(gbCent[gbAct][1]))
	else:
		gbX, gbY = (cenX, cenY)
	if debugElements:
		cv.rectangle(im, (bStat[bAct, cv.CC_STAT_LEFT] + bLef, bStat[bAct, cv.CC_STAT_TOP] + bTop), (bStat[bAct, cv.CC_STAT_LEFT] + bStat[bAct, cv.CC_STAT_WIDTH] + bLef, bStat[bAct, cv.CC_STAT_TOP] + bStat[bAct, cv.CC_STAT_HEIGHT] + bTop), (255, 255, 255), 1)
		cv.rectangle(im, (gyStat[gyAct, cv.CC_STAT_LEFT], gyStat[gyAct, cv.CC_STAT_TOP]), (gyStat[gyAct, cv.CC_STAT_LEFT] + gyStat[gyAct, cv.CC_STAT_WIDTH], gyStat[gyAct, cv.CC_STAT_TOP] + gyStat[gyAct, cv.CC_STAT_HEIGHT]), (255, 255, 255), 1)
		cv.rectangle(im, (gbStat[gbAct, cv.CC_STAT_LEFT], gbStat[gbAct, cv.CC_STAT_TOP]), (gbStat[gbAct, cv.CC_STAT_LEFT] + gbStat[gbAct, cv.CC_STAT_WIDTH], gbStat[gbAct, cv.CC_STAT_TOP] + gbStat[gbAct, cv.CC_STAT_HEIGHT]), (255, 255, 255), 1)
		cv.circle(im, (bX, bY), 4, (0, 255, 0), -1)
		cv.circle(im, (gyX, gyY), 4, (255, 0, 0), -1)
		cv.circle(im, (gbX, gbY), 4, (0, 0, 255), -1)
		cv.line(im, (cenX, cenY), (bX, bY), (0, 0, 0), 1)
		cv.line(im, (cenX, cenY), (gyX, gyY), (0, 0, 0), 1)
		cv.line(im, (cenX, cenY), (gbX, gbY), (0, 0, 0), 1)
	if saveFPS > 0:
		if (time.time() - prevSave) > saveFreq:
			prevSave = time.time()
	if debug:
		cv.imshow('Image', im)
	#stream format (all coords based on centre): ballX, ballY, yellowX, yellowY, blueX, blueY
	stream = [500+bX-cenX, 500-bY+cenY, 500+gyX-cenX, 500-gyY+cenY, 500+gbX-cenX, 500-gbY+cenY]
	for i in range(len(stream)):
		arduino.write(bytes(idPackets[i] + str(stream[i]), 'utf-8'))
	arduino.write(bytes("!", 'utf-8'))
	if cv.waitKey(1) & 0xFF == ord('q'):
		break
	prevStart = startTime

videoDat.append([robotDat[1], int(time.time()-vidStart)])
with open("Data.csv", "w") as out:
	writer = csv.writer(out)
	writer.writerow(robotDat)
	writer.writerow(fieldDat)
	for row in videoDat:
		writer.writerow(row)
	writer.writerows(configLoop)

camera.release()
if saveFPS > 0:
	out.release()
cv.destroyAllWindows()
