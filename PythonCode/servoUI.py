import math
import sys
from threading import Timer
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

serialPort = 0

def sendData(data):
	print('data:',data)
	d = int(data)
	#print('byte:', d)
	b = bytes([d])
	serialPort.write(b)
	#print(b)

def calculateServoPosition(x, y):
	if (x == 0 and y == 0):
		servoX = 0
		servoY = MIN_SERVO_POSITION
		
	servoX = MAX_SERVO_POSITION - dt * (math.pi - math.atan2(y, x))
	servoY = MAX_SERVO_POSITION - dt * (math.pi - math.atan2(y, HEIGHT))
	return (servoX, servoY)
	
def setPosition(x, y):
	pos = calculateServoPosition(x, y)
	xPos = pos[0]
	yPos = pos[1]
	
	xHundreds = xPos // 100
	xNumber = xPos - xHundreds * 100
	
	yHundreds = yPos // 100
	yNumber = yPos - yHundreds * 100
	
	sendData(START_BYTE)
	sendData(xHundreds*100)
	sendData(xNumber)
	sendData(yHundreds*100)
	sendData(yNumber)
	sendData(STOP_BYTE)
	
class MyWindow(QWidget):
	
	def myCallback(self):
		setPosition(self.xPos, self.yPos)
	
	def __init__(self):
		super(MyWindow, self).__init__()
		self.WIN_Y_SIZE = 400
		self.WIN_X_SIZE = 500
		self.xPos = 0
		self.yPos = 0
		self.initUI()
		
	def initUI(self):
		self.setGeometry(0, 0, 500, self.WIN_Y_SIZE)
		self.setWindowTitle('Servo control')
		self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)
		self.show()
	
	def startTimer(self):
		if self.isTimerOn:
			setPosition(self.xPos, self.yPos)
			Timer(0.2, self.startTimer).start()
	
	def mousePressEvent(self, QMouseEvent):
		self.isTimerOn = True
		pos = getCursorPosition()
		self.xPos = pos.x() - self.WIN_X_SIZE
		self.yPos = self.WIN_Y_SIZE - pos.y()
		self.startTimer()
		
	def mouseMoveEvent(self, QMouseEvent):
		pos = getCursorPosition()
		self.xPos = pos.x() - self.WIN_X_SIZE
		self.yPos = self.WIN_Y_SIZE - pos.y()
		
	def mouseReleaseEvent(self, QMouseEvent):
		self.isTimerOn = False
		
	def getCursorPosition():
		return QtGui.QCursor().pos()
		
def main():
	serialPort = serial.Serial()
	serialPort.baudrate = 9600
	serialPort.port = "COM3"
	serialPort.open()
	app = QApplication(sys.argv)
	ex = MyWindow()
	serialPort.close()
	sys.exit(app.exec_())

#if __name__ == '__main__':
#	main()

main()
