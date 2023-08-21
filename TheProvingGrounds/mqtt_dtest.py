import paho.mqtt.client as mqtt


MQTT_client = mqtt.Client()
MQTT_client.connect("localhost", 1883)

topic, msg = "zigbee2mqtt/Bathroom/uid/3/Warning Device/set", "{\"color\": " + "{\"r\": 0,\"g\":255,\"b\":0}" + "}"

print(topic + " " + msg)

MQTT_client.publish(topic, msg)