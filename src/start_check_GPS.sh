#!/bin/bash
python -u /home/linklabs/Octanis1-Field-Station/src/check_GPS.py &>> /var/log/field_station.log &
echo $! > /var/run/check_GPS.pid
