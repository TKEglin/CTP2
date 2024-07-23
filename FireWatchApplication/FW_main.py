from FW_web_client import FW_TCP_client
from FW_controller import FW_controller
import sys
from threading import Thread
from heucod import HeucodEventType as HEvent

class Main:
    def start_controller(TCP_HOST: str, TCP_PORT: int, 
                         MQTT_HOST: str, MQTT_PORT: int,
                         restart: bool):
        
        client = FW_TCP_client(TCP_HOST, TCP_PORT)
        controller = FW_controller(client, MQTT_HOST, MQTT_PORT)
        
        exit_value = controller.run_controller(restart)
        if(exit_value == 1):
            print("\n !!Time limit exceeded, controller shut down!!")
            
        print("Input 'restart' to restart the controller"  )


    def run_firewatch():
        TCP_HOST = str(sys.argv[1]) # Web server IP
        TCP_PORT = 2001
        MQTT_HOST = str(sys.argv[2]) # MQTT server IP
        MQTT_PORT = 1883
        
        client = FW_TCP_client(TCP_HOST, TCP_PORT)
        
        print("Initializing Firewatch controller...")

        # Starting controller
        controller_thread = Thread(target=Main.start_controller, 
                                    args=(TCP_HOST, TCP_PORT, 
                                          MQTT_HOST, MQTT_PORT,
                                          False), 
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
                
            if(user_input in ('restart', 'RESTART')):  
                if(not controller_thread.is_alive()):
                    print("\nRestarting controller thread...")
                    controller_thread = Thread(target=Main.start_controller, 
                                                args=(TCP_HOST, TCP_PORT, True), 
                                                daemon=True            )
                    controller_thread.start()
                    print("Controller thread restarted.")
                else:
                    print("Controller is still running.")
                    


if __name__ == '__main__':
    Main.run_firewatch()