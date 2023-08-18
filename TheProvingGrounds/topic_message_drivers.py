import paho.mqtt.client as mqtt


def SendOccupancyEvent(room: str, id: str, state: str):
    MQTT_client = mqtt.Client()
    MQTT_client.connect("127.0.0.1", 1883)

    MQTT_client.publish(f"Zigbee2mqtt/{room}/{id}/", "{\"occupancy\": \"" + state + "\"}")

def SendPowerEvent(room: str, id: str, state: str):
    MQTT_client = mqtt.Client()
    MQTT_client.connect("127.0.0.1", 1883)

    MQTT_client.publish(f"Zigbee2mqtt/{room}/{id}/", "{\"power\": \"" + state + "\"}")


SendPowerEvent("Kitchen", "4", "0")
# SendPowerEvent("Kitchen", "14", "0")
# SendPowerEvent("Basement", "11", "0")


SendOccupancyEvent("Kitchen", "1", "True")
SendOccupancyEvent("Bedroom", "7", "True")
SendOccupancyEvent("Bathroom", "6", "True")
SendOccupancyEvent("Living Room", "5", "True")
# SendOccupancyEvent("Bathroom"   , "10", "True")
# SendOccupancyEvent("Basement"   , "12", "False")

