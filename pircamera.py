#!/usr/bin/python -u
import os
import shutil
import time
import datetime
import RPi.GPIO as GPIO
import picamera
from fractions import Fraction

motorPin = 21
irPin = 15
pirPin = 14

GPIO.setmode(GPIO.BCM)

# PIR input
GPIO.setup(14, GPIO.IN)

# IR control H=off L=on
GPIO.setup(irPin, GPIO.OUT)
GPIO.output(irPin, GPIO.HIGH)

# Motor control H=on
GPIO.setup(motorPin, GPIO.OUT)
GPIO.output(motorPin, GPIO.LOW)

GPIO.output(irPin, GPIO.LOW)
camera = picamera.PiCamera( resolution = (1024, 768), framerate=30)
#camera.vflip = True
#camera.rotation = 90
camera.iso=400
time.sleep(5)
camera.capture('camcal.jpg')
camera.shutter_speed = camera.exposure_speed
camera.exposure_mode = 'off'
GPIO.output(irPin, GPIO.HIGH)


print("Ready")

picPerTrig = 3
outDir = "/mnt/tomnas/photo/rpi/pir"
calFlag = 1
while (1):

#	Dont' do anything in afternoon because of sun light
	thour = time.localtime().tm_hour 
#	if ((thour > 14) & (thour < 17)) :
#		continue

	if (GPIO.input(14)):
		GPIO.output(irPin, GPIO.LOW)			# Turn on IR light
		GPIO.output(motorPin, GPIO.HIGH)		# Turn zapper
		tstr = time.strftime("%Y%m%d%H%M%S")
		for i in range(0,picPerTrig):
			imgName = 'pir%s_%d.jpg'%(tstr,i)
			print imgName,
			camera.capture(imgName)
			print('Date now: %s' % datetime.datetime.now())
		GPIO.output(irPin, GPIO.HIGH) 			# Turn off IR light
		time.sleep(2)
		GPIO.output(motorPin, GPIO.LOW) 		# Turn off Zapper

		if (os.path.isdir(outDir)):			# Copy file to server
			for i in range(0,picPerTrig):
				imgName = 'pir%s_%d.jpg'%(tstr,i)
				shutil.copy(imgName, outDir)
				print("%s copied to %s" %(imgName,outDir))
				outName = outDir + '/' + imgName
				if (os.path.isfile(outName)): #	Remove local if copied ok
					os.unlink(imgName)
					print("%s removed" %(imgName))
		# delay between picture cycle to let PIR trigger settle
		while (GPIO.input(14)): # loop and wait for PIR to turn off
			time.sleep(1)

	time.sleep(.100)
	tmin = time.localtime().tm_min 
	if ((tmin < 30) & (calFlag)): 	# recalibrate once every hour
		calFlag = 0
		GPIO.output(irPin, GPIO.LOW)
		camera.shutter_speed = 0
		camera.exposure_mode = 'auto'
		time.sleep(5)
		camera.capture('camcal.jpg')
		camera.shutter_speed = camera.exposure_speed
		camera.exposure_mode = 'off'
		GPIO.output(irPin, GPIO.HIGH)
		print('Recal %s' % datetime.datetime.now())
		time.sleep(10)
	if (tmin > 30):
		calFlag = 1


