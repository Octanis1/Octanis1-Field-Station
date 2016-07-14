#!/bin/python
#This script was authored by AndrewH7 and belongs to him (www.instructables.com/member/AndrewH7)
import RPi.GPIO as GPIO
import os

gpio_pin_number=23

GPIO.setmode(GPIO.BCM)
#Use BCM pin numbering (i.e. the GPIO number, not pin number)
#WARNING: this will change between Pi versions
#Check yours first and adjust accordingly


GPIO.setup(gpio_pin_number, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#It's very important the pin is an input to avoid short-circuits
#The pull-up resistor means the pin is high by default


try:
   GPIO.wait_for_edge(gpio_pin_number, GPIO.RISING)
   #Use falling edge detection to see if pin is pulled 
   #low to avoid repeated polling
   os.system("sudo shutdown -h now")
   #Send command to system to shutdown
except:
   print("couldn't shutdown")
   pass

GPIO.cleanup()
