
import mysql.connector


db_connection = mysql.connector.connect(
    host = "127.0.0.1",
    user = "root",
    password = "grp4",
    database = "firewatchdata"
)
cursor = db_connection.cursor(buffered = True)

cursor.execute("CREATE TABLE IF NOT EXISTS tesdata (" +
                "uid INT AUTO_INCREMENT PRIMARY KEY, " +
                "name VARCHAR(255) NOT NULL, " +
                "status VARCHAR(255)," +
                "statuscolor VARCHAR(255) DEFAULT 'gray'," +
                "devicesinuse INT NOT NULL DEFAULT 0," +
                "UNIQUE (name))")

db_connection.commit()