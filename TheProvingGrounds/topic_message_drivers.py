import paho.mqtt.client as mqtt


def SendOccupancyEvent(room: str, id: str, state: str):
    MQTT_client = mqtt.Client()
    MQTT_client.connect("127.0.0.1", 1883)

    MQTT_client.publish(f"Zigbee2mqtt/{room}/{id}/", "{\"occupancy\": \"" + state + "\"}")

def SendPowerEvent(room: str, id: str, state: str):
    MQTT_client = mqtt.Client()
    MQTT_client.connect("127.0.0.1", 1883)

    MQTT_client.publish(f"Zigbee2mqtt/{room}/{id}/", "{\"power\": \"" + state + "\"}")


SendPowerEvent("Kitchen", "1", "0")
SendPowerEvent("Kitchen", "14", "0")
SendPowerEvent("Basement", "11", "0")


SendOccupancyEvent("Kitchen"    , "2", "False")
SendOccupancyEvent("Living Room", "4", "False")
SendOccupancyEvent("Garage"     , "6", "True")
SendOccupancyEvent("Bedroom"    , "8", "False")
SendOccupancyEvent("Bathroom"   , "10", "True")
SendOccupancyEvent("Basement"   , "12", "False")








# <?php 
# if ($roomdata->num_rows > 0) {
#     while($room = $roomdata->fetch_assoc()) {
#         echo "
#             <div class=\"tm-table-mt tm-table-actions-row\">
#                 <div class=\"tm-table-actions-col-left\">
#                     <h3 style=\"color:", $room["statuscolor"], ";text-align:center\">", $room["name"], "</h3>
#                 </div>
#                 <div class=\"tm-table-actions-col-right\">";
#         if($room["status"] === "None"){
#             echo "<h3 style=\"color:", $room["statuscolor"], ";text-align:center\"></h3>";
#         }
#         else{
#             echo "<h3 style=\"color:", $room["statuscolor"], ";text-align:center\">", $room["status"], "</h3>";
#         }
#         echo "  </div>
#             </div>";
#     }
# } 
# ?>