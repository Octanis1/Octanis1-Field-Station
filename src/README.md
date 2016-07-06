Bridge UDP-MQTT
===============

## The goal of the bridge
The goal of this script is to recieve MQTT messages from 'A' and to transform them into UDP messages that are sent to 'B' and to recieve UDP messages from 'B' and to transform them into MQTT that are sent to 'A'.

# Configuration of the bridge
At the begin of the Python script, you can change the IP and the port of the differents actors.

# Test the bridge
To test the bridge, you can use the scripts _send\_mqtt.sh_ and _send\_udp.sh_. You just need to change the parameters at the begin of each script.


