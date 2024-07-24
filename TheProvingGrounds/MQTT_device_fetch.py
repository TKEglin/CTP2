import paho.mqtt.client as mqtt
from threading import Thread

def on_message(self, client, userdata, message):
    print(f"Recevied message on topic {message.topic}")
    print(str(bytes.decode(message.payload, "utf-8")))

def listener(MQTT_client):
    MQTT_client.loop_forever()

MQTT_client = mqtt.Client()
MQTT_client.connect("192.168.0.104", 1883)
MQTT_client.on_message = on_message

MQTT_client.subscribe("#")

Thread(target=listener, args=(MQTT_client), daemon=True).start()