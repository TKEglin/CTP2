import json
from types import SimpleNamespace
from typing import List
from enum import Enum
from heucod import HeucodEventType as HEvent
from dataclasses import dataclass, replace as dataclass_replace


@dataclass
class MQTT_device_type:
    class MQTT_device_function(Enum):
        """Not currently in use"""
        PresenceSensor = (1, "Presence Sensor")
        WarningDevice  = (2, "Warning Device")
        PowerPlug      = (3, "Power Plug")

    brand_name:          str = None
    general_topic:       str = None # Overall topic that the device publishes to
    device_function:     str = None
    actuator_topic:      str = None  
    actuator_value_name: str = None # Example: "State" for a power plug
    actuator_enable:     str = None # JSON format. Example: "{"state": "ON"}"
    actuator_disable:    str = None # JSON format. Example: "{"state": "OFF"}"
    sensor_topic:        str = None
    sensor_value_name:   str = None # Example: "Occupancy" for a motion sensor

    def toJSON(self):
        return json.dumps(self, default=vars)
    
    def fromJSON(JSON_object):
        return json.loads(JSON_object, object_hook=lambda d: SimpleNamespace(**d))
    

class MQTT_device:
    uid: int
    name: str
    room: str
    function: str
    specific_topic: str = None # topic = type.general_topic + specific_topic + type.actuator_topic/.sensor_topic
    type: MQTT_device_type

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
        # Example           zigbee2mqtt   / kitchen   / 12         / set
        # Topic formatting: general_topic + room name + device uid + sensor topic
        topic = self.type.general_topic + "/" + self.room.replace(" ", "_") + "/" + str(self.uid) + "/" + self.type.sensor_topic

        return topic


class FW_room:
    name: str
    occupied: bool = False
    watched_device: bool = False
    watched_devices: List[MQTT_device] = list()
    sensor_devices:  List[MQTT_device] = list()
    warning_devices: List[MQTT_device] = list()


@dataclass
class FW_Device_Message:
    device_uid: int
    room: str
    payload: HEvent


