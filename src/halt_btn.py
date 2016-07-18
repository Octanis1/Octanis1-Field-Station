#!/bin/python
#This script was authored by AndrewH7 and belongs to him (www.instructables.com/member/AndrewH7)
import RPi.GPIO as GPIO
import os
import sys
import time

gpio_pin_number=23

GPIO.setmode(GPIO.BCM)
#Use BCM pin numbering (i.e. the GPIO number, not pin number)
#WARNING: this will change between Pi versions
#Check yours first and adjust accordingly


GPIO.setup(gpio_pin_number, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#It's very important the pin is an input to avoid short-circuits
#The pull-up resistor means the pin is high by default

while True:
      try:
         print("waiting for shutdown command")
         GPIO.wait_for_edge(gpio_pin_number, GPIO.RISING)
         time.sleep(2)
         #still high?
         if GPIO.input(gpio_pin_number) == GPIO.HIGH:
	   #Send command to system to shutdown
	   print("going down")
	   os.system("echo Shutdown | wall")
   	   os.system("sudo shutdown -h now")
      except:
         print("couldn't shutdown")
         print("Unexpected error 0:", sys.exc_info()[0])
         print("Unexpected error 1:", sys.exc_info()[1])
         print("Unexpected error 2:", sys.exc_info()[2])
      pass
pass

GPIO.cleanup()


