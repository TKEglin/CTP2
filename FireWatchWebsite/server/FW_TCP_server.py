import socket
import sys
from threading import Thread
import mysql.connector
import pickle

from heucod import HeucodEvent
from heucod import HeucodEventType as HEvent
from FW_datatypes import MQTT_device_type


def run_server():
    hostname = socket.gethostname()
    HOST = socket.gethostbyname(hostname)
    PORT = 2001

    print( "Initializing server...")
    print(f"    Hostname: {hostname}")
    print(f"    Host:     {HOST}")
    print(f"    Port:     {PORT}")
    
    print( "  Initializing datebase...")
    initialize_database()
    
    print("  Resetting room data...")
    reset_room_data()
    
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

        # Starting handler thread
        # Thread(target=connection_handler, 
        #        args=(connection, address), 
        #        daemon=True                ).start()
        connection_handler(connection, address)

def connection_handler(connection: socket.socket, address):
    message = pickle.loads(connection.recv(16384))
    
    database_connection = mysql.connector.connect(host     = "localhost",
                                                  database = "FireWatchData",
                                                  username = "root",
                                                  password = "grp4")
    
                                     
    # # >  Server communication format: 
    # # >  "<message_purpose>:<data>"
    # # >  <data> can be left empty when not needed

    # Checking for messages
    if(isinstance(message, str)):
        message_components = message.split(":")
        match message_components[0]:
            case "send_device_data":
                cursor = database_connection.cursor()
                query = (f"SELECT * FROM devicedata")
                cursor.execute(query)
                device_rows = cursor.fetchall()
                database_connection.commit()
                
                print(f"  Sending device data.")
                connection.send(pickle.dumps(device_rows))
            case "longest_unwatched_timestamp":
                cursor = database_connection.cursor()
                timestamp = int(message_components[1])
                update_db_timestamp(cursor, timestamp)
                database_connection.commit()
    else:  
        # Else, message is event
        event: HeucodEvent
        event = message

        # Storing in database
        cursor = database_connection.cursor()
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
                update_db_timestamp(cursor, -1)
                reset_room_data(database_connection, cursor)
            case (HEvent.SystemOn.value      | 
                  HEvent.SystemRestart.value):
                status = "System running | No devices in use"
                statuscolor = "teal"
                update_db_timestamp(cursor, -1)
                initialize_room_data(database_connection, cursor)
            case HEvent.NoDevicesInUse.value:
                status = "System running | No devices in use"
                statuscolor = "teal"
                update_db_timestamp(cursor, -1)
            case HEvent.AllDevicesWatched.value:
                status = "System running | All devices watched"
                statuscolor = "green"
                update_db_timestamp(cursor, -1)
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
            
        
        # Updating room status data if event has location
        if(event.location):
            cursor.execute(f"SELECT * FROM roomdata WHERE name = '{event.location}'")
            roomdata = cursor.fetchall()[0]
            db_status      : str = roomdata[2]
            devices_in_use : int = roomdata[4]
            
            status_changed = True
            match event.event_type_enum:
                case HEvent.WatchedDeviceActivated.value:
                    query = (f"UPDATE roomdata SET `devicesinuse` = {devices_in_use + 1} WHERE name = '{event.location}'")
                    cursor.execute(query)
                    database_connection.commit()
                    if(db_status == "Occupied"):
                        status = "Watched Device"
                        statuscolor = "green"
                    else:
                        status = "Unwatched Device"
                        statuscolor = "orange"
                case HEvent.WatchedDeviceShutdown.value:
                    query = (f"UPDATE roomdata SET `devicesinuse` = {devices_in_use - 1} WHERE name = '{event.location}'")
                    cursor.execute(query)
                    database_connection.commit()
                    if(devices_in_use - 1 == 0): # If last device:
                        if(db_status == "Watched Device"):
                            status = "Occupied"
                            statuscolor = "teal"
                        else:
                            status = "Not occupied"
                            statuscolor = "gray"
                    else:
                        status_changed = False
                        
                case HEvent.WatcherDetected.value:
                    if(devices_in_use and devices_in_use > 0):
                        status = "Watched Device"
                        statuscolor = "green"
                    else:
                        status = "Occupied"
                        statuscolor = "teal"
                case HEvent.WatcherLeftRoom.value:
                    if(devices_in_use and devices_in_use > 0):
                        status = "Unwatched Device"
                        statuscolor = "orange"
                    else:
                        status = "Not occupied"
                        statuscolor = "gray"
                        
                case HEvent.OccupantDetected.value:
                    status = "Occupied"
                    statuscolor = "teal"
                case HEvent.OccupantLeftRoom.value:
                    status = "Not occupied"
                    statuscolor = "gray"
                    
                case HEvent.CuttingPowerToDevice.value:
                    status = "Shutdown"
                    statuscolor = "red"
                    
                case _:
                    status_changed = False
                    
            if(status_changed):    
                print(f"Adding status '{status}' to roomdata of room {event.location}.")
                query = (f"UPDATE roomdata SET status = '{status}', statuscolor = '{statuscolor}' WHERE name = '{event.location}'")   
                cursor.execute(query)

        database_connection.commit()

    cursor.close()

    # Closing connection
    connection.close()


def update_db_timestamp(cursor, timestamp: int):
    """Adds the timestamp to the unwatchedtimestamp field of the systemdata table"""
    query = (f"UPDATE systemdata SET unwatchedtimestamp = \"{timestamp}\" LIMIT 1")
    cursor.execute(query)
    print(f"  Inserted timestamp '{timestamp}' into systemdata.")
       
        
def initialize_room_data(db_connection, cursor):
    """Sets all status fields to 'Not occupied' and all statuscolor fields to null"""
    reset_room_data(db_connection = db_connection, cursor = cursor, status="Not Occupied")
    
    
def reset_room_data(db_connection = None, cursor = None, status = None):
    """Sets all status and statuscolor fields in roomdata to null"""
    if(not db_connection):
        db_connection = mysql.connector.connect(host     = "localhost",
                                                database = "FireWatchData",
                                                username = "root",
                                                password = "grp4")
    if(not cursor):
        cursor = db_connection.cursor()
        
    statuscolor = "gray"
    query = (f"UPDATE roomdata SET status = '{status}', statuscolor = '{statuscolor}', devicesinuse = 0")
    cursor.execute(query)
    print("  Room data reset.")
    
    db_connection.commit()

    

        
        
def initialize_database():
    db_connection = mysql.connector.connect(
        host = "127.0.0.1",
        user = "root",
        password = "grp4",
        database = "firewatchdata"
    )
    cursor = db_connection.cursor(buffered = True)
    
    # System data
    cursor.execute("CREATE TABLE IF NOT EXISTS systemdata (" +
                    "status VARCHAR(255) NOT NULL, " +
                    "statuscolor VARCHAR(255) NOT NULL, " +
                    "unwatchedtimestamp INT)")
    
    # If systemdata already has an entry, the database is initialized and function can return
    cursor.execute("SELECT * FROM systemdata LIMIT 1")
    systemdata_row = cursor.fetchall()
    if(systemdata_row):
        print("  Database was already initialized.")
        return
    # Else, continue initialization:
    
    #   Adding default systemdata
    cursor.execute("INSERT INTO systemdata " +
                    "(status, statuscolor, unwatchedtimestamp) " +
                    "VALUES " +
                    "('System not running', 'gray', -1)")
    
    # User data
    cursor.execute("CREATE TABLE IF NOT EXISTS userdata (" +
                    "username VARCHAR(255) NOT NULL, " +
                    "password VARCHAR(255) NOT NULL)")
    #   Adding default userdata
    cursor.execute("INSERT INTO userdata " +
                    "(username, password) " +
                    "VALUES " +
                    "('admin', 'admin')")
        
    # Event data
    cursor.execute("CREATE TABLE IF NOT EXISTS eventdata (" +
                    "ID INT NOT NULL, " +
                    "Type VARCHAR(255) NOT NULL, " +
                    "Location VARCHAR(255) NOT NULL, " +
                    "Timestamp INT NOT NULL)")
    
    # Device data
    cursor.execute("CREATE TABLE IF NOT EXISTS devicedata (" +
                    "uid INT AUTO_INCREMENT PRIMARY KEY, " +
                    "name VARCHAR(255) NOT NULL, " +
                    "type VARCHAR(255) NOT NULL, " +
                    "room VARCHAR(255) NOT NULL, " +
                    "device_JSON TEXT NOT NULL)")
    # Room data
    cursor.execute("CREATE TABLE IF NOT EXISTS roomdata (" +
                    "uid INT AUTO_INCREMENT PRIMARY KEY, " +
                    "name VARCHAR(255) NOT NULL, " +
                    "status VARCHAR(255)," +
                    "statuscolor VARCHAR(255) DEFAULT 'gray'," +
                    "devicesinuse INT NOT NULL DEFAULT 0," +
                    "UNIQUE (name))")
    
    # Supported devices
    cursor.execute("CREATE TABLE IF NOT EXISTS supporteddevices (" +
                    "uid INT AUTO_INCREMENT PRIMARY KEY, " +
                    "name VARCHAR(255) NOT NULL, " +
                    "`function` VARCHAR(255) NOT NULL, " +
                    "device_JSON TEXT NOT NULL)")
    #   Adding supported devices
    #       Immax NEO 07048L
    device_JSON = MQTT_device_type(
                    brand_name          = "Immax NEO 07048L power unit",
                    general_topic       = "Zigbee2mqtt",
                    device_function     = "Power Plug",
                    actuator_topic      = "set",
                    actuator_value_name = "state",
                    actuator_enable     = "ON",
                    actuator_disable    = "OFF",
                    sensor_topic        = "",
                    sensor_value_name   = "power",
                    sensor_threshold    = 10 # In_use/not in_use threshold
                    ).toJSON()
    cursor.execute("INSERT INTO supporteddevices " +
                    "(name, `function`, device_JSON) " +
                    "VALUES " +
                    "('Immax NEO 07048L', 'Power Plug', '" + device_JSON + "')")
    #       GLEDOPTO GL-MC-001PK
    device_JSON = MQTT_device_type(
                    brand_name          = "GLEDOPTO GL-MC-001PK",
                    general_topic       = "Zigbee2mqtt",
                    device_function     = "Warning Device",
                    actuator_topic      = "set",
                    actuator_value_name = "state",
                    actuator_enable     = "ON",
                    actuator_disable    = "OFF",
                ).toJSON()
    cursor.execute("INSERT INTO supporteddevices " +
                    "(name, `function`, device_JSON) " +
                    "VALUES " +
                    "('GLEDOPTO GL-MC-001PK', 'Warning Device', '" + device_JSON + "')")
    
    #       IKEA_E1525_E1745
    device_JSON = MQTT_device_type(
                    brand_name        = "IKEA E1525/E1745",
                    general_topic     = "Zigbee2mqtt",
                    device_function   = "Presence Sensor",
                    sensor_topic      = "",
                    sensor_value_name = "occupancy",
                ).toJSON()
    cursor.execute("INSERT INTO supporteddevices " +
                    "(name, `function`, device_JSON) " +
                    "VALUES " +
                    "('IKEA_E1525_E1745', 'Presence Sensor', '" + device_JSON + "')")
    db_connection.commit()

    print("  Database initialized.")
    
    
    
if __name__ == '__main__':
    run_server()