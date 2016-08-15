#!/bin/bash
python -u /home/linklabs/Octanis1-Field-Station/src/halt_btn.py &>> /var/log/field_station.log &
echo $! > /var/run/halt_btn.pid
