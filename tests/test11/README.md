# Tested usecase - RETAIN MESSAGE WITH WILDCARD SUBSCRIBERS

|Time   | Actions
|:--:   | :--
|0      | S1,S2,S3,S4,P connect
|1      | P publish r1 house/garage/main-light 'gargage'
|       | P publish r1 house/room/main-light 'room-main'
|       | P publish r1 house/room/side-light 'room-side'
|       | P publish r1 house/room 'room'
|       | P publish r1 house 'house'
|4      | S1 subscribe house/#
|       | S2 subscribe house/+/main-light
|       | S3 subscribe house/room/+
|       | S4 subscribe house/room/#
| 10    | S1,S2,S3,S4,P disconnect