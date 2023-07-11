import socket
import pickle
from typing import Dict
from heucod import HeucodEvent
from FW_datatypes import MQTT_device_type, MQTT_device

class FW_TCP_client:
    def __init__(self, HOST: str, PORT: int):
        # Host address and port of Firewatch server
        self.HOST = HOST
        self.PORT = PORT

    def request_device_data(self) -> Dict[int, MQTT_device]:
        """Returns a list of MQTT_devices"""

        print("Retrieving device data from server...")
        print(f" Host: {self.HOST}")
        print(f" Port: {self.PORT}\n")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPsocket:
            TCPsocket.connect((self.HOST, self.PORT))

            TCPsocket.send(pickle.dumps("send_device_data"))
            
            device_rows = pickle.loads(TCPsocket.recv(16384))

            devices = MQTT_device.fromSQL(device_rows)
            
        return devices

    def send_event(self, event: HeucodEvent):
        
        print(f"Sending {event.event_type.name} event with location {event.location} to server...")
        print(f" Host: {self.HOST}")
        print(f" Port: {self.PORT}\n")

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPsocket:
                TCPsocket.connect((self.HOST, self.PORT))

                TCPsocket.send(pickle.dumps(event))
        except:
            print("Failed to send event. Web server might be down.")

