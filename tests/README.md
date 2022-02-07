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

## PUBLISH
### MQTT-3.3.1-5
If the RETAIN flag is set to 1, in a PUBLISH Packet sent by a Client to a Server, 
the Server MUST store the Application Message and its QoS, so that it can be 
delivered to future subscribers whose subscriptions match its topic name 
### MQTT-3.3.1-6
When a new subscription is established, the last retained message, if any, on 
each matching topic name MUST be sent to the subscriber
### MQTT-3.3.1-7
If the Server receives a QoS 0 message with the RETAIN flag set to 1 it MUST 
discard any message previously retained for that topic. It SHOULD store the new 
QoS 0 message as the new retained message for that topic, but MAY choose to 
discard it at any time - if this happens there will be no retained message for 
that topic
### MQTT-3.3.1-8
When sending a PUBLISH Packet to a Client the Server MUST set the RETAIN flag to 
1 if a message is sent as a result of a new subscription being made by a Client
### MQTT-3.3.1-9
It MUST set the RETAIN flag to 0 when a PUBLISH Packet is sent to a Client 
because it matches an established subscription regardless of how the flag was set 
in the message it received
### MQTT-3.3.1-10
A PUBLISH Packet with a RETAIN flag set to 1 and a payload containing zero bytes 
will be processed as normal by the Server and sent to Clients with a subscription 
matching the topic name. Additionally any existing retained message with the same 
topic name MUST be removed and any future subscribers for the topic will not 
receive a retained message
### MQTT-3.3.1-11
A zero byte retained message MUST NOT be stored as a retained message on the 
Server