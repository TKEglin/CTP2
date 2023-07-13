import json
from types import SimpleNamespace
from typing import List
from enum import Enum
from dataclasses import dataclass


class DFunction(Enum):
    """Enumerator of the different device functions"""
    PresenceSensor = (1, "Presence Sensor")
    WarningDevice  = (2, "Warning Device")
    PowerPlug      = (3, "Power Plug")

@dataclass
class MQTT_device_type:
    brand_name:          str = None
    general_topic:       str = None # Overall topic that the device publishes to
    device_function:     str = None
    # Actuator values
    actuator_topic:      str = None  
    actuator_value_name: str = None # Example: "State" for a power plug
    actuator_enable:     str = None # JSON format. Example: "{"state": "ON"}"
    actuator_disable:    str = None # JSON format. Example: "{"state": "OFF"}"
    # Sensor values
    sensor_topic:        str = None
    sensor_value_name:   str = None # Example: "Occupancy" for a motion sensor
    sensor_threshold:    int = None # Used for power plugs and similar devices

    def toJSON(self):
        return json.dumps(self, default=vars)
    
    def fromJSON(JSON_object):
        return json.loads(JSON_object, object_hook=lambda d: SimpleNamespace(**d))
    

class MQTT_device:
    uid: int
    name: str
    room: str
    function: str
    specific_topic: str = None
    type: MQTT_device_type
    in_use: bool = False # Set for watched devices when they are in use
    unwatched: bool = False
    unwatched_start_time: int = None

    def fromSQL(sql_rows: list) -> dict():
        """Takes the rows of a sql SELECT result and converts it to a python dict of MQTT_devices"""
        devices = dict()

        for i in range(sql_rows.__len__()):
            device = MQTT_device()
            device.uid      = sql_rows[i][0]
            device.name     = sql_rows[i][1]
            device.room     = sql_rows[i][3]
            device.type:MQTT_device_type = MQTT_device_type.fromJSON(sql_rows[i][4])
            device.function = device.type.device_function
            devices[device.uid] = device

        return devices
    
    def generate_subscription_topic(self) -> str:
        # Example           zigbee2mqtt   / kitchen   / 12         / 
        # Topic formatting: general_topic + room name + device uid + sensor topic
        topic = self.type.general_topic + "/" + self.room + "/" + str(self.uid) + "/" + self.type.sensor_topic

        return topic

    def generate_publish_topic(self) -> str:
        # Example           zigbee2mqtt   / kitchen   / 12         / 
        # Topic formatting: general_topic + room name + device uid + actuator topic
        topic = self.type.general_topic + "/" + self.room + "/" + str(self.uid) + "/" + self.type.actuator_topic

        return topic



@dataclass
class FW_room:
    name          : str
    occupied      : bool = False
    watched_device: bool = False
    
    def __init__(self) -> None:
        self.watched_devices: List[MQTT_device] = list()
        self.sensor_devices:  List[MQTT_device] = list()
        self.warning_devices: List[MQTT_device] = list()


@dataclass
class FW_Device_Message:
    device_uid: int = None
    room: str       = None
    payload         = None


