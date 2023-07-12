from FW_web_client import FW_TCP_client
from FW_controller import FW_controller
import sys
from threading import Thread
from heucod import HeucodEventType as HEvent


def start_controller(HOST:str, PORT: str, restart: bool):
    
    client = FW_TCP_client(HOST, PORT)
    controller = FW_controller(client)
    
    exit_value = controller.run_controller(restart)
    if(exit_value == 1):
        print("\n !!Time limit exceeded, controller shut down!!")
        
    print("Input 'restart' to restart the controller"  )


def run_firewatch():
    HOST = str(sys.argv[1]) # Web server IP
    PORT = 2001
    
    client = FW_TCP_client(HOST, PORT)
    
    print("Initializing Firewatch controller...")

    # Starting controller
    controller_thread = Thread(target=start_controller, 
                                args=(HOST, PORT, False), 
                                daemon=True)
    controller_thread.start()
    print("  Controller thread started.")

    print("Firewatch controller initialized and running.")
    print("Input 'exit' to shut down the system.\n")

    # Ready to process input
    while True:
        user_input = input()
        if(user_input in ('exit', 'EXIT')):
            client.send_event(HEvent.SystemOff)
            print("\nFirewatch shutting down")
            sys.exit(0)
            
        if(user_input in ('restart', 'RESTART') and not controller_thread.is_alive()):  
            print("\nRestarting controller thread...")
            controller_thread = Thread(target=start_controller, 
                                        args=(HOST, PORT, True), 
                                        daemon=True            )
            controller_thread.start()
            print("Controller thread restarted.")
                    


if __name__ == '__main__':
    run_firewatch()