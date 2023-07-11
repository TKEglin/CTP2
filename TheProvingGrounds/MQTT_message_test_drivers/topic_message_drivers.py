import paho.mqtt.client as mqtt
from time import sleep


def SendOccupancyEvent(room: str, id: str, state: str):
    MQTT_client = mqtt.Client()
    MQTT_client.connect("127.0.0.1", 1883)

    MQTT_client.publish(f"Zigbee2mqtt/{room}/{id}/", "{\"occupancy\": \"" + state + "\"}")

def SendPowerEvent(room: str, id: str, state: str):
    MQTT_client = mqtt.Client()
    MQTT_client.connect("127.0.0.1", 1883)

    MQTT_client.publish(f"Zigbee2mqtt/{room}/{id}/", "{\"power\": \"" + state + "\"}")


SendPowerEvent("Kitchen", "17", "100")

SendOccupancyEvent("Kitchen", "18", "False")

# SendOccupancyEvent("Living Room", "20", "True")
# SendOccupancyEvent("Bathroom", "21", "True")