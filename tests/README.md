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

