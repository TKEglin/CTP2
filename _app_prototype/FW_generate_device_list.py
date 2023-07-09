from heucod import MQTT_device

device = MQTT_device()

device.device_name = "PowerPlug"
device.device_location = "Kitchen"
device.device_type = "Plug"
device.device_topic = "MQTT_PowerPlug"

device_json = device.toJSON()

with open("FW_device_list.txt", "a") as file:
    file.write(device_json + "\n")
