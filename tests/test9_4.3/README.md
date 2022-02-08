# Tested usecase - Publish QoS 1, Qos2

### MQTT-4.3.2-2
In the QoS 1 delivery protocol, the Receiver
* MUST respond with a PUBACK Packet containing the Packet Identifier from the 
incoming PUBLISH Packet, having accepted ownership of the Application Message
* After it has sent a PUBACK Packet the Receiver MUST treat any incoming 
PUBLISH packet that contains the same Packet Identifier as being a new 
publication, irrespective of the setting of its DUP flag.


| Time  ||
| --    | -- 
| 0     | S1,S2,S3,P1,P2 connect
|       | S1 subscribe home/room q0
|       | S2 subscribe home/room q1
|       | S3 subscribe home/room q2
| 2     | P1 publish home/room q1
|       | P2 publish home/room q2
| 5     | S1,S2,S3,P1,P2 disconnect