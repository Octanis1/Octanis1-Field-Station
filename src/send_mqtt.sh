$topic="topic"
$port=1883
mosquitto_pub -p $port -t $topic -m $1 -q 1
