from FW_web_client import FW_TCP_client
from FW_datatypes import MQTT_device
from typing import List

client = FW_TCP_client("192.168.0.223", 2001)

devices: List[MQTT_device] = client.request_device_data()

device = MQTT_device(
)

device.name = "test"


device2 = device

device2.name="changed"

print(device.name)
