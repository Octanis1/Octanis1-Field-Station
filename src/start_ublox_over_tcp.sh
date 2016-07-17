#!/bin/bash
socat tcp-l:2000,reuseaddr,fork file:/dev/ttyACM0,nonblock,waitlock=/var/run/ttyACM0.lock,b9600,iexten=0,raw &>> /var/log/ublox_over_tcp.log &
echo $! > /var/run/ublox_over_tcp.pid
