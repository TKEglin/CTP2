from FW_datatypes import MQTT_device_type

print("\nImmax NEO 07048L power plug JSON:")
Immax_NEO_07048L = MQTT_device_type(
    brand_name          = "Immax NEO 07048L power unit",
    general_topic       = "Zigbee2mqtt",
    device_function     = "Power Plug",
    actuator_topic      = "set",
    actuator_value_name = "state",
    actuator_enable     = "ON",
    actuator_disable    = "OFF",
    sensor_topic        = "",
    sensor_value_name   = "power",
    sensor_threshold    = 10        # In use not in use threshold
).toJSON()
print(Immax_NEO_07048L)
jsontest = MQTT_device_type.fromJSON(Immax_NEO_07048L)

print("\nGLEDOPTO GL-MC-001PK LED light JSON:")
GLEDOPTO_GL_MC_001PK = MQTT_device_type(
    brand_name          = "GLEDOPTO GL-MC-001PK",
    general_topic       = "Zigbee2mqtt",
    device_function     = "Warning Device",
    actuator_topic      = "set",
    actuator_value_name = "state",
    actuator_enable     = "ON",
    actuator_disable    = "OFF",
).toJSON()
print(GLEDOPTO_GL_MC_001PK)
jsontest = MQTT_device_type.fromJSON(GLEDOPTO_GL_MC_001PK)

print("\nIKEA Motion Sensor JSON:")
IKEA_E1525_E1745 = MQTT_device_type(
    brand_name        = "IKEA E1525/E1745",
    general_topic     = "Zigbee2mqtt",
    device_function   = "Presence Sensor",
    sensor_topic      = "",
    sensor_value_name = "occupancy",
).toJSON()
print(IKEA_E1525_E1745)
jsontest = MQTT_device_type.fromJSON(IKEA_E1525_E1745)
