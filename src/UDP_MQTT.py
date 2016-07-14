#!/usr/bin/python

"""
	Installation of paho : pip install paho-mqtt
"""

import paho.mqtt.client as mqtt
import socket
import thread
import time
import base64
import json
import ast

UDP_IP = "192.168.2.1"
UDP_PORT_SENDER = 14555
UDP_PORT_RECIEVER = 14550 # the bridge send MQTT message to a the UDP Reciever
hostMQTT="localhost"
portMQTT=1883
topicToPublishMQTT="application/70b3d57ed0000172/node/f03d291000000046/tx"
topicToSubscribeMQTT="application/70b3d57ed0000172/node/+/rx"

def encodeBase64(data):
	return base64.b64encode(data)

def encodeData(binary):
	data64=encodeBase64(binary)
	return "{\"reference\":\"mavlink\",\"devEUI\":\"f03d291000000046\",\"fPort\":1,\"confirmed\": false,\"data\":\""+str(data64)+"\"}"

def UDP_to_MQTT(client,data):
	global topicToPublishMQTT
	(result,mid)=client.publish(topicToPublishMQTT,data)


def callback_UDP_to_MQTT(sock,client,data):
	data, addr = sock.recvfrom(1024) # buffer size is 1024 byte
	print("data :"+str(data))
	UDP_to_MQTT(client,encodeData(data))

# Create the two threads
try:
	client = mqtt.Client()
	client.connect(hostMQTT, port=portMQTT)
	sock = socket.socket(socket.AF_INET, # Internet
		                 socket.SOCK_DGRAM) # UDP
	sock.bind((UDP_IP, UDP_PORT_SENDER))
	while 1:
		data, addr = sock.recvfrom(1024) # buffer size is 1024 byte
		callback_UDP_to_MQTT(sock,client,data)
		time.sleep(0.5)
		pass
except:
   print "Error: unable to start thread"


