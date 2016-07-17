#!/bin/bash
python /home/linklabs/Octanis1-Field-Station/src/status_reporter.py &>> /var/log/field_station.log &
echo $! > /var/run/status_reporter.pid
