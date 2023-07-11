from queue import Queue
from threading import Thread
from time import sleep, time
from typing import List, Dict, Tuple
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
    
    def __init__(self, FW_client: FW_TCP_client):
        self.web_client = FW_client
        
        # Dictionary of all connected devices mapped to UIDs:
        self.devices: Dict[int, MQTT_device]
        # Dict of room object mapped to room names. Contains UIDs of all room devices
        self.rooms: Dict[str, FW_room] = dict()
        # Dict of occupied rooms mapped to room names. Used to turn on warning devices only in occupied rooms
        self.occupied_rooms: Dict[str, FW_room] = dict()
        # List watched devices
        self.watched_devices: List[MQTT_device] = list()
        # List of warning devices
        self.warning_devices: List[MQTT_device] = list()
        # List of sensor devices. Used to subscribe to topics
        self.sensor_devices:  List[MQTT_device] = list()
        # List of of unwatched devices
        self.unwatched_devices: List[MQTT_device] = list()
        # A tuple of the uid and unwatched timestamp of longest unwatched device. Used for in for on web page
        self.longest_unwatched: Tuple[int, int] = ("", 0)

        self.message_queue = Queue()
        self.device_handler = FW_MQTT_handler("127.0.0.1", 1883, self.message_queue)
    


    def run_controller(self, restart: bool):
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
        if(restart):
            self.web_client.send_event(HeucodEvent(event_type = HEvent.SystemRestart,
                                                    event_type_enum = HEvent.SystemRestart.value,
                                                    timestamp = time()))
        else:
            self.web_client.send_event(HeucodEvent(event_type = HEvent.SystemOn,
                                                    event_type_enum = HEvent.SystemOn.value,
                                                    timestamp = time()))

        # Main control loop
        while True:
            # Checking for time exceeded on at least one unwatched device
            time_exceeded = False
            for device in self.unwatched_devices:
                device: MQTT_device
                                            # TODO: Implement "longest unwatched here"
                if(time() - device.unwatched_start_time > UNWATCHED_TIME_LIMIT):
                    time_exceeded = True
                    
            if(time_exceeded):
                print("Unwatched safe time limit exceeded!")
                self.web_client.send_event(HeucodEvent(event_type = HEvent.TimelimitExceeded,
                                                        event_type_enum = HEvent.TimelimitExceeded.value,
                                                        timestamp = time()))
                
                for room in self.occupied_rooms.values():
                    for device in room.warning_devices:
                        self.web_client.send_event(HeucodEvent(event_type = HEvent.TurningOnWarningLight,
                                                                event_type_enum = HEvent.TurningOnWarningLight.value,
                                                                location = device.room,
                                                                timestamp = time()))
                    # Publishing turn on message for device
                    message = "{\"" + device.type.actuator_value_name + "\": \"" + device.type.actuator_enable + "\"}" 
                    self.device_handler.publish(device.generate_publish_topic(), message)
                
                for device in self.watched_devices:
                    self.web_client.send_event(HeucodEvent(event_type = HEvent.CuttingPowerToDevice,
                                                            event_type_enum = HEvent.CuttingPowerToDevice.value,
                                                            location = device.room,
                                                            timestamp = time()))
                    # Publishing cut power message for device
                    message = "{\"" + device.type.actuator_value_name + "\": \"" + device.type.actuator_disable + "\"}" 
                    self.device_handler.publish(device.generate_publish_topic(), message)
                
                return 1


            # Processing messages
            while not self.message_queue.empty():
                message: FW_Device_Message
                message = self.message_queue.get()

                
                json_object = json.loads(message.payload)
                device: MQTT_device = self.devices[message.device_uid]
                room:   FW_room     = self.rooms[device.room]
                state:  str         = json_object[device.type.sensor_value_name]
                print(f"Controller received payload: {message.payload} from room: {device.room} with uid: {device.uid}")
                
                if(device.function == "Presence Sensor"):
                    print("Device is Presence Sensor")
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
                        for watched_device in room.watched_devices:
                            if(watched_device.in_use):
                                # Updating unwatched time only if device was not already unwatched
                                if(watched_device.unwatched == False):
                                    watched_device.unwatched_start_time = time()
                                watched_device.unwatched = True
                                self.unwatched_devices.append(watched_device)
                        self.web_client.send_event(HeucodEvent(event_type = HEvent.OccupantLeftRoom,
                                                                event_type_enum = HEvent.OccupantLeftRoom.value,
                                                                location = device.room,
                                                                timestamp = time()))
                        
                elif(device.function == "Power Plug"):
                    print("Device is Power Plug")
                    0
                            
                            
                

                
            sleep(1)