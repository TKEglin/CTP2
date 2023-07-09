import socket
import sys
from heucod import HeucodEvent
import pickle
import time

class FW_TCP_client:
    def __init__(self, HOST: str, PORT: int):
        # Host address and port of Firewatch server
        self.HOST = HOST
        self.PORT = PORT

    def request_device_data(self) -> list:

        print("Retrieving device data from server...")
        print(f" Host: {self.HOST}")
        print(f" Port: {self.PORT}\n")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPsocket:
            TCPsocket.connect((self.HOST, self.PORT))

            TCPsocket.send(pickle.dumps("send_device_data"))

            device_data = TCPsocket.recv(1024)
            
        return device_data

    def send_event(self, event: HeucodEvent):

        print("Sending event to server...")
        print(f" Host: {self.HOST}")
        print(f" Port: {self.PORT}\n")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPsocket:
            TCPsocket.connect((self.HOST, self.PORT))

            TCPsocket.send(pickle.dumps(event))

