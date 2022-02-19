# Tested usecase - SUBACK

## Mandatory normative statements

### MQTT-3.9.3-1

The order of return codes in the SUBACK Packet MUST match the order of Topic Filters in the SUBSCRIBE Packet

### MQTT-3.9.3-2

SUBACK return codes other than 0x00, 0x01, 0x02 and 0x80 are reserved and MUST NOT be used

| Time  | |
| ---   | --- |
| 0     | client connect
|       | client subscribe
|       | sport/tennis/player1 q0
|       | sport/tennis/player1/ranking q1
|       | sport/tennis/player1/score/wimbledon q2
|       | sport/# q0
|       | # q1
|       | sport/tennis/# q2
|       | sport/tennis# q0
|       | sport/tennis/#/ranking q1
|       | + q2
|       | +/tennis/# q0
|       | sport+ q1
|       | sport/+/player1 q2
|       | /finance q0
|       | finance/ q1
|       | /finance/ q2
|       | / q0
|       | +/+ q1
|       | /+ q2
|       | +/ q0
|       | /+/ q1
|       |   q2
