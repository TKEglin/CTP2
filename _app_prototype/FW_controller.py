from queue import Queue
from threading import Thread
from time import sleep, time
from FW_MQTT_devices import MQTT_device
from FW_web_client import FW_TCP_client
from FW_device_handler import FW_MQTT_handler
from FW_MQTT_devices import FW_Device_Message
from heucod import HeucodEvent
from heucod import HeucodEventType as HEvent


class FW_controller():
    
    def __init__(self, FW_client: FW_TCP_client):
        self.web_client = FW_client
        
        # WIll contain device information for each connected device
        self.devices = list()
        self.occupied_rooms = list()

        # Watchde device
        self.watched_device: MQTT_device

        # State flags and variables
        self.watched_device_running = False
        self.device_being_watched = False
        self.device_unwatched_time = 0

        self.message_queue = Queue()
        self.device_handler = FW_MQTT_handler("127.0.0.1", 1883, self.message_queue)

        self.controller()


    def controller(self):
        # Fetching device data from server
        self.devices = self.web_client.request_device_data()

        # Starting listener
        self.device_handler.subscribe("Sensor1Topic")
        self.device_handler.subscribe("Sensor2Topic")
        self.device_handler.subscribe("PlugTopic")

        print("Controller starting listener")

        self.device_handler.start_listener()

        # Main control loop
        event = HeucodEvent()

        print("Sending SystemOn event")
        event.event_type = HEvent.SystemOn
        event.event_type_enum = HEvent.SystemOn.value
        event.location = " "
        event.timestamp = time()
        self.web_client.send_event(event)

        while True:
            while not self.message_queue.empty():
                message: FW_Device_Message
                message = self.message_queue.get()

                print(f"Controller received event: {message.event}")

                
                # Checking for time exceeded
                if(self.watched_device_running and self.device_unwatched_time > 1200):
                    self.web_client.send_event(HeucodEvent(event_type = HEvent.TimelimitExceeded,
                                                           event_type_enum = HEvent.TimelimitExceeded.value,
                                                           location = " ", 
                                                           timestamp = time()))
                    
                    self.web_client.send_event(HeucodEvent(event_type = HEvent.TurningOnWarningLight,
                                                           event_type_enum = HEvent.TurningOnWarningLight.value,
                                                           location = "Living Room", 
                                                           timestamp = time()))
                    
                    self.web_client.send_event(HeucodEvent(event_type = HEvent.CuttingPowerToDevice,
                                                           event_type_enum = HEvent.CuttingPowerToDevice.value,
                                                           location = self.watched_device.room, 
                                                           timestamp = time()))
                    # TurnOffStove()
                    # TurnOnLight()
                
                # Occupant in kitchen or watched_device turned off
                if(message.event == HEvent.WatchedDeviceActivated):
                    self.watched_device_running = True
                    self.web_client.send_event(HeucodEvent(event_type = message.event,
                                                           event_type_enum = message.event.value,
                                                           location = message.device.room, 
                                                           timestamp = time()))

                
                if(message.event == HEvent.NullEvent)
                
                
                

                # Sending event to web server
                self.web_client.send_event(event)



            sleep(0.01)