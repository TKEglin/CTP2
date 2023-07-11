from queue import Queue
from time import sleep, time
from typing import List, Dict, Tuple
import json

from heucod import HeucodEvent
from heucod import HeucodEventType as HEvent
from FW_datatypes import MQTT_device, FW_room
from FW_web_client import FW_TCP_client
from FW_MQTT_handler import FW_MQTT_handler
from FW_datatypes import FW_Device_Message


UNWATCHED_TIME_LIMIT = 60 # seconds

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
        self.longest_unwatched: Tuple[int, int]

        self.message_queue = Queue()
        self.device_handler = FW_MQTT_handler("127.0.0.1", 1883, self.message_queue)
    

    def run_controller(self, restart: bool):
        # Fetching and processing device data from server
        self.devices = self.web_client.request_device_data()

        for device in list(self.devices.values()):
            device: MQTT_device
            room_name = device.room
            # Adding to rooms
            if(room_name not in list(self.rooms.keys())):
                self.rooms[room_name] = FW_room()
                self.rooms[room_name].name = room_name
            
            match device.function:
                case "Presence Sensor":
                    self.rooms[room_name].sensor_devices.append(device)
                    self.sensor_devices.append(device)
                case "Warning Device":
                    self.rooms[room_name].warning_devices.append(device)
                    self.warning_devices.append(device)
                case "Power Plug":
                    self.rooms[room_name].watched_devices.append(device)
                    self.watched_devices.append(device)
                    self.rooms[room_name].watched_device = True
            

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
        
        print("\n")

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
                time_elapsed = time() - device.unwatched_start_time
                if(time_elapsed > UNWATCHED_TIME_LIMIT):
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
                
                return 1 # Return value 1 indicates time limit exceeded


            # Processing messages
            while not self.message_queue.empty():
                message: FW_Device_Message
                message = self.message_queue.get()
                
                json_object = json.loads(message.payload)
                device: MQTT_device = self.devices[message.device_uid]
                room  : FW_room     = self.rooms[device.room]
                state : str         = json_object[device.type.sensor_value_name]
                
                print(f"Controller received payload: {message.payload} from room: {device.room} with uid: {device.uid}")
                
                if(device.function == "Presence Sensor"):
                    if(state == "True"):
                        # Only processing if occupied state has changed
                        if(not room.occupied):
                            # Adding room to occupied rooms
                            self.occupied_rooms[room.name] = room
                            # updating unwatched flag of all watched devices in room 
                            for watched_device in room.watched_devices:
                                watched_device.unwatched = False
                                if(self.unwatched_devices.__contains__(watched_device)):
                                    self.unwatched_devices.remove(watched_device)
                                    
                            room.occupied = True
                            print(f"    Room {device.room} now occupied.")
                            if(room.watched_device == True):
                                 self.web_client.send_event(HeucodEvent(event_type = HEvent.WatcherDetected,
                                                                        event_type_enum = HEvent.WatcherDetected.value,
                                                                        location = device.room,
                                                                        timestamp = time()))                               
                            else:
                                self.web_client.send_event(HeucodEvent(event_type = HEvent.OccupantDetected,
                                                                        event_type_enum = HEvent.OccupantDetected.value,
                                                                        location = device.room,
                                                                        timestamp = time()))
                            
                    elif(state == "False"):
                        if(room.occupied):
                            # Updating unwatched flag of all watched devices in room 
                            for watched_device in room.watched_devices:
                                if(watched_device.in_use):
                                    # Updating unwatched time only if device was not already unwatched
                                    if(watched_device.unwatched == False):
                                        watched_device.unwatched_start_time = time()
                                    watched_device.unwatched = True
                                    self.unwatched_devices.append(watched_device)
                                    
                            if(device.room in list(self.devices.keys())):
                                self.occupied_rooms.pop(device.room)
                                
                            room.occupied = False
                            print(f"    Room {device.room} no longer occupied.")
                            if(room.watched_device == True):
                                 self.web_client.send_event(HeucodEvent(event_type = HEvent.WatcherLeftRoom,
                                                                        event_type_enum = HEvent.WatcherLeftRoom.value,
                                                                        location = device.room,
                                                                        timestamp = time()))                               
                            else:
                                self.web_client.send_event(HeucodEvent(event_type = HEvent.OccupantLeftRoom,
                                                                        event_type_enum = HEvent.OccupantLeftRoom.value,
                                                                        location = device.room,
                                                                        timestamp = time()))
                        
                        
                elif(device.function == "Power Plug"):
                    if(int(state) >= device.type.sensor_threshold):
                        # Checking state first to avoid continuous updates of device
                        if(not device.in_use):
                            device.in_use = True
                            print(f"    Device with name {device.name} in room {device.room} now in use.")
                            self.web_client.send_event(HeucodEvent(event_type = HEvent.WatchedDeviceActivated,
                                                                    event_type_enum = HEvent.WatchedDeviceActivated.value,
                                                                    location = device.room,
                                                                    timestamp = time()))
                    else:
                        if(device.in_use):
                            device.in_use = False
                            print(f"    Device with name {device.name} in room {device.room} no longer in use.")
                            self.web_client.send_event(HeucodEvent(event_type = HEvent.WatchedDeviceShutdown,
                                                                    event_type_enum = HEvent.WatchedDeviceShutdown.value,
                                                                    location = device.room,
                                                                    timestamp = time()))
                            
            sleep(0.1)