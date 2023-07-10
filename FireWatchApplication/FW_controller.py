from queue import Queue
from threading import Thread
from time import sleep, time
from typing import List, Dict
import json
import sys

from heucod import HeucodEvent
from heucod import HeucodEventType as HEvent
from FW_datatypes import MQTT_device, FW_room, DFunction
from FW_web_client import FW_TCP_client
from FW_MQTT_handler import FW_MQTT_handler
from FW_datatypes import FW_Device_Message

UNWATCHED_TIME_LIMIT = 10


class FW_controller():
    # Dictionary of all connected devices mapped to UIDs:
    devices: Dict[int, MQTT_device]
    # Dict of room object mapped to room names. Contains UIDs of all room devices
    rooms: Dict[str, FW_room] = dict()
    # Dict of occupied rooms mapped to room names. Used to turn on warning devices only in occupied rooms
    occupied_rooms: Dict[str, FW_room] = dict()
    # List watched devices
    watched_devices: List[MQTT_device] = list()
    # List of warning devices
    warning_devices: List[MQTT_device] = list()
    # List of sensor devices. Used to subscribe to topics
    sensor_devices:  List[MQTT_device] = list()
    # List of of unwatched devices
    unwatched_devices: List[MQTT_device] = list()
    
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
            if(room not in list(self.rooms.keys())):
                self.rooms[room] = FW_room()
                self.rooms[room].name = room
            
            match device.function:
                case "Presence Sensor":
                    self.rooms[room].sensor_devices.append(device)
                    self.sensor_devices.append(device)
                case "Warning Device":
                    self.rooms[room].warning_devices.append(device)
                    self.warning_devices.append(device)
                case "Power Plug":
                    self.rooms[room].watched_devices.append(device)
                    self.watched_devices.append(device)
                    self.rooms[room].watched_device = True
            

        # Subscribing to topics and starting listener
        print("Controller starting listener")
        for device in self.sensor_devices:
            device: MQTT_device
            topic = device.generate_subscription_topic()
            self.device_handler.subscribe(topic)
        for device in self.watched_devices:
            device: MQTT_device
            topic = device.generate_subscription_topic()
            self.device_handler.subscribe(topic)

        self.device_handler.start_listener()

        # Sending startup event to web server
        self.web_client.send_event(HeucodEvent(event_type = HEvent.SystemOn,
                                               event_type_enum = HEvent.SystemOn.value,
                                               timestamp = time()))


        # Main control loop
        while True:
            print("\nRunning control loop...")
            # Checking for time exceeded on unwatched devices
            time_exceeded = False
            for device in self.unwatched_devices:
                device: MQTT_device
                print(device.unwatched_start_time)
                print(time())
                print(time() - device.unwatched_start_time)
                if(time() - device.unwatched_start_time > UNWATCHED_TIME_LIMIT):
                    time_exceeded = True
                    
            if(time_exceeded):
                self.web_client.send_event(HeucodEvent(event_type = HEvent.TimelimitExceeded,
                                                        event_type_enum = HEvent.TimelimitExceeded.value,
                                                        timestamp = time()))
                
                for device in self.warning_devices:
                    self.web_client.send_event(HeucodEvent(event_type = HEvent.TurningOnWarningLight,
                                                            event_type_enum = HEvent.TurningOnWarningLight.value,
                                                            location = device.room,
                                                            timestamp = time()))
                    # -- Publish turn on message to topic
                
                for device in self.watched_devices:
                    self.web_client.send_event(HeucodEvent(event_type = HEvent.CuttingPowerToDevice,
                                                            event_type_enum = HEvent.CuttingPowerToDevice.value,
                                                            location = device.room,
                                                            timestamp = time()))
                    # -- Publish cut power message to topic
                
                # ----------------------------------------------
                # --!! Implement system reset functionality !!--
                # ----------------------------------------------


            # Processing messages
            while not self.message_queue.empty():
                message: FW_Device_Message
                message = self.message_queue.get()

                print(f"Controller received payload: {message.payload}")
                
                json_object = json.loads(message.payload)
                device: MQTT_device = self.devices[message.device_uid]
                room:   FW_room     = self.rooms[device.room]
                state:  str         = json_object[device.type.sensor_value_name]
                
                if(device.function == "Presence Sensor"):
                    print("Device is Presence sensor")
                    if(state == "True"):
                        # Adding room to occupied rooms
                        self.occupied_rooms[room.name] = room
                        # updating unwatched flag of all watched devices in room 
                        for watched_device in room.watched_devices:
                            watched_device.unwatched = False
                            if(self.unwatched_devices.__contains__(watched_device)):
                                self.unwatched_devices.remove(watched_device)
                        self.web_client.send_event(HeucodEvent(event_type = HEvent.OccupantDetected,
                                                                event_type_enum = HEvent.OccupantDetected.value,
                                                                location = device.room,
                                                                timestamp = time()))
                    elif(state == "False"):
                        # Removing room from occupied rooms
                        if(device.room in list(self.devices.keys())):
                            self.occupied_rooms.pop(device.room)
                        # and updating unwatched flag of all watched devices in room 
                        for watched_device in room.warning_devices:
                            # Updating unwatched time only if device was not already unwatched
                            if(watched_device.unwatched == False):
                                watched_device.unwatched_start_time = time()
                            watched_device.unwatched = True
                            self.unwatched_devices.append(watched_device)
                        self.web_client.send_event(HeucodEvent(event_type = HEvent.OccupantLeftRoom,
                                                                event_type_enum = HEvent.OccupantLeftRoom.value,
                                                                location = device.room,
                                                                timestamp = time()))
                        
                elif(device.function == "Warning Device"):
                    0
                    
                elif(device.function == "Power Plug"):
                    0
                            
                            
                

                
            sleep(5)