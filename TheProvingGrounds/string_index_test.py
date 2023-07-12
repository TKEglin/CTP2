from heucod import HeucodEvent

message1 = "send_device_data:"
message2 = "unwa_stamp:1111111111"

print(message1.split(":")[0])
print(message2.split(":")[1])

number = 1

event = HeucodEvent()

print(isinstance(event, str))