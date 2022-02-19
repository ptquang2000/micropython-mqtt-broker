# Tested usecase - RETAIN MESSAGE

## Mandatory normative statements

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

|Time   | Actions
|:--:   | :--
|0      | S1,S2,S3,S4,P connect
|       | S1 subscribe house/garage
|1      | P publish r1 house/garage 'temp'
|3      | P publish r1 house/garage 'on'
|5      | S2 subscribe house/garage
|6      | P publish house/garage, house/room 'off'
|8      | S3 subscribe house/garage, house/room
|9      | P publish house/garage, house/room ''
|10     | S4 subscribe house/garage, house/room
