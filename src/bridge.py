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

def decodeBase64(data):
	return base64.b64decode(data)

def decodeData(strJSON):
	tmp=ast.literal_eval(str(strJSON))	
	tmp['data']=decodeBase64(tmp['data'])
	#resultat="{\"devEUI\":\""+ str(tmp['devEUI'])  +"\",\"fPort\":"+ str(tmp['fPort']) +",\"gatewayCount\":" + str(tmp['gatewayCount']) +",\"rssi\":" + str(tmp['rssi']) +",\"data\":\""+ str(tmp['data'])  + "\"}"
	return str(tmp['data'])

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    client.subscribe(topicToSubscribeMQTT)

# The callback for when a PUBLISH message is received from the server.
def MQTT_to_UDP(client, userdata, msg):
	global UDP_IP, UDP_PORT_RECIEVER
	sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
	sock.sendto(decodeData(msg.payload), (UDP_IP, UDP_PORT_RECIEVER))

def UDP_to_MQTT(client,data):
	global topicToPublishMQTT
	(result,mid)=client.publish(topicToPublishMQTT,data)


def callback_UDP_to_MQTT(sock,client,data):
	data, addr = sock.recvfrom(1024) # buffer size is 1024 byte
	UDP_to_MQTT(client,decodeData(data))

# Create the two threads
try:
	client = mqtt.Client()
	client.on_connect = on_connect
	client.on_message = MQTT_to_UDP
	client.connect(hostMQTT, port=portMQTT)
	client.loop_forever()

	client = mqtt.Client()
	client.connect(hostMQTT, port=portMQTT)
	sock = socket.socket(socket.AF_INET, # Internet
		                 socket.SOCK_DGRAM) # UDP
	sock.bind((UDP_IP, UDP_PORT_SENDER))
	while 1:
		data, addr = sock.recvfrom(1024) # buffer size is 1024 byte
		UDP_to_MQTT(sock,client,data)
		time.sleep(20)
		pass
except:
   print "Error: unable to start thread"


