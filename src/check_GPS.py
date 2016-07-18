import serial
import time
from pymavlink.dialects.v10 import common as mavlink
import pymavlink.mavutil as mavutil
import paho.mqtt.client as mqtt
import socket
import thread
import base64
import ast
import sys 

hostMQTT="localhost"
portMQTT=1883
topicToPublishMQTT="application/70b3d57ed0000172/node/f03d291000000046/rx"
timeMax = 50

class fifo(object):
    def __init__(self):
        self.buf = []
    def write(self, data):
        self.buf += data
        return len(data)
    def read(self):
        return self.buf.pop(0)
  
# we will use a fifo as an encode/decode buffer
f = fifo()
# create a mavlink instance, which will do IO on file object 'f'
mav = mavlink.MAVLink(f)

def encodeBase64(data):
	return base64.b64encode(data)

def encodeData(data):
	data64=encodeBase64(data)
	return "{\"reference\":\"mavlink\",\"devEUI\":\"f03d291000000046\",\"fPort\":1,\"confirmed\": false,\"data\":\""+str(data64)+"\"}"

def isUBX(message):
	if(len(message)>8):
		if(ord(message[0]) == 181 and ord(message[1]) == 98):
			return True
		else:
			return False
	else:
		return False

def isSRV_IN(message):
   if(ord(message[2]) == 1 and ord(message[3]) == 59):
	   return True
   else:
	   return False
	
def isGPS_ready(message):
   print(len(message))
   if(ord(message[44])==0): # 44 because 6 of the header and 38 to have to good byte of the payload
      return True
   else:
      return False

def publishMQTT(client,ready):
   global topicToPublishMQTT

   if(ready):
      mav = mavlink.MAVLink(f, 24, 1)
		#gps_raw_int_encode(usec, fix_type, lat, lon, alt, eph, epv, v, hdg)
      m = mav.gps_raw_int_encode(0,4,0,0,0,0,0,0,65535,255)
      m.pack(mav)
      data = m.get_msgbuf()
   else:
      mav = mavlink.MAVLink(f, 24, 1)
		#gps_raw_int_encode(usec, fix_type, lat, lon, alt, eph, epv, v, hdg)
      m = mav.gps_raw_int_encode(0,0,0,0,0,0,0,0,65535,255)
      m.pack(mav)
      data = m.get_msgbuf()
      (result,mid)=client.publish(topicToPublishMQTT,encodeData(data))

def checkSum(message):
   message=str(message)
   checkA, checkB = 0, 0
   for i in message:
      checkA += ord(i)
      checkB += checkA
   checkA="{0:b}".format(checkA)
   checkB="{0:b}".format(checkB)
   checkA=checkA[-8:]
   checkB=checkB[-8:]
   return int(checkA,2), int(checkB,2)

def pollRequestGPS(serial_port):
   #ca, cb = checkSum(chr(1)+chr(59)+"40")
   #request=chr(181)+chr(98)+chr(1)+chr(59)+"40"+chr(ca)+chr(cb)
   serial_port.write("\xB5\x62\x01\x3B\x00\x00\x3C\xB5")

ser = serial.Serial('/dev/ttyACM0')
client = mqtt.Client()
client.connect(hostMQTT, port=portMQTT)
timeBegin=time.time()
pollRequestGPS(ser)
diffTime=0
while diffTime < timeMax:
   line=ser.readline()
   diffTime=time.time()-timeBegin
   if(line[0] != '$'):
      line=[str(x)+":"+str(i) for (x,i) in enumerate(line)]
      print(line)
      print(line[47])     
      """publishMQTT(client,True)
         else:
            #publish sur le MQTT que c'est pas pret
            publishMQTT(client,False)
         break"""
	
if(diffTime>timeMax):
   publishMQTT(client,False)
   #publish sur le MQTT que c'est pas pret

"""
['0:\xb5', '1:b', '2:\x01', '3:;', '4:(', '5:\x00', '6:\x00', '7:\x00', '8:\x00', '9:\x00', '10:\x80', '11::', '12:$', '13:\x08', '14:\xc4', '15:\x0f', '16:\x00', '17:\x00', '18:\x00', '19:\x00', '20:\x00', '21:\x00', '22:\x00', '23:\x00', '24:\x00', '25:\x00', '26:\x00', '27:\x00', '28:\x00', '29:\x00', '30:\x00', '31:\x00', '32:\x00', '33:\x00', '34:\x00', '35:\xc2', '36:\x8b', '37:8', '38:\x00', '39:\x00', '40:\x00', '41:\x00', '42:\x00', '43:\x01', '44:\x00', '45:\x00', '46:\xa3', '47:s', '48:$', '49:G', '50:N', '51:R', '52:M', '53:C', '54:,', '55:1', '56:3', '57:5', '58:6', '59:1', '60:5', '61:.', '62:0', '63:0', '64:,', '65:V', '66:,', '67:,', '68:,', '69:,', '70:,', '71:,', '72:,', '73:1', '74:8', '75:0', '76:7', '77:1', '78:6', '79:,', '80:,', '81:,', '82:N', '83:,', '84:V', '85:*', '86:1', '87:5', '88:\r', '89:\n']
"""
