from queue import Queue
from threading import Thread
from time import sleep, time
from typing import List, Dict

from heucod import HeucodEvent
from heucod import HeucodEventType as HEvent
from FW_datatypes import MQTT_device, FW_room
from FW_web_client import FW_TCP_client
from FW_MQTT_handler import FW_MQTT_handler
from FW_datatypes import FW_Device_Message

UNWATCHED_TIME_LIMIT = 1200000000


class FW_controller():
    # Dictionary of all connected devices mapped to UIDs:
    devices = Dict[int, MQTT_device]
    # Dict of room object mapped to room names. Contains UIDs of all room devices
    rooms: Dict[str, FW_room] = dict()
    # List of names of occupied rooms of the rooms dict
    occupied_rooms: List[str] = list()
    # List watched devices
    watched_devices: List[MQTT_device] = list()
    # List of warning devices
    warning_devices: List[MQTT_device] = list()
    # List of sensor devices. Used to subscribe to topics
    sensor_devices:  List[MQTT_device] = list()
    
    def __init__(self, FW_client: FW_TCP_client):
        self.web_client = FW_client

        self.message_queue = Queue()
        self.device_handler = FW_MQTT_handler("127.0.0.1", 1883, self.message_queue)

        self.controller()


    def controller(self):
        # Fetching and processing device data from server
        self.devices = self.web_client.request_device_data()

        for device in list(self.devices.values()):
            device: MQTT_device
            room = device.room
            # Adding to rooms
            print("\nloop start")
            print("room: " + room + " device name: " + device.name)
            print("room in dict" + str(room not in list(self.rooms.keys())))
            if(room not in list(self.rooms.keys())):
                self.rooms[room] = FW_room()
                print("room " + room + " instantiated")
                self.rooms[room].name = room
            
            print("adding device to function lists")
            match device.function:
                case "Presence Sensor":
                    self.rooms[room].sensor_devices.append(device)
                    self.sensor_devices.append(device)
                case "Warning Device":
                    self.rooms[room].warning_devices.append(device)
                case "Power Plug":
                    self.rooms[room].watched_devices.append(device)
                    self.watched_devices.append(device)
                    self.rooms[room].watched_device = True
            
            print("loop end\n")

        # Subscribing to topics and starting listener
        print("Controller starting listener")
        for device in self.sensor_devices:
            device: MQTT_device
            topic = device.generate_subscription_topic()
            self.device_handler.subscribe(topic)

        self.device_handler.start_listener()

        # Sending startup event to web server
        self.web_client.send_event(HeucodEvent(event_type = HEvent.SystemOn,
                                               event_type_enum = HEvent.SystemOn.value,
                                               location = "_", 
                                               timestamp = time()))

        # Main control loop
        while True:
            # Checking for time exceeded on unwatched device
            if(0
                # !!write test here!!
               ):
                self.web_client.send_event(HeucodEvent(event_type = HEvent.TimelimitExceeded,
                                                        event_type_enum = HEvent.TimelimitExceeded.value,
                                                        location = "", 
                                                        timestamp = time()))
                
                for device in self.warning_devices:
                    device: MQTT_device
                    self.web_client.send_event(HeucodEvent(event_type = HEvent.TurningOnWarningLight,
                                                            event_type_enum = HEvent.TurningOnWarningLight.value,
                                                            location = device.room,
                                                            timestamp = time()))
                
                for device in self.watched_devices:
                    device: MQTT_device
                    self.web_client.send_event(HeucodEvent(event_type = HEvent.CuttingPowerToDevice,
                                                        event_type_enum = HEvent.CuttingPowerToDevice.value,
                                                        location = device.room,
                                                        timestamp = time()))
                # TurnOffStove()
                # TurnOnLight()

            if not self.message_queue.empty():
                message: FW_Device_Message
                message = self.message_queue.get()

                print(f"Controller received event: {message.event}")

                



                # Occupancy change
                

                
            sleep(0.1)