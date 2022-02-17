# Tested usecase - UNSUBRIBE
### MQTT-3.10.4-1
The Topic Filters (whether they contain wildcards or not) supplied in an 
UNSUBSCRIBE packet MUST be compared character-by-character with the current 
set of Topic Filters held by the Server for the Client. If any filter matches 
exactly then its owning Subscription is deleted, otherwise no additional 
processing occurs
### MQTT-3.10.4-4
The Server MUST respond to an UNSUBSUBCRIBE request by sending an UNSUBACK packet. 
The UNSUBACK Packet MUST have the same Packet Identifier as the UNSUBSCRIBE 
Packet.
### MQTT-3.10.4-5
Even where no Topic Subscriptions are deleted, the Server MUST respond with an 
UNSUBACK
### MQTT-3.10.4-6
If a Server receives an UNSUBSCRIBE packet that contains multiple Topic Filters 
it MUST handle that packet as if it had received a sequence of multiple 
UNSUBSCRIBE packets, except that it sends just one UNSUBACK response

|Time   ||
|---    |---|
|0      |S1 connect|
|       |S1 subscribe house/room1/main-light, house/room1/side-light, house/garage|
|6      |S1 unsubscribe house|
|6      |S1 unsubscribe house/room1/side-light, house/garage|
|6      |S1 subsribe house/room1/side-light|
|6      |S1 unsubscribe house/room1/side-light, house/garage|