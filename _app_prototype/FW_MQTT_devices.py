import json
from types import SimpleNamespace
from enum import Enum
from heucod import HeucodEventType as HEvent


class MQTT_device_function(Enum):
    Sensor         = (1, "Sensor")
    Actuator       = (2, "Actuator")
    SensorActuator = (3, "SensorAcutator")

class MQTT_device_type:
    """Data about a MQTT device type. Will be used to instantiate each MQTT_device connected to the system"""
    name: str
    id: int
    topic: str
    function: MQTT_device_function

class MQTT_device:
    name : str               
    room : str               
    state: str          
    type : MQTT_device_type

    def toJSON(self):
        return json.dumps(self, default=vars)
    
    def fromJSON(JSON_object):
        return json.loads(JSON_object, object_hook=lambda d: SimpleNamespace(**d))
    
class FW_Device_Message:
    device: MQTT_device
    state: str
    event: HEvent
