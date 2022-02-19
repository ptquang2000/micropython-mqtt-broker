# Tested usecase - Clean Session, QoS Order

## Mandatory normative statements

### MQTT-3.1.2-4

If CleanSession is set to 0, the Server MUST resume communications with the
Client based on state from the current Session (as identified by the Client
identifier). If there is no Session associated with the Client identifier the
Server MUST create a new Session. The Client and Server MUST store the Session
after the Client and Server are disconnected

### MQTT-3.1.2-5

After the disconnection of a Session that had CleanSession set to 0, the Server
MUST store further QoS 1 and QoS 2 messages that match any subscriptions that
the client had at the time of disconnection as part of the Session state

### MQTT-4.3.3-1

In the QoS 2 delivery protocol, the Sender

* MUST assign an unused Packet Identifier when it has a new Application Message
to publish.
* MUST send a PUBLISH packet containing this Packet Identifier with QoS=2, DUP=0.
* MUST treat the PUBLISH packet as “unacknowledged” until it has received the
corresponding PUBREC packet from the receiver. See Section 4.4 for a discussion
of unacknowledged messages.
* MUST send a PUBREL packet when it receives a PUBREC packet from the receiver.
This PUBREL packet MUST contain the same Packet Identifier as the original PUBLISH packet.
* MUST treat the PUBREL packet as “unacknowledged” until it has received the
corresponding PUBCOMP packet from the receiver.
* MUST NOT re-send the PUBLISH once it has sent the corresponding PUBREL packet.

### MQTT-4.3.2-1

n the QoS 1 delivery protocol, the Sender

* MUST assign an unused Packet Identifier each time it has a new Application
Message to publish.
* MUST send a PUBLISH Packet containing this Packet Identifier with QoS=1, DUP=0.
* MUST treat the PUBLISH Packet as “unacknowledged” until it has received the
corresponding PUBACK packet from the receiver. See Section 4.4 for a discussion
of unacknowledged messages.

### MQTT-4.3.2-2

In the QoS 1 delivery protocol, the Receiver

* MUST respond with a PUBACK Packet containing the Packet Identifier from the
incoming PUBLISH Packet, having accepted ownership of the Application Message
* After it has sent a PUBACK Packet the Receiver MUST treat any incoming PUBLISH
packet that contains the same Packet Identifier as being a new publication,
irrespective of the setting of its DUP flag.

### MQTT-4.3.3-2

In the QoS 2 delivery protocol, the Receiver

* MUST respond with a PUBREC containing the Packet Identifier from the incoming
PUBLISH Packet, having accepted ownership of the Application Message.
* Until it has received the corresponding PUBREL packet, the Receiver MUST
acknowledge any subsequent PUBLISH packet with the same Packet Identifier by
sending a PUBREC. It MUST NOT cause duplicate messages to be delivered to any
onward recipients in this case.
* MUST respond to a PUBREL packet by sending a PUBCOMP packet containing the
same Packet Identifier as the PUBREL.
* After it has sent a PUBCOMP, the receiver MUST treat any subsequent PUBLISH
packet that contains that Packet Identifier as being a new publication.

### MQTT-4.4.0-1

When a Client reconnects with CleanSession set to 0, both the Client and Server
MUST re-send any unacknowledged PUBLISH Packets (where QoS > 0) and PUBREL
Packets using their original Packet Identifiers

| Time      | |
| ---       | ---
|           | S1,P1 connect
| 1         | S1 subscribe /house/room q0
|           | S1 subscribe /house/room/gargae q1
|           | S1 subscribe /house/room/main-light q2
| 10        | P1 publish /house/room q0 'on'
|           | P1 publish /house/gargage q1 'on'
|           | P1 publish /house/room/main-light q2 'on'
| 11        | P1 publish /house/room q0 'off'
|           | P1 publish /house/gargage q1 'off'
|           | exit P1 thread
|           | P1 reconnect
|           | P1 publish /house/room/main-light q2 'off'
| 12        | P1 publish /house/room q0 'off'
|           | P1 publish /house/gargage q1 'off'
|           | P1 publish /house/room/main-light q2 'off'
|           | P1 disconnect
|           | P1 reconnect
