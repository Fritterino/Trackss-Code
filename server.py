#recieving information from the users pc
import RPi.GPIO as GPIO
import socket
import time
import sys
from _thread import *
#setting up the networking defenitions
host = ''
port = 5555
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#setting up the GPIO defenitions
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
clockR = 11
counterclockR = 15
PWMR = 13
clockL = 16
counterclockL = 18
PWML = 12
GPIO.setup(clockR,GPIO.OUT)
GPIO.setup(counterclockR,GPIO.OUT)
GPIO.setup(PWMR,GPIO.OUT)
pwmrV = GPIO.PWM(PWMR,20000)
pwmrV.start(0)
GPIO.setup(clockL,GPIO.OUT)
GPIO.setup(counterclockL,GPIO.OUT)
GPIO.setup(PWML,GPIO.OUT)
pwmlV = GPIO.PWM(PWML,20000)
pwmlV.start(0)
try:
	s.bind((host,port))
except socket.error as e:
	print(str(e))

s.listen(5)

def threaded_client(conn):
	while True:
		data = conn.recv(256)
		if len(data)>0:
			#reading the string format
			clean_data = b''
			for i in range(0,256):
				if data[i]==0 and data[i+1]==0:
					break
				clean_data += bytes([data[i]])
			data_string = clean_data.decode('utf-8')
			data_int = list(map(int,data_string.split(',')))
			#data_int format:
			#data_int[0] - motor1 clockwise direction
			#data_int[1] = motor1 counterclockwise direction
			#data_int[2] = motor1 PWM duty cycle
			#data_int[3] = motor2 clockwise ...
			#data_int[4] = motor2 counterclockwise ...
			#data_int[5] = motor2 PWM
			if data_int[0]==2:
				pwmrV.stop()
				pwmlV.stop()
				GPIO.cleanup()
				sys.exit()
			GPIO.output(clockR,data_int[0])
			GPIO.output(counterclockR,data_int[1])
			GPIO.output(clockL,data_int[3])
			GPIO.output(counterclockL,data_int[4])
			pwmrV.ChangeDutyCycle(data_int[2])
			pwmlV.ChangeDutyCycle(data_int[5])
			#print('recieved data:',data_int)

while True:
	conn,addr = s.accept()
	start_new_thread(threaded_client, (conn,))
