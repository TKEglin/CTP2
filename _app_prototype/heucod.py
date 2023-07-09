from __future__ import annotations
import json
import re
from copy import deepcopy
from dataclasses import dataclass, replace as dataclass_replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Union
from uuid import UUID




class HeucodEventType(Enum):
    def __new__(cls, type_: int, description: str):
        obj = object.__new__(cls)
        obj._value_ = type_
        obj.description = description

        return obj

    def __int__(self):
        return self.value

    def __repr__(self) -> str:
        return self.description

    def __str__(self) -> str:
        return self.description

    # System Events 0-9
    NullEvent = (0, "FireWatch.System.NoEvent")
    SystemOn = (1, "FireWatch.System.SystemOn")
    SystemOff = (2, "FireWatch.System.SystemOff")

    # Sensor events 10-19
    WatchedDeviceActivated = (10, "FireWatch.Sensor.WatchedDeviceActivated")
    WatchedDeviceShutdown = (11, "FireWatch.Sensor.WatchedDeviceShutdown")
    WatcherDetected = (12, "FireWatch.Sensor.WatcherDetected")
    WatcherLeftRoom = (13, "FireWatch.Sensor.WatcherLeftRoom")
    OccupantDetected = (14, "FireWatch.Sensor.OccupantDetected")
    OccupantLeftRoom = (15, "FireWatch.Sensor.OccupantLeftRoom")

    # Controller events 20-29
    TimelimitExceeded = (20, "FireWatch.Controller.TimelimitExceeded")
    CuttingPowerToDevice = (21, "FireWatch.Controller.CuttingPowerToDevice")
    TurningOnWarningLight = (22, "FireWatch.Controller.TurningOnWarningLight")





class HeucodEventJsonEncoder(json.JSONEncoder):
    def default(self, obj):  # pylint: disable=E0202
        def to_camel(key):
            # Convert the attribtues names from snake case (Python "default") to camel case.
            return "".join([key.split("_")[0].lower(), *map(str.title, key.split("_")[1:])])

        if isinstance(obj, HeucodEvent):
            result = deepcopy(obj.__dict__)
            keys_append = {}
            keys_remove = set()
            camel_name = {}

            for k, v in result.items():
                # Check if the name must be changed to camel case
                first, *others = k.split("_")

                if first != "id" and len(others) > 0 and v is not None:
                    camel_name[k] = to_camel(k)
                    keys_remove.add(k)

                # Remove value if it is None
                if v is None:
                    keys_remove.add(k)
                # Change the attribute "id_" to "id"
                elif k == "id_":
                    keys_append["id"] = str(v) if not isinstance(v, str) else v
                    keys_remove.add(k)
                elif isinstance(v, UUID):
                    result[k] = str(v)
                elif isinstance(v, datetime):
                    result[k] = int(v.timestamp())
                elif isinstance(v, HeucodEventType):
                    result[k] = str(v)

            for k, v in camel_name.items():
                result[v] = result[k]
            for k in keys_remove:
                result.pop(k)
            for k, v in keys_append.items():
                result[k] = v
        # Attributes to ignore
        elif isinstance(obj, HeucodEventJsonEncoder):
            pass
        else:
            # Base class default() raises TypeError:
            return json.JSONEncoder.default(self, obj)

        return result


@dataclass
class HeucodEvent:
    # --------------------  General event properties --------------------
    # The unique ID of the event. Usually a GUID or UUID but one is free to choose.
    id_: Union[UUID, str] = None
    # The type of the event. This should preferably match the name of the "class" of the device
    # following the HEUCOD ontology in enumeration HeucodEventType.
    event_type: str = None
    # The type of the event as an integer. This should prefaribly match the name of the "class" of
    # the device following the HEUCOD ontology in enumeration HeucodEventType.
    event_type_enum: int = None
    # This field supports adding a prose description of the event - which can e.g. by used for
    # audit and logging purposes.
    description: str = None
    # This field can contain advanced or composite values which are well-known to the specialized
    # vendors.
    advanced: str = None
    # The timestamp of the event being created in the UNIX Epoch time format.
    timestamp: int = None
    # Start of the observed event.
    start_time: int = None
    # End of the observerd event.
    end_time: int = None
    # The length of the event period - in milliseconds. For example, if a PIR sensor has detected
    # movement and it covers 90 seconds, it would be 90000 ms.
    length: int = None
    # For how long is the sensor blind, in seconds. forexample, a PIR sensor will detect movement
    # and then send it. After this, it will be "blind" typically between 10 and 120 seconds. This is
    # important for the classification services.
    sensor_blind_duration: int = None
    # The primary value (as a long). If the value is not a number, use the description field instead.
    value: Any = None
    # The unit of the device. The unit can be a simple unit of the SI system, e.g. meters, seconds,
    # grams, or it could be a custom unit.
    unit: str = None
    # The secondary value. If there are more than 3 values, use the advanced field to add data.
    value2: Any = None
    # The unit of the second value from the device. The unit can be a simple unit of the SI system,
    # e.g. meters, seconds, grams, or it could be a custom unit.
    unit2: str = None
    # The tertariy value. If there are more than 3 values, use the advanced field to add data.
    value3: Any = None
    # The unit of the third value from the device. The unit can be a simple unit of the SI system,
    # e.g. meters, seconds, grams, or it could be a custom unit.
    unit3: str = None
    # Is this a direct event? This mean there is no gateway involved.
    direct_event: bool = None
    sending_delay: int = None
    advanced: str = None
    # -------------------- Patient details --------------------
    # ID of the user or patient to whom this event belongs.
    patient_id: str = None
    # ID of the caregiver - e.g. one helping with a rehab or care task that is reported.
    caregiver_id: int = None
    # The ID that can be used to monitor events of this person.
    monitor_id: str = None
    # Location can be an addres or apartment ID.
    location: str = None
    street_adress: str = None
    city: str = None
    postal_code: str = None
    # Could be the name or identifier of the care facility or care organization.
    site: str = None
    # Name of the room where the event occured (if any).
    room: str = None
    # -------------------- Sensor details --------------------
    # All sensors should have a unique ID which they continue to use to identify themselves.
    sensor_id: str = None
    # The type of sensor used.
    sensor_type: str = None
    sensor_location: str = None
    sensor_rtc_clock: bool = None
    # The model of the device.
    device_model: str = None
    # The vendor of the device.
    device_vendor: str = None
    # The ID of a gatway who is either relaying the event from a sensor or if the event is generated
    # by the gateway itself.
    gateway_id: str = None
    # The ID of the service generating the event. A service can be a sensor monitoring service, or
    # it could be a higher level service - interpreting data from one or more sensors and even from
    # several sensors, and maybe historical data.
    service_id: str = None
    # The average power consumption of the device in watts. Use together with the length attribute
    # to calcualte the value in kWh (kilowatt/hour).
    power: int = None
    # The battery level in percentage (0-100). A battery alert service may use this information to
    # send alerts at 10% or 20 % battery life - and critical alerts at 0%.
    battery: int = None
    # Sensor RSSI (Received Signal Strength Indicator). It is often used with radio based networks,
    # including WiFi, BLE, Zigbee and Lora.
    rssi: float = None
    # Measured Power indicates what’s the expected RSSI at a distance of 1 meter to the beacon.
    # Combined with RSSI, it allows to estimate the distance between the device and the beacon.
    measured_power: float = None
    # Signal-to-noise ratio(abbreviated SNR or S/N) is a measure used in science and engineering
    # that compares the level of a desired signal to the level of background noise.SNR is defined as
    # the ratio of signal power to the noise power, often expressed in decibels.
    signal_to_noise_ratio: float = None
    # The self-reproted accuracy of the sensor or service event. For example, a sensor may be 99%
    # sure that it has detected a fall, while a classification service may be 88% sure.
    accuracy: int = None
    # Link Quality (LQ) is the quality of the real data received in a signal. This is a value from 0
    # to 255, being 255 the best quality. Typically expect from 0 (bad) to 50-90 (good). It is
    # related to RSSI and SNR values as a quality indicator.
    link_quality: float = None
    # -------------------- Python class specific attributes --------------------
    json_encoder = HeucodEventJsonEncoder

    @classmethod
    def from_json(cls, event: str) -> HeucodEvent:
        if not event:
            raise ValueError("The string can't be empty or None")

        try:
            json_obj = json.loads(event)
        except json.JSONDecodeError as ex:
            raise ex from None

        instance = cls()

        # Convert the names of the JSON attributes to snake case (from camel case).
        obj_dict = {}
        for k, v in json_obj.items():
            if k != "id":
                key_tokens = re.split("(?=[A-Z])", k)
                obj_dict["_".join([t.lower() for t in key_tokens])] = v
            else:
                # The id_ attribtues is an exception of the naming standard. In Python, id is a
                # reserved word and its use for naming variables/attribtues/... should be avoided.
                # Thus the name id_.
                obj_dict["id_"] = v

        instance = dataclass_replace(instance, **obj_dict)

        return instance

    def to_json(self):
        if not self.json_encoder:
            raise TypeError("A converter was not specified. Use the converter attribute to do so.")

        # The dumps function looks tries to serialize the JSON string based in the JSON encoder that
        # is passed in the second argument. In this case, it will be the class HeucodEventJsonEncoder,
        # that inherits json.JSONEncoder. It has only the default() function this is called by
        # dumps() when serializing the class.
        return json.dumps(self, cls=self.json_encoder)