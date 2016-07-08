topic="topic"
port=1883
mosquitto_pub -h "localhost"  -t $topic -m $1 -q 0
