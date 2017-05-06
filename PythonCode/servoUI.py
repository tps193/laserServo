from uart import MspSerial

import sys
from threading import Thread
import time
import math
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5 import QtCore, QtGui
	
class MyWindow(QWidget):
	isTimerOn = False
	inProcess = False
	
	def __init__(self):
		super(MyWindow, self).__init__()
		#TODO: add scale
		self.WIN_Y_SIZE = 500
		self.WIN_X_SIZE = 500
		self.xPos = 0
		self.yPos = 0
		self.initUI()
		self.msp = MspSerial(True, True)
		self.msp.open()
		MyWindow.inProcess = True
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
		MyWindow.inProcess = False
	
	def startTime(self):
		time.sleep(0.4)
		if MyWindow.isTimerOn:
			self.msp.setAnglePosition(self.fiX, self.fiY)
		if MyWindow.inProcess:
		#	print('loop')
			self.startTime()
		else:
			print('stop loop')
		
	def mousePressEvent(self, QMouseEvent):
		MyWindow.isTimerOn = True
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
		self.msp.close()
		
def main():
	app = QApplication(sys.argv)
	ex = MyWindow()
	
	#ex.t.set()
	sys.exit(app.exec_())

#if __name__ == '__main__':
#	main()

main()
