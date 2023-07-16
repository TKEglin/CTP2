import paho.mqtt.client as mqtt


def SendOccupancyEvent(room: str, id: str, state: str):
    MQTT_client = mqtt.Client()
    MQTT_client.connect("127.0.0.1", 1883)

    MQTT_client.publish(f"Zigbee2mqtt/{room}/{id}/", "{\"occupancy\": \"" + state + "\"}")

def SendPowerEvent(room: str, id: str, state: str):
    MQTT_client = mqtt.Client()
    MQTT_client.connect("127.0.0.1", 1883)

    MQTT_client.publish(f"Zigbee2mqtt/{room}/{id}/", "{\"power\": \"" + state + "\"}")


SendPowerEvent("køkken", "1", "0")
# SendPowerEvent("Kitchen", "14", "0")
# SendPowerEvent("Basement", "11", "0")


SendOccupancyEvent("køkken"    , "3", "False")
SendOccupancyEvent("bad", "4", "False")
# SendOccupancyEvent("Garage"     , "6", "True")
# SendOccupancyEvent("Bedroom"    , "8", "False")
# SendOccupancyEvent("Bathroom"   , "10", "True")
# SendOccupancyEvent("Basement"   , "12", "False")

