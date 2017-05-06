from uart import MspSerial
import math

msp = MspSerial(True, True)
msp.open()

for i in range (36, 1, -1):
	print('value:', i)
	d = math.pi / 36 * i
	msp.setAnglePosition(d,d)
	
msp.close()
	