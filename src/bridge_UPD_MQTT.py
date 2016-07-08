#!/usr/bin/python

"""
	Installation of paho : pip install paho-mqtt
"""

import paho.mqtt.client as mqtt
import socket
import thread
import time

UDP_IP = "localhost"
UDP_PORT_SENDER = 44000
UDP_PORT_RECIEVER = 43000 # the bridge send MQTT message to a the UDP Reciever
hostMQTT="localhost"
portMQTT=1883
topicToPublishMQTT="application/70b3d57ed0000172/node/f03d291000000046/tx"
topicToSubscribeMQTT="application/70b3d57ed0000172/node/+/rx"

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    client.subscribe(topicToSubscribeMQTT)

# The callback for when a PUBLISH message is received from the server.
def MQTT_to_UDP(client, userdata, msg):
	global UDP_IP, UDP_PORT_RECIEVER
	sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
	sock.sendto(msg.payload, (UDP_IP, UDP_PORT_RECIEVER))

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
	client.loop_forever()
	time.sleep(delay)

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
		UDP_to_MQTT(client,data)
		time.sleep(delay)

# Create the two threads
try:
   thread.start_new_thread(bridge_MQTT_to_UDP, ("MQTT to UDP", 2, ))
   thread.start_new_thread(bridge_UDP_to_MQTT, ("UDP to MQTT", 2, ))
except:
   print "Error: unable to start thread"

while 1:
   pass
