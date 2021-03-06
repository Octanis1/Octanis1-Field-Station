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
import binascii

hostMQTT="localhost"
portMQTT=1883
topicToPublishMQTT="application/70b3d57ed0000172/node/f03d291000000046/rx"
timeMax = 1 # we need timeMax <= 1 

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
	return "{\"devEUI\":\"f03d291000000046\",\"fPort\":99,\"gatewayCount\":99,\"rssi\":99,\"data\":\""+str(data64)+"\"}"

def extract_observation_time(message): 
   if(len(message)>20):
      binString=bin(int(binascii.hexlify(message[14]+message[15]+message[16]+message[17]), 16))
      obsTime=int(binString,2)
      print(obsTime)
      return obsTime
   else:
      print("format of the message is not correct")
      return 0

def publishMQTT_ready(client,message):
   publishMQTT_gps_raw_int(client,4, extract_observation_time(message))

def publishMQTT_not_ready(client,message):
   publishMQTT_gps_raw_int(client,0, extract_observation_time(message))

def publishMQTT_gps_raw_int(client,fix_type,obs_time=0):
   global topicToPublishMQTT
   mav = mavlink.MAVLink(f, 24, 1)
	#gps_raw_int_encode(usec, fix_type, lat, lon, alt, eph, epv, v, hdg)
   m = mav.gps_raw_int_encode(obs_time,fix_type,0,0,0,0,0,0,65535,255)
   m.pack(mav)
   data = m.get_msgbuf()
   (result,mid)=client.publish(topicToPublishMQTT,encodeData(data))

def pollRequestGPS(serial_port):
   serial_port.write("\xB5\x62\x01\x3B\x00\x00\x3C\xB5")

def gps_ready(message):
   if(len(message)<49):
      return False
   else:
      if(message[43]=='\x00' and message[44]=='\x00'):
         return True
      else:
         return False

ser = serial.Serial('/dev/ttyACM0')
client = mqtt.Client()
client.connect(hostMQTT, port=portMQTT)
timeBegin=time.time()
diffTime=0
while 1:
   # after waiting 0.5 second since the last timeBegin, we send another poll request and reinitialize the timer
   diffTime=time.time()-timeBegin
   if(diffTime>timeMax):
      # we wait 0.5 second, to avoid using 100% processor when the poll request always fail
      time.sleep(2)
      timeBegin=time.time()
      pollRequestGPS(ser)

   line=ser.readline()
   if(line[0] != '$'): # i.e we have a UBX message
      line=[str(i) for (x,i) in enumerate(line)]
      if(gps_ready(line)):
         publishMQTT_ready(client,line)
         print("ready")
      else:
         publishMQTT_not_ready(client,line)
         print("Not ready")
         # we wait 1 second and next we will send another poll request (because diffTime > 1 >= timeMax)
      time.sleep(3)


"""
['0:\xb5', '1:b', '2:\x01', '3:;', '4:(', '5:\x00', '6:\x00', '7:\x00', '8:\x00', '9:\x00', '10:\x80', '11::', '12:$', '13:\x08', '14:\xc4', '15:\x0f', '16:\x00', '17:\x00', '18:\x00', '19:\x00', '20:\x00', '21:\x00', '22:\x00', '23:\x00', '24:\x00', '25:\x00', '26:\x00', '27:\x00', '28:\x00', '29:\x00', '30:\x00', '31:\x00', '32:\x00', '33:\x00', '34:\x00', '35:\xc2', '36:\x8b', '37:8', '38:\x00', '39:\x00', '40:\x00', '41:\x00', '42:\x00', '43:\x01', '44:\x00', '45:\x00', '46:\xa3', '47:s', '48:$', '49:G', '50:N', '51:R', '52:M', '53:C', '54:,', '55:1', '56:3', '57:5', '58:6', '59:1', '60:5', '61:.', '62:0', '63:0', '64:,', '65:V', '66:,', '67:,', '68:,', '69:,', '70:,', '71:,', '72:,', '73:1', '74:8', '75:0', '76:7', '77:1', '78:6', '79:,', '80:,', '81:,', '82:N', '83:,', '84:V', '85:*', '86:1', '87:5', '88:\r', '89:\n']
"""
