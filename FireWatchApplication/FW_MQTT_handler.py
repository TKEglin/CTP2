import paho.mqtt.client as mqtt
from threading import Thread
from queue import Queue
from FW_datatypes import FW_Device_Message


class FW_MQTT_handler:
    def __init__(self, broker_ip: str, broker_port: int, message_queue: Queue) -> None:
        self.message_queue = message_queue

        self.MQTT_client = mqtt.Client()
        self.MQTT_client.on_message = self.message_received
        self.MQTT_client.connect(broker_ip, broker_port)
        

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
        self.MQTT_client.loop_forever()
    
    def message_received(self, client, userdata, message):
        # Add message to queue
        fw_message = FW_Device_Message()

        # Retrieving UID and room from topic
        topic_components: str = message.topic.split("/")
        fw_message.device_uid = int(topic_components[2])
        fw_message.room       = topic_components[1]
        fw_message.payload    = bytes.decode(message.payload, "utf-8")

        self.message_queue.put(fw_message)


    #                          #
    # Publishing Functionality #
    #                          #
    def publish(self, topic: str, message: str):
        self.MQTT_client.publish(topic, message)
