import paho.mqtt.client as mqtt


MQTT_client = mqtt.Client()
MQTT_client.connect("127.0.0.1", 1883)
