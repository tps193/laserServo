import math
import sys
from threading import Thread
import time
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5 import QtCore, QtGui

import serial

MAX_NUMBER = 125
HEIGHT = 150
START_BYTE = 126
STOP_BYTE = 127

MAX_SERVO_POSITION = 2300
MIN_SERVO_POSITION = 700
dt = (MAX_SERVO_POSITION - MIN_SERVO_POSITION) / math.pi

LEFT_SIDE_Y = True
LASER_X_POSITION = 200


serialPort = serial.Serial()
serialPort.baudrate = 9600
serialPort.port = "COM3"

inProcess = True

res = 0

def sendData(data):
	global serialPort
	global res
	print(res)
	res=res+1
	#print(serialPort.isOpen)
	#print('data:',data)
	d = int(data)
	#print('byte:', d)
	b = bytes([d])
	
	if (serialPort.isOpen()):
		#print(serialPort.isOpen())
		i = 10
		ok = False
		while i > 0 and not ok:
			try:
				print('try to send ', i)
				time.sleep(0.1)
				serialPort.write(b)
				ok = True
			except Exception:
				print('ups')
				time.sleep(1)
				i=i-1
	#serialPort.close()
	#print(b)

def calculateServoPosition(x, y):
	if (x == 0 and y == 0):
		servoX = 1500
		if (LEFT_SIDE_Y):
			servoY = MIN_SERVO_POSITION
		else:
			servoY = MAX_SERVO_POSITION
			
	#servoX = MAX_SERVO_POSITION - dt * (math.pi - math.atan2(y, x))
	servoX = MAX_SERVO_POSITION - dt * math.atan2(y, x)
	yFi = math.atan2(y, -HEIGHT)
	yDiff = 0
	if (LEFT_SIDE_Y):
		yDiff = dt * yFi
	else:
		yDiff = dt * (math.pi - yFi)
	servoY = MAX_SERVO_POSITION - yDiff
	return (servoX, servoY)	

def setPosition(x, y):
	pos = calculateServoPosition(x, y)
	xPos = pos[0]
	yPos = pos[1]
	print("xMs:", xPos)
	print("yMs:",yPos)
	global inProcess
	#inProcess = True
	sendPositionData(xPos, yPos)
	#inProcess = False
	
def setAnglePosition(fiX, fiY):
	servoX = MAX_SERVO_POSITION - dt * fiX
	yDiff = 0
	if (LEFT_SIDE_Y):
		yDiff = dt * fiY
	else:
		yDiff = dt * (math.pi - fiY)
	servoY = MAX_SERVO_POSITION - yDiff
	print('send ', servoX, ';', servoY)
			
	sendPositionData(servoX,servoY)
	
def sendPositionData(xPos, yPos):
	xHundreds = xPos // 100
	xNumber = xPos - xHundreds * 100
	
	yHundreds = yPos // 100
	yNumber = yPos - yHundreds * 100
	
	#inProcess = True
	print('startSend')
	sendData(START_BYTE)
	sendData(xHundreds)
	sendData(xNumber)
	sendData(yHundreds)
	sendData(yNumber)
	sendData(STOP_BYTE)
	#time.sleep(0.03)
	print('finishSend')
	#inProcess = False
		
	
class MyWindow(QWidget):
	isTimerOn = False
	
	def myCallback(self):
		setPosition(self.xPos, self.yPos)
	
	def __init__(self):
		super(MyWindow, self).__init__()
		#TODO: add scale
		self.WIN_Y_SIZE = 500
		self.WIN_X_SIZE = 500
		self.xPos = 0
		self.yPos = 0
		self.initUI()
		
		self.t = Thread(target = self.startTime)
		self.t.start()
		
		
	def initUI(self):
		self.setGeometry(0, 0, self.WIN_X_SIZE, self.WIN_Y_SIZE)
		self.setWindowTitle('Servo control')
		self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)
		
		
		self.show()
		
	def paintEvent(self, paintEvent):
		painter = QtGui.QPainter(self)
		painter.drawEllipse(0,0, self.WIN_X_SIZE, self.WIN_Y_SIZE)
		painter.drawLine(-self.WIN_X_SIZE, self.WIN_Y_SIZE / 2, self.WIN_X_SIZE, self.WIN_Y_SIZE /2)
		painter.drawLine(self.WIN_X_SIZE/2, 0, self.WIN_X_SIZE/2, self.WIN_Y_SIZE)
		
	def stopInProcess(self):
		global inProcess
		inProcess = False
	
	def startTimer2(self):
		global inProcess
		if self.isTimerOn:
			#setPosition(self.xPos, self.yPos)
			if (not inProcess):
				setAnglePosition(self.fiX, self.fiY)
				#if self.isTimerOn:
				#	Timer(0.3, self.startTimer).start()
		else:
			global serialPort
			print("port closed")
			#serialPort.close()

	def startTime(self):
		#print(time)
		global inProcess
		time.sleep(0.4)
		if MyWindow.isTimerOn:
			setAnglePosition(self.fiX, self.fiY)
		if inProcess:
		#	print('loop')
			self.startTime()
		else:
			print('stop loop')
		
	def mousePressEvent(self, QMouseEvent):
		MyWindow.isTimerOn = True
		global serialPort
		#if (not serialPort.isOpen()):
		#	serialPort.open()
		#self.setCursorPosition()
		self.setPolarPosition()
		print("press")
		#self.startTimer()
		
	def mouseMoveEvent(self, QMouseEvent):
		#self.setCursorPosition()
		self.setPolarPosition()
		print(self.fiX, ";", self.fiY)
	#	print('move')
		
	def mouseReleaseEvent(self, QMouseEvent):
		MyWindow.isTimerOn = False
		time.sleep(0.4)
		print('release')
		
	def setCursorPosition(self):
		pos = QtGui.QCursor().pos()
		self.xPos = pos.x() - self.WIN_X_SIZE + LASER_X_POSITION
		print("x:",self.xPos)
		self.yPos = self.WIN_Y_SIZE - pos.y()
		print("y:",self.yPos)
		
	def setPolarPosition(self):
		pos = QtGui.QCursor().pos()
		xRatio = pos.x() / self.WIN_X_SIZE
		self.fiX = math.pi * (1 - xRatio)
		yRatio = pos.y() / self.WIN_Y_SIZE
		self.fiY = math.pi * (1 - yRatio)
		
	def closeEvent(self, event):
		print('close')
		self.stopInProcess()
		self.t.join()
		global serialPort
		serialPort.close()
		
def main():
	global serialPort
	print(serialPort.isOpen)
	serialPort.open()
	
	app = QApplication(sys.argv)
	ex = MyWindow()
	
	#ex.t.set()
	sys.exit(app.exec_())

#if __name__ == '__main__':
#	main()

main()
