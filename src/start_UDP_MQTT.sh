#!/bin/bash
python /home/linklabs/Octanis1-Field-Station/src/UDP_MQTT.py &>> /var/log/field_station.log &
echo $! > /var/run/UDP_MQTT.pid
