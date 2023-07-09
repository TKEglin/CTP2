from FW_web_client import FW_TCP_client
from FW_controller import FW_controller
import sys
from threading import Thread
from heucod import HeucodEvent
from heucod import HeucodEventType as HEvent
import json
import time


def start_controller(client):
    FW_controller(client)


def run_firewatch():
    HOST = str(sys.argv[1]) # Server IP
    PORT = 2001

    client = FW_TCP_client(HOST, PORT)
    
    print("Initializing Firewatch controller...")

    # Starting controller
    print("  Starting controller thread...")
    Thread(target=start_controller, 
           args=(client,), 
           daemon=True             ).start()
    print("  Controller thread started.")

    print("Firewatch controller initialized and running.\n\n")

    # Ready to process input
    while True:
        s = input()
        if(s in ('exit', 'EXIT')):
            print("\nFirewatch shutting down")

            print("Sending SystemOff event")
            event = HeucodEvent()

            event.event_type = HEvent.SystemOff
            event.event_type_enum = HEvent.SystemOff.value
            event.location = " "
            event.timestamp = time.time()

            client.send_event(event)
            sys.exit(0)


if __name__ == '__main__':
    run_firewatch()