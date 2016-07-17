#!/usr/bin/python

"""
	Installation of paho : pip install paho-mqtt
"""
from pymavlink.dialects.v10 import common as mavlink
import pymavlink.mavutil as mavutil
import paho.mqtt.client as mqtt
import socket
import thread
import time
import base64
import json
import ast
import sys 

UDP_IP = "192.168.2.18"
UDP_PORT_SENDER = "14555"
UDP_PORT_RECIEVER = 14550 # the bridge send MQTT message to a the UDP Reciever
hostMQTT="localhost"
portMQTT=1883
topicToPublishMQTT="application/70b3d57ed0000172/node/f03d291000000046/tx"
topicToSubscribeMQTT="application/70b3d57ed0000172/node/+/rx"
msgId_whitelist = ["SET_MODE","COMMAND_LONG","MISSION_SET_CURRENT","MISSION_REQUEST","MISSION_REQUEST_LIST","MISSION_COUNT","MISSION_ITEM","MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN"]

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

def encodeData(binary):
	data64=encodeBase64(binary)
	return "{\"reference\":\"mavlink\",\"devEUI\":\"f03d291000000046\",\"fPort\":1,\"confirmed\": false,\"data\":\""+str(data64)+"\"}"

def UDP_to_MQTT(client,data):
	global topicToPublishMQTT
	(result,mid)=client.publish(topicToPublishMQTT,data)

#open udp port and mqtt client
try:
	client = mqtt.Client()
	client.connect(hostMQTT, port=portMQTT)
	udp_connection = mavutil.mavlink_connection('udp:'+UDP_IP+':'+UDP_PORT_SENDER) 
	
	print("Parsing MAVLink message from UDP...")
	
	while True:
		m = udp_connection.recv_match(blocking=True,type=msgId_whitelist)
	        if(m != None):
		   print("LoRa TX: msg_id %u, fields %s, len %u" % (m.get_msgId(), m.get_fieldnames(), len(m.get_msgbuf())))
		   UDP_to_MQTT(client,encodeData(m.get_msgbuf()))
	pass

except:
    print("Unexpected error 0:", sys.exc_info()[0])
    print("Unexpected error 1:", sys.exc_info()[1])
    print("Unexpected error 2:", sys.exc_info()[2])


