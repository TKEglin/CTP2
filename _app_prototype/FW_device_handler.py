import paho.mqtt.client as mqtt
from threading import Thread
from queue import Queue
from FW_MQTT_devices import MQTT_device, FW_Device_Message


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
        self.MQTT_client.subscribe(topic)

    def start_listener(self):
        """Listens at the given topic and pushes detected messages to the message_queue given in the constructor"""
        Thread(target=self.listener, daemon=True).start()
    
    def listener(self):
        self.MQTT_client.loop_forever()
    
    def message_received(self, client, userdata, message):
        # Add message to queue
        fw_message: FW_Device_Message

        fw_message.message 

        self.message_queue.put()




    #                          #
    # Publishing Functionality #
    #                          #
    def publish(self, topic: str, message: str):
        self.MQTT_client.publish(topic, message)
