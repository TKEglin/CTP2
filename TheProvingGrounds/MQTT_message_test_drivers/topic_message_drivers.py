import paho.mqtt.client as mqtt

def occ_kitchen(state: str):
    MQTT_client = mqtt.Client()
    MQTT_client.connect("127.0.0.1", 1883)

    MQTT_client.publish("Zigbee2mqtt/Kitchen/18/", "{\"occupancy\": \"" + state + "\"}")

def occ_living(state: str):
    MQTT_client = mqtt.Client()
    MQTT_client.connect("127.0.0.1", 1883)

    MQTT_client.publish("Zigbee2mqtt/Living_Room/20/", "{\"occupancy\": \"" + state + "\"}")

occ_kitchen("False")
occ_living("False")