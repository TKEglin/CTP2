import paho.mqtt.client as mqtt
from heucod import HeucodEvent
import time

client = mqtt.Client()
client.connect("127.0.0.1", 1883)

event = HeucodEvent()

event.event_type = "MQTT.JSONtest.eventtest"
event.id_ = 25
event.sensor_location = "Local Network"
event.timestamp = time.time()

event_json = event.to_json()

client.publish("Test", event_json)
client.disconnect()