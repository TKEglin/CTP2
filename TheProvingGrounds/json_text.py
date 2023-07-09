from heucod import MQTT_device

device = MQTT_device()

device.device_name = "MotionSensor2"
device.device_location = "Kitchen"
device.device_type = "Sensor"
device.device_topic = "Zbigboi123_sensor22"

device_json = device.toJSON()

with open("FW_device_list.txt", "a") as file:
    file.write(device_json + "\n")


print(device_json)

device_loaded = MQTT_device.fromJSON(device_json)

print(device_loaded.device_name)