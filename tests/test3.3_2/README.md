# Tested usecase - RETAIN MESSAGE

## Mandatory normative statements

### MQTT-3.3.1-12

If the RETAIN flag is 0, in a PUBLISH Packet sent by a Client to a Server, the
Server MUST NOT store the message and MUST NOT remove or replace any existing
retained message

|Time   | Actions
|:--:   | :--
|0      | S1,S2,P connect
|       | S1 subscribe house/room
|2      | P publish r1 house/room 'on'
|4      | P publish r0 house/room 'off'
|6      | S2 subscribe house/room
|8      | S1,S2,P disconnect
