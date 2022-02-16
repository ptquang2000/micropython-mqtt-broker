# Tested usecase - Publish QoS 1, Qos2

### MQTT-2.3.1-1
SUBSCRIBE, UNSUBSCRIBE, and PUBLISH (in cases where QoS > 0) Control Packets 
MUST contain a non-zero 16-bit Packet Identifier. 
### MQTT-2.3.1-2
Each time a Client sends a new packet of one of these types it MUST assign it a 
currently unused Packet Identifier [].
### MQTT-2.3.1-3
If a Client re-sends a particular Control 
Packet, then it MUST use the same Packet Identifier in subsequent re-sends of 
that packet. The Packet Identifier becomes available for reuse after the Client 
has processed the corresponding acknowledgement packet. In the case of a QoS 1 
PUBLISH this is the corresponding PUBACK; in the case of QoS 2 it is PUBCOMP. 
For SUBSCRIBE or UNSUBSCRIBE it is the corresponding SUBACK or UNSUBACK. 
### MQTT-2.3.1-4
The same conditions apply to a Server when it sends a PUBLISH with QoS > 0.
### MQTT-2.3.1-5
A PUBLISH Packet MUST NOT contain a Packet Identifier if its QoS value is set to 0.
### MQTT-2.3.1-6
A PUBACK, PUBREC or PUBREL Packet MUST contain the same Packet Identifier as the 
PUBLISH Packet that was originally sent. Similarly SUBACK and UNSUBACK MUST 
contain the Packet Identifier that was used in the corresponding SUBSCRIBE and 
UNSUBSCRIBE Packet respectively


| Time  ||
| --    | -- 
| 0     | S1,S2,S3,P1,P2 connect
|       | S1 subscribe home/room q0
|       | S2 subscribe home/room q1
|       | S3 subscribe home/room q2
| 2     | P1 publish home/room q1
|       | P2 publish home/room q2
| 5     | S1,S2,S3,P1,P2 disconnect