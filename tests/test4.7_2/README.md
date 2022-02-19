# Tested usecase - WILDCARD '+'

## Mandatory normative statements

### MQTT-4.7.1-3

The single-level wildcard can be used at any level in the Topic Filter,
including first and last levels. Where it is used it MUST occupy an entire level
of the filter

| Time      | |
| ---       | --- |
| 0         | S1,S2,P connect |
|           | S1 subscribe house/room1/main-light q0, house/garage q0,
|           | house/room1/side-light q0, house/room2/main-light q0,
|           | house/room2/side-light q0, house q0
|           | S2 subscribe house/+/main-light q0
|           | P publish house/room1/main-light q0 'on',
|           | P publish house/room2/main-light q0 'on',
|           | P publish house/room1/side-light q0 'on',
|           | P publish house/room2/side-light q0 'on',
|           | P publish house/house/garage q0 'on',
|           | P publish house q0 'on'
| 5         | P publish house/room1/main-light q0 'off',
|           | P publish house/room2/main-light q0 'off',
|           | P publish house/room1/side-light q0 'off',
|           | P publish house/room2/side-light q0 'off',
|           | P publish house/house/garage q0 'off',
|           | P publish house q0 'off'
| 10        | P publish ... 'on'
| ...       | ...
