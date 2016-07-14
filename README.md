# Octanis1-Field-Station
Software that runs on the Raspberry Pi in the field. Acts as a LoRa tranceiver and MAVLink protocol handler. Must accept and relay MAVLink commands from APM Planner / QGcontrol.

[Software running on the field station but not in this repository.](http://wiki.octanis.org/orb/fieldbasestation)

UDP <-> MQTT bridge
===============

### The goal of the bridge
The goal of this script is to receive MQTT messages from 'A' and to transform them into UDP messages that are sent to 'B' and to receive UDP messages from 'B' and to transform them into MQTT that are sent to 'A'.

### Configuration of the bridge
At the beginning of the Python scripts, you can change the IP and the port of the differents actors.

### Test the bridge
To test the bridge, you can use the scripts _send\_mqtt.sh_ and _send\_udp.sh_. You just need to change the parameters at the begin of each script.
To listen : mosquitto_sub -t topic -q 1 and nc -l -u -p 43000


status_reporter script
===============
Sends RADIO_STATUS message to the UDP endpoint (APM Planner) which includes last RSSI from TX MQTT topic. It also sends a HEARTBEAT with sysid 24.


Halt button script
===============
Listens to a rising edge on GPIO pin 16 (hardware pin, not BCM) and halts the operating system if risen.


 

