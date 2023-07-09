from FW_MQTT_devices import MQTT_device_type



device_type = MQTT_device_type()

device_type.brand_name = "TestBrand"

print("test")

print(device_type.toJSON())

json_Str = "{\"brand_name\": \"TestBrand\"}"

device = MQTT_device_type.fromJSON(json_Str)

print(device_type.brand_name)