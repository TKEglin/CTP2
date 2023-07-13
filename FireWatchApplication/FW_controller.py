from queue import Queue
from time import sleep, time
from typing import List, Dict
import json
from itertools import chain

from heucod import HeucodEventType as HEvent
from FW_datatypes import MQTT_device, FW_room, FW_Device_Message
from FW_web_client import FW_TCP_client
from FW_MQTT_handler import FW_MQTT_handler


UNWATCHED_TIME_LIMIT = 1200 # seconds

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
        # List of warning devices.
        self.warning_devices: List[MQTT_device] = list()
        # List of sensor devices. Used to subscribe to topics
        self.sensor_devices:  List[MQTT_device] = list()
        # List of of unwatched devices
        self.unwatched_devices: List[MQTT_device] = list()
        # List of watched devices that are using power
        self.devices_in_use: List[MQTT_device] = list()
        # Used to see if the longest unwatched has changed, so new timestamp can be sent to server
        self.longest_unwatched_uid = -1

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
        for device in chain(self.sensor_devices, self.watched_devices):
            device: MQTT_device
            topic = device.generate_subscription_topic()
            self.device_handler.subscribe(topic)

        self.device_handler.start_listener()
        print("")

        # Sending startup event to web server
        if(restart):
            self.web_client.send_event(HEvent.SystemRestart)
        else:
            self.web_client.send_event(HEvent.SystemOn)

        # Main control loop
        while True:
            # Checking if longest unwatched has changed and web server timestamp needs to be updated
            #   This method relies on the fact that the first element of the unwatched_devices list
            #   will have been in there the longest, and thus have the longest unwatched time.
            if(self.unwatched_devices and 
               self.unwatched_devices[0].uid != self.longest_unwatched_uid):
                self.longest_unwatched_uid = self.unwatched_devices[0].uid
                self.web_client.send_unwatched_timestamp(int(self.unwatched_devices[0].unwatched_start_time))
            elif(not self.unwatched_devices):   # If list is empty, reset unwatched UID
                self.longest_unwatched_uid = -1 
                
            # Checking for time exceeded on at least one unwatched device
            time_exceeded = False
            for device in self.unwatched_devices:
                device: MQTT_device
                time_elapsed = time() - device.unwatched_start_time
                if(time_elapsed > UNWATCHED_TIME_LIMIT):
                    time_exceeded = True
                    
            if(time_exceeded):
                print("Unwatched safe time limit exceeded!")
                self.web_client.send_event(HEvent.TimelimitExceeded)
                
                for room in self.occupied_rooms.values():
                    for device in room.warning_devices:
                        self.web_client.send_event(HEvent.TurningOnWarningLight, device.room)
                    # Publishing turn on message for device
                    message = "{\"" + device.type.actuator_value_name + "\": \"" + device.type.actuator_enable + "\"}" 
                    self.device_handler.publish(device.generate_publish_topic(), message)
                
                for device in self.watched_devices:
                    self.web_client.send_event(HEvent.CuttingPowerToDevice, device.room)
                    # Publishing cut power message for device
                    message = "{\"" + device.type.actuator_value_name + "\": \"" + device.type.actuator_disable + "\"}" 
                    self.device_handler.publish(device.generate_publish_topic(), message)
                
                return 1 # Return value 1 indicates time limit exceeded


            # Processing messages
            while not self.message_queue.empty():
                message: FW_Device_Message
                message = self.message_queue.get()
                
                json_object = json.loads(message.payload)
                device : MQTT_device = self.devices[message.device_uid]
                room   : FW_room     = self.rooms[device.room]
                state  : str         = json_object[device.type.sensor_value_name]
                
                print(f"Received payload: {message.payload} | Room: {device.room} | UID: {device.uid}")
                
                if(device.function == "Presence Sensor"):
                    # If occupant detected and room was not already occupied
                    if(state == "True" and not room.occupied):
                        # Adding room to occupied rooms
                        self.occupied_rooms[room.name] = room
                        room.occupied = True
                        print(f"    Room '{device.room}' now occupied.")
                        # If room has a watched device, watcher event is sent instead of occupant event
                        if(room.watched_device == True):
                            self.web_client.send_event(HEvent.WatcherDetected, device.room)                               
                        else:
                            self.web_client.send_event(HEvent.OccupantDetected, device.room)
                            
                        # updating unwatched flag of all watched devices in room 
                        for watched_device in room.watched_devices:
                            watched_device.unwatched = False
                            if(self.unwatched_devices.__contains__(watched_device)):
                                self.unwatched_devices.remove(watched_device)
                            # If this was the last unwatched device and there are items in use, send event to server
                            if(self.unwatched_devices.__len__() == 0 and self.devices_in_use.__len__() > 0):
                                self.web_client.send_event(HEvent.AllDevicesWatched)
                            
                    # If no occupant detected and room was previously occupied
                    elif(state == "False" and room.occupied):
                        room.occupied = False
                        print(f"    Room '{device.room}' no longer occupied.")
                        if(room.watched_device == True):
                            self.web_client.send_event(HEvent.WatcherLeftRoom, device.room)                               
                        else:
                            self.web_client.send_event(HEvent.OccupantLeftRoom, device.room)
                            
                        # Updating unwatched flag of all watched devices in room 
                        for w_device in room.watched_devices:
                            if(w_device.in_use):
                                w_device.unwatched = True
                                w_device.unwatched_start_time = time()
                                self.unwatched_devices.append(w_device)
                                self.web_client.send_event(HEvent.UnwatchedDevice, device.room)
                                
                        if(device.room in list(self.occupied_rooms.keys())):
                            self.occupied_rooms.pop(device.room)
                            
                        
                elif(device.function == "Power Plug"):
                    # if power above threshold and device was not in use
                    if(int(state) >= device.type.sensor_threshold and not device.in_use):
                        device.in_use = True
                        print(f"    Device with name '{device.name}' in room '{device.room}' now in use.")
                        self.web_client.send_event(HEvent.WatchedDeviceActivated, device.room)
                        
                        self.devices_in_use.append(device)
                        # If the room of the device is unoccupied, the device is unwatched
                        if(not self.rooms[device.room].occupied):
                            print(f"    Room '{device.room}' was not occupied when watched device activated.")
                            device.unwatched = True
                            device.unwatched_start_time = time()
                            self.unwatched_devices.append(device)
                            self.web_client.send_event(HEvent.UnwatchedDevice, device.room)
                        # If the newly activated and watched device is the only device in use
                        elif(self.devices_in_use.__len__() == 1):
                            self.web_client.send_event(HEvent.AllDevicesWatched)
                            
                    # else if power below threshold and device was in use
                    elif(int(state) < device.type.sensor_threshold and device.in_use):
                        device.in_use = False
                        print(f"    Device with name '{device.name}' in room '{device.room}' no longer in use.")
                        self.web_client.send_event(HEvent.WatchedDeviceShutdown, device.room)
                        
                        if(self.unwatched_devices.__contains__(device)):
                            self.unwatched_devices.remove(device)
                        self.devices_in_use.remove(device)
                        if(self.devices_in_use.__len__() == 0):
                            self.web_client.send_event(HEvent.NoDevicesInUse)
                            
            sleep(0.1)