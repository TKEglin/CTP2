import json
from types import SimpleNamespace
from enum import Enum
from heucod import HeucodEventType as HEvent


class MQTT_device:
    uid: int
    name: str
    room: str
    device_JSON: str


class MQTT_device_type:
    class MQTT_device_function(Enum):
        Sensor = (1, "Sensor")
        Actuator = (2, "Actuator")
        SensorActuator = (3, "SensorActuator")

    brand_name: str
    general_topic: str      # Overall topic that the device publishes to
    device_type: MQTT_device_function
    actuator_topic: str     
    actuator_enable: str    # JSON format. Example: "{State: On}"
    actuator_disable: str   # JSON format. Example: "{State: Off}"
    sensor_topic: str
    sensor_value_name: str  # Example: "Occupancy" for a motion sensor

    def toJSON(self):
        return json.dumps(self, default=vars)
    
    def fromJSON(JSON_object):
        return json.loads(JSON_object, object_hook=lambda d: SimpleNamespace(**d))
    
class FW_Device_Message:
    state: str
    event: HEvent


