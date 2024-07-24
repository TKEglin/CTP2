import paho.mqtt.client as mqtt
from threading import Thread
from queue import Queue
from FW_datatypes import FW_Device_Message


class FW_MQTT_handler:
    def __init__(self, broker_ip: str, broker_port: int, message_queue: Queue) -> None:
        self.message_queue = message_queue

        self.MQTT_client = mqtt.Client()
        self.MQTT_client.on_message = self.message_received
        self.MQTT_client.on_connect = self.connection_established
        self.MQTT_client.on_connect_fail = self.connection_failed

        self.MQTT_client.username_pw_set(username = "LoftNet", password = "emcue123")
        print("Connecting to MQTT client...")
        self.MQTT_client.connect(broker_ip, broker_port)
    
    def connection_established(client, userdata, flags, rc, properties):
        print(f"Connected to MQTT broker with result code {str(rc)}")

    def connection_failed(client, userdata, flags, rc):
        print("Failed to connect to MQTT broker. Restart the client to try again.")

    #                         #
    # Listening Functionality #
    #                         #
    def subscribe(self, topic: str):
        print("    Subscribing to topic: " + topic)
        self.MQTT_client.subscribe(topic)

    def start_listener(self):
        """Listens at the given topic and pushes detected messages to the message_queue given in the constructor"""
        Thread(target=self.listener, daemon=True).start()
    
    def listener(self):
        print("MQTT handler starting listener")
        self.MQTT_client.loop_forever()
    
    def message_received(self, client, userdata, message):
        fw_message = FW_Device_Message()

        # Retrieving UID and room from topic
        # Topic format must be "{DeviceName}/{UID}uid"
        topic_components      = message.topic.split("/")
        fw_message.device_uid = int(topic_components[2][:-3])
        fw_message.payload    = bytes.decode(message.payload, "utf-8")

        self.message_queue.put(fw_message)


    #                          #
    # Publishing Functionality #
    #                          #
    def publish(self, topic: str, message: str):
        print(f"Publishing to topic {topic}: {message}")
        self.MQTT_client.publish(topic, message)
