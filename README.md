# CTP2

## Runnning the server
  1. Make sure that all required python packages are installed.
  2. Navigate to the `FireWatchWebsite/server/` folder
  3. Run the file `FW_TCP_server.py` in the terminal. No parameters are required

## Running the controller
  1. Make sure that all required python packages are installed.
  2. Navigate to the FireWatchApplication folder
  3. Run the file `FW_main.py` in the terminal with parameters `{FireWatch Server IP} {MQTT Server IP}` using the server IP printed to the console when you ran `FW_TCP_server.py` and the IP of your MQTT server. Example: `python3 FW_main.py 192.168.0.60 192.168.0.104`

## Running the website
The website was tested using Microsoft's WAMP.net, that is, Apache HTTP server, MySQL database, and the PHP programming language running on Windows OS. Both MySQL and PHP are required, but it should be possible to run the website using different operating systems and HTTP servers. 
  1. Ensure that Apache, MySQL and PHP interpreter are running.
  2. Ensure that the website is setup with document root `\CTP2\FireWatchWebsite`.
  3. Make sure to run the Firewatch server at least once, as this will initialize the database.
  4. Navigate to `{server IP address}/pages/login.php` in any web browser. This will take you to the login page.
  5. Login using the default username and password (`admin`, `admin`).
You will now have access to the system dashboard. You can click `Manage System` to access the device management system.

## Note on device friendly names
The present iteration of the system does not have automatic registration of Zigbee devices. This means that the system cannot automatically adjust friendly names and set up the correct MQTT publishing topics. For the system to work, the friendly name of each device in the Zigbee2MQTT system must have the format `{Device Name}/{Device ID}`, where the Device name and ID are the ones displayed in the `Manage System` page on the Firewatch website.
