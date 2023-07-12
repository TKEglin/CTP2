import socket
import sys
from threading import Thread
from heucod import HeucodEvent
from heucod import HeucodEventType as HEvent
import mysql.connector
import pickle

# Used to handle status display
UnwatchedDevice = False

def run_server():
    hostname = socket.gethostname()
    HOST = socket.gethostbyname(hostname)
    PORT = 2001

    print( "Initializing server...")
    print(f"    Hostname: {hostname}")
    print(f"    Host:     {HOST}")
    print(f"    Port:     {PORT}")
    print( "  Connecting to socket...")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPsocket:
        TCPsocket.bind((HOST, PORT))
        TCPsocket.listen()
        print("  Connected to socket")
        print("Initialization complete.")
        print("Input 'exit' to terminate.")
        
        # Starting listener thread
        Thread(target=listener, 
               args=(TCPsocket,), 
               daemon=True       ).start()

        # Ready to process input
        while True:
            s = input()
            if(s in ('exit', 'EXIT')):
                print("Server shutting down")
                sys.exit(0)


def listener(TCPsocket: socket):
    print("\nListening...")
    while True:
        connection, address = TCPsocket.accept()
        print(f"Connected to client        ({address[0]}:{address[1]})")

        # Starting handler thread
        Thread(target=connection_handler, 
               args=(connection, address), 
               daemon=True                ).start()

def connection_handler(connection: socket.socket, address):
    message = pickle.loads(connection.recv(16384))
    
    database_connection = mysql.connector.connect(host     = "localhost",
                                                  database = "FireWatchData",
                                                  username = "root",
                                                  password = "grp4")
    

    cursor = database_connection.cursor()
    
    # Server communication format: 
    # "<message_purpose>:<data>"
    # Data can be left empty when not needed

    # Checking for requests
    if(isinstance(message, str)):
        message_components = message.split(":")
        match message_components[0]:
            case "send_device_data":
                query = (f"SELECT * FROM devicedata")
                cursor.execute(query)
                device_rows = cursor.fetchall()
                
                print(f"  Sending device data.")

                connection.send(pickle.dumps(device_rows))
            case "longest_unwatched_timestamp":
                timestamp = message_components[1]
                query = (f"UPDATE systemdata SET unwatchedtimestamp = \"{timestamp}\" LIMIT 1")
                cursor.execute(query)
                print(f"  Inserted timestamp into systemdata.")
    else:  
        # Else, message is event
        event: HeucodEvent
        event = message

        # Storing in database
        query = (f"INSERT INTO eventdata(Type, ID, Location, Timestamp) VALUES ( '{event.event_type}', '{event.event_type_enum}', '{event.location}', '{event.timestamp}')")
        cursor.execute(query)
        print(f"  Inserted event {event.event_type} from location {event.location}.")

        # Updating system status data
        status: str
        statuscolor: str
        status_changed = True
        match event.event_type_enum:
            case HEvent.SystemOff.value:
                status = "System not running"
                statuscolor = "gray"
            case (HEvent.SystemOn.value | 
                  HEvent.SystemRestart.value |
                  HEvent.NoDevicesInUse.value):
                status = "System running | No devices in use"
                statuscolor = "teal"
            case HEvent.AllDevicesWatched.value:
                status = "System running | All devices watched"
                statuscolor = "green"
            case HEvent.UnwatchedDevice.value:
                status = "System running | Device(s) unwatched"
                statuscolor = "orange"
            case HEvent.TimelimitExceeded.value:
                status = "Time Exceeded | Watched devices shut down"
                statuscolor = "red"
            case _:
                status_changed = False
            
        if(status_changed):
            query = (f"UPDATE systemdata SET status = \"{status}\", statuscolor = \"{statuscolor}\" LIMIT 1")
            cursor.execute(query)
            print(f"  Updated system status to \"{status}\".")

        database_connection.commit()

        cursor.close()


    # Closing connection
    connection.close()
    print(    f"  Disconnected from client ({address[0]}:{address[1]})")

    

if __name__ == '__main__':
    run_server()