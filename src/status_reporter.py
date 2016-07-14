#!/usr/bin/python

"""
        Installation of paho : pip install paho-mqtt
"""
from pymavlink.dialects.v10 import common as mavlink
import paho.mqtt.client as mqtt
import socket
import thread
import time
import base64
import json
import ast

UDP_IP = "192.168.2.1"
UDP_PORT_RECEIVER = 14550 # the bridge send MQTT message to a the UDP Reciever
hostMQTT="localhost"
portMQTT=1883
publishtopicMQTT="application/70b3d57ed0000172/node/f03d291000000046/rx"
radio_msg=""

class fifo(object):
    def __init__(self):
        self.buf = []
    def write(self, data):
        self.buf += data
        return len(data)
    def read(self):
        return self.buf.pop(0)

f = fifo()

def extractData(strJSON):
	tmp=ast.literal_eval(str(strJSON))	
	rssi=tmp['rssi']
	return rssi

def on_connect(client, userdata, flags, rc):
    client.subscribe(publishtopicMQTT)

# HEARTBEAT mavlink packet generator
def gen_heartbeat_msg_str():
   # create a mavlink instance, which will do IO on file object 'f'
   mav = mavlink.MAVLink(f, 24, 1)
   m = mav.heartbeat_encode(0,8,4,3,2)
   m.pack(mav)

   # get the encoded message as a buffer
   b = m.get_msgbuf()
   heartbeat_str = base64.b64encode(b)
   heartbeat_msg_str="{\"devEUI\":\"f03d291000000046\",\"fPort\":99,\"gatewayCount\":99,\"rssi\":99,\"data\":\""+ str(heartbeat_str)  + "\"}"
   
   return heartbeat_msg_str


# RADIO_STATUS mavlink packet generator
def gen_radio_status_msg_str(client, userdata, msg):
   rssi=extractData(msg)
   # create a mavlink instance, which will do IO on file object 'f'
   mav = mavlink.MAVLink(f, 24, 1)
   #radio_status_encode(rssi, remrssi, txbuf, noise, remnoise, rxerrors, fixed)
   m = mav.radio_status_encode(rssi,rssi,9,0,0,0,9)
   m.pack(mav)

   # get the encoded message as a buffer
   b = m.get_msgbuf()
   
   radio_status_str = base64.b64encode(b)
   # the devEUI is false. We have to modify it if we need the good one.
   radio_status_msg_str="{\"devEUI\":\"f03d291000000046\",\"fPort\":99,\"gatewayCount\":99,\"rssi\":99,\"data\":\""+ str(radio_status_str)  + "\"}"

   return radio_status_msg_str

def publishInfo(client, userdata, msg):
	global radio_msg
	radio_msg = msg

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = publishInfo
client.connect(hostMQTT, port=portMQTT)
client.loop_forever()

while 1:
    (result,mid)=client.publish(publishtopicMQTT, gen_radio_status_msg_str())
    (result,mid)=client.publish(publishtopicMQTT, gen_heartbeat_msg_str())
    time.sleep(1)

client.disconnect()
