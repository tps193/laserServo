import serial           # import the module
import math
import time

MAX_NUMBER = 125
HEIGHT = 150
START_BYTE = 126 #~
STOP_BYTE = 127 #DEL

MAX_SERVO_POSITION = 2300
MIN_SERVO_POSITION = 700
dt = (MAX_SERVO_POSITION - MIN_SERVO_POSITION) / math.pi

LEFT_SIDE_Y = True
LASER_X_POSITION = 200

class MspSerial():
	
	def __init__(self, leftSideY, debug):
		self.serial = serial.Serial()
		s = self.serial
		s.baudrate = 9600
		s.port = "COM3"
		self.leftSideY = leftSideY
		self.debug = debug
		self.sentBytesCount = 0
		
		
	def sendData(self, data):
		self.sentBytesCount += 1
		if self.debug:
			print('Sending ', self.sentBytesCount, ' byte')
			print('Serial is open:', self.serial.isOpen())
			print('Data to send:',data)
		d = int(data)
		
		if d == 0:
			print('Zero value! lets sens 0x01')
			d = 1
		
		b = bytes([d])
		if (self.serial.isOpen()):
			i = 5
			ok = False
			while i > 0 and not ok:
				try:
					if self.debug:
						print(i, ' attempt to send ', b)
					#time.sleep(0.1)
					self.serial.write(b)
					ok = True
				except Exception:
					print('Fail to send ', b, '. Try again after a  second')
					time.sleep(1)
					i=i-1
		
	def calculateServoPosition(self, x, y):
		if (x == 0 and y == 0):
			servoX = 1500
			if (self.leftSideY):
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
		if self.debug:
			print('Convert (', x,';',y,') -> (',servoX,';',servoY,')');
		return (servoX, servoY)	

	def setPlainPosition(self, x, y):
		pos = self.calculateServoPosition(x, y)
		xPos = pos[0]
		yPos = pos[1]
		sendPositionData(xPos, yPos)
		
	def setAnglePosition(self, fiX, fiY):
		servoX = MAX_SERVO_POSITION - dt * fiX
		yDiff = 0
		if (self.leftSideY):
			yDiff = dt * fiY
		else:
			yDiff = dt * (math.pi - fiY)
		servoY = MAX_SERVO_POSITION - yDiff
		if self.debug:
			print('Convert (', fiX,';',fiY,') -> (',servoX,';',servoY,')');		
		self.sendPositionData(servoX,servoY)
		
	def sendPositionData(self, xPos, yPos):
		xHundreds = xPos // 100
		xNumber = xPos - xHundreds * 100
		
		yHundreds = yPos // 100
		yNumber = yPos - yHundreds * 100
		if self.debug:
			print('Start send byte array')
		arr = (START_BYTE, xHundreds, xNumber, yHundreds, yNumber, STOP_BYTE)
		self.sendArray(arr)
		time.sleep(0.055)
		if self.debug:
			print('Finish send by array')

	def sendArray(self, arr):
		for data in arr:
			self.sendData(data)
			time.sleep(0.1)
	
	def open(self):
		self.serial.open()
	
	def close(self):
		self.serial.close()