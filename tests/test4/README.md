# Tested usecase

## SUBSCRIRBE

### MQTT-3.8.4-1
When the Server receives a SUBSCRIBE Packet from a Client, the Server MUST 
respond with a SUBACK Packet
### MQTT-3.8.4-2
The SUBACK Packet MUST have the same Packet Identifier as the SUBSCRIBE 
Packet that it is acknowledging
### MQTT-3.8.4-4
If a Server receives a SUBSCRIBE packet that contains multiple Topic Filters it 
MUST handle that packet as if it had received a sequence of multiple SUBSCRIBE 
packets, except that it combines their responses into a single SUBACK response 