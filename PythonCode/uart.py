import serial           # import the module

ComPort = serial.Serial('COM24') # open COM24
ComPort.baudrate = 115200 # set Baud rate to 9600
ComPort.bytesize = 8    # Number of data bits = 8
ComPort.parity   = 'N'  # No parity
ComPort.stopbits = 1    # Number of Stop bits = 1
# Write character 'A' to serial port
ar = [125, 100, 50, 127]
for b in ar:
	date = bytearray(b)
	No = ComPort.write(data)
#data = bytearray(b'A')




ComPort.close()         # Close the Com port