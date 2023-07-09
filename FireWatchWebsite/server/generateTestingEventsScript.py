
import mysql.connector
from heucod import HeucodEvent
from datetime import datetime, timezone

event = HeucodEvent()

event.event_type = "Testing Event Type of Significant Length"
event.sensor_location = "Somewhere on Earth"
event.timestamp = datetime.now().timestamp()
print(event.timestamp)

for i in range(0, 4):  
    try:
        connection = mysql.connector.connect(host = "localhost",
                                             database = "FireWatchData",
                                             username = "root",
                                             password = "grp4")

        
        # Storing in database
        mysql_insert_query = (f"INSERT INTO eventdata(Type, ID, Location, Timestamp) VALUES ( '{event.event_type}', '{i}', '{event.sensor_location}', '{event.timestamp}')")

        cursor = connection.cursor()
        cursor.execute(mysql_insert_query)
        connection.commit()

        print(cursor.rowcount, "Inserted successfully into the tables")
        
        cursor.close()

    except mysql.connector.Error as error:
        print("Failed to insert record {}".format(error))