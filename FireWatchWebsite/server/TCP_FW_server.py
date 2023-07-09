import socket
import sys
from threading import Thread
from heucod import HeucodEvent
from heucod import HeucodEventType as HEvent
import mysql.connector
import pickle


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

    # Checking for requests
    match message:
        case "send_device_data":
            query = (f"SELECT * FROM devicedata")
            cursor.execute(query)
            device_rows = cursor.fetchall()
            
            print(f"  Sending device data.")

            connection.send(pickle.dumps(device_rows))
        case _:
            # Else, message is event
            event: HeucodEvent
            event = message

            # Storing in database
            query = (f"INSERT INTO eventdata(Type, ID, Location, Timestamp) VALUES ( '{event.event_type}', '{event.event_type_enum}', '{event.sensor_location}', '{event.timestamp}')")
            cursor.execute(query)
            print(f"  Inserted event {event.event_type} from location {event.sensor_location}.")

            # Updating system status data
            status: str
            statuscolor: str
            status_changed = True
            match event.event_type_enum:
                case HEvent.SystemOn.value:
                    status = "System running | Stove not in use"
                    statuscolor = "teal"
                case HEvent.SystemOff.value:
                    status = "System not running"
                    statuscolor = "gray"
                case HEvent.WatchedDeviceActivated.value:
                    status = "System running | Stove in use"
                    statuscolor = "green"
                case HEvent.WatcherLeftRoom.value:
                    status = "System running | Stove unwatched"
                    statuscolor = "orange"
                case HEvent.TimelimitExceeded.value:
                    status = "System running | Unwatched stove shutdown"
                    statuscolor = "red"
                case _:
                    status_changed = False
                
            if(status_changed):
                cursor.execute("truncate systemdata")
                query = (f"INSERT INTO systemdata(status, statuscolor) VALUES ( '{status}', '{statuscolor}' )")
                cursor.execute(query)
                print(f"  Updated system status to \"{status}\".")

            database_connection.commit()

            cursor.close()


    # Closing connection
    connection.close()
    print(    f"  Disconnected from client ({address[0]}:{address[1]})")

    

if __name__ == '__main__':
    run_server()