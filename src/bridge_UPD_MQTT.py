#!/usr/bin/python

"""
	Installation of paho : pip install paho-mqtt
	Sorry, the name is ..._UPD_... instead of ..._UDP_...
	line 41 and 69 : there are the two lines we need to decode base64 in the comments
"""

import paho.mqtt.client as mqtt
import socket
import thread
import time
import base64
import json

UDP_IP = "localhost"
UDP_PORT_SENDER = 44000
UDP_PORT_RECIEVER = 43000 # the bridge send MQTT message to a the UDP Reciever
hostMQTT="192.168.3.3"
portMQTT=1883
topicToPublishMQTT="topic"
topicToSubscribeMQTT="topic"

def decodeBase64(data):
	return base64.b64decode(data)

def decodeData(strJSON):
	tmp=strJSON	
	tmp['data']=decodeBase64(tmp['data'])
	return tmp

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    client.subscribe(topicToSubscribeMQTT)

# The callback for when a PUBLISH message is received from the server.
def MQTT_to_UDP(client, userdata, msg):
	global UDP_IP, UDP_PORT_RECIEVER
	sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
	sock.sendto(decodeData(msg.payload), (UDP_IP, UDP_PORT_RECIEVER))
	#sock.sendto(msg.payload, (UDP_IP, UDP_PORT_RECIEVER))

def UDP_to_MQTT(client,data):
	global topicToPublishMQTT
	(result,mid)=client.publish(topicToPublishMQTT,data)

""" the function which transform MQTT message into UDP message """
def bridge_MQTT_to_UDP(name_thread,delay):
	# I've tested and it works ! (use the script send_mqtt.sh and netcat to recieve the message)
	client = mqtt.Client()
	client.on_connect = on_connect
	client.on_message = MQTT_to_UDP
	client.connect(hostMQTT, port=portMQTT)
	time.sleep(delay)
	client.loop_forever()

""" the function which transform UDP message into MQTT message """
def bridge_UDP_to_MQTT(name_thread,delay):
	# I've tested and it works ! (use the script send_udp.sh and mosquitto_sub to recieve the message)
	global UDP_IP, UDP_PORT_SENDER
	client = mqtt.Client()
	client.connect(hostMQTT, port=portMQTT)
	sock = socket.socket(socket.AF_INET, # Internet
		                 socket.SOCK_DGRAM) # UDP
	sock.bind((UDP_IP, UDP_PORT_SENDER))
	while True:
		data, addr = sock.recvfrom(1024) # buffer size is 1024 byte
		UDP_to_MQTT(client,decodeData(data))
		#UDP_to_MQTT(client,data)
		time.sleep(delay)

# Create the two threads
try:
   thread.start_new_thread(bridge_MQTT_to_UDP, ("MQTT to UDP", 100, ))
   thread.start_new_thread(bridge_UDP_to_MQTT, ("UDP to MQTT", 100, ))
except:
   print "Error: unable to start thread"

while 1:
   pass
