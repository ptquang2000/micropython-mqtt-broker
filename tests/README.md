# Tested usecase

## CONNECT

### MQTT-3.1.2-24 
If the Keep Alive value is non-zero and the Server does not receive a Control 
Packet from the Client within one and a half times the Keep Alive time period, 
it MUST disconnect the Network Connection to the Client as if the network had 
failed
### MQTT-3.1.4-2
If the ClientId represents a Client already connected to the Server then the 
Server MUST disconnect the existing Client


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
### MQTT-4.7.1-2
The multi-level wildcard character MUST be specified either on its own or 
following a topic level separator. In either case it MUST be the last character 
specified in the Topic Filter 
### MQTT-4.7.1-3
The single-level wildcard can be used at any level in the Topic Filter, 
including first and last levels. Where it is used it MUST occupy an entire level 
of the filter


## UNSUBRIBE
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
