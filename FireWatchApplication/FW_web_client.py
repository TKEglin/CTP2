import socket
import pickle
from typing import Dict
from time import time, sleep

from heucod import HeucodEvent
from heucod import HeucodEventType as HEvent
from FW_datatypes import MQTT_device, TCP_BUFFER_SIZE

class FW_TCP_client:
    def __init__(self, HOST: str, PORT: int):
        # Host address and port of Firewatch server
        self.HOST = HOST
        self.PORT = PORT

    def request_device_data(self, attempts: int = 0) -> Dict[int, MQTT_device]:
        """Returns a list of MQTT_devices"""

        print("Retrieving device data from server.")
        print(f" Host: {self.HOST}")
        print(f" Port: {self.PORT}\n")

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPsocket:
                TCPsocket.connect((self.HOST, self.PORT))

                TCPsocket.send(pickle.dumps("send_device_data:"))

                data = b''
                while True:
                    package = TCPsocket.recv(TCP_BUFFER_SIZE)
                    data += package
                    if(not package or len(package) < TCP_BUFFER_SIZE):
                        print("All data received.")
                        break
                
                device_rows = pickle.loads(data)
                devices = MQTT_device.fromSQL(device_rows)
                print("Getting data...")

        except Exception as ex:
            if (attempts < 15):
                print(f"    Retry {attempts+1}...")
                # Retrying recursively
                # Increasing wait time for each attempt in case of server overload.
                sleep(0.1*attempts)
                devices = self.request_device_data(attempts + 1)
            else:
                print("Failed to retrieve device data. Ensure that web server is running and try again.")
                print("\tException: " + str(ex))
                return None
        
        return devices
    
    
    def send_unwatched_timestamp(self, timestamp: int):
        """Sends the timestamp to the server. A value of -1 indicates no unwatched devices."""

        print(f"Sending unwatched timestamp '{timestamp}' to server.")

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPsocket:
                TCPsocket.connect((self.HOST, self.PORT))

                TCPsocket.send(pickle.dumps(f"longest_unwatched_timestamp:{timestamp}"))
        except:
            print("Failed to send timestamp. Ensure that web server is running and try again.")


    def send_event(self, HEvent: HEvent, room: str = None):
        
        event = HeucodEvent(event_type      = HEvent,
                            event_type_enum = HEvent.value,
                            location        = room,
                            timestamp       = time())
        
        console_message = f"  Sending '{HEvent.name}' event"
        if(room): 
            console_message += f" with location '{room}'"
        console_message += f" to server."
        print(console_message)

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPsocket:
                TCPsocket.connect((self.HOST, self.PORT))

                TCPsocket.send(pickle.dumps(event))
        except BaseException as ex:
            print("Failed to send event. Exception: " + str(ex))

