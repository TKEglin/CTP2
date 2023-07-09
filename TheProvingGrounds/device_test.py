from FW_device_handler import FW_MQTT_handler



handler = FW_MQTT_handler("127.0.0.1", 1883)

handler.subscribe("TestTopic1")