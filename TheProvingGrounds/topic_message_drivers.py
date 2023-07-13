import paho.mqtt.client as mqtt


def SendOccupancyEvent(room: str, id: str, state: str):
    MQTT_client = mqtt.Client()
    MQTT_client.connect("127.0.0.1", 1883)

    MQTT_client.publish(f"Zigbee2mqtt/{room}/{id}/", "{\"occupancy\": \"" + state + "\"}")

def SendPowerEvent(room: str, id: str, state: str):
    MQTT_client = mqtt.Client()
    MQTT_client.connect("127.0.0.1", 1883)

    MQTT_client.publish(f"Zigbee2mqtt/{room}/{id}/", "{\"power\": \"" + state + "\"}")


SendPowerEvent("Kitchen", "1", "110")
SendPowerEvent("Bedroom", "7", "0")

# SendOccupancyEvent("Kitchen"    , "2", "True")
# SendOccupancyEvent("Living Room", "4", "True")
# SendOccupancyEvent("Bathroom"   , "6", "True")
# SendOccupancyEvent("Bedroom"    , "9", "True")


SendOccupancyEvent("Kitchen"    , "2", "False")
SendOccupancyEvent("Living Room", "4", "False")
SendOccupancyEvent("Bathroom"   , "6", "True")
SendOccupancyEvent("Bedroom"    , "9", "True")




# <?php 
# if ($roomdata->num_rows > 0) {
#     while($room = $roomdata->fetch_assoc()) {
#         echo "<tr>
#               <td style=\"color:", $room["statuscolor"], "\" class=\"tm-product-name\">", $room["name"], "</td>";
#         if($room["status"] === "None"){
#             echo "<td class=\"text-center\"></td>";
#         }
#         else{
#             echo "<td style=\"color:", $room["statuscolor"], "\" class=\"text-center\">", $room["status"], "</td>";
#         }
#         echo "</tr>";
#     }
# } 
# ?> 