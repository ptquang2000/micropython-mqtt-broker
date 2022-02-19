# Tested usecase - WILDCARD '#'

## Mandatory normative statements

### MQTT-4.7.1-2

The multi-level wildcard character MUST be specified either on its own or
following a topic level separator. In either case it MUST be the last character
specified in the Topic Filter

| Time      | |
| ---       | --- |
| 0         | S1,S2,P connect |
|           | S1 subscribe house/room/main-light q0,
|           | house/room/side-light q0, house/main-door q0,
|           | house/garage/main-light q0, house q0
|           | S2 subscribe house/# q0
|           | P publish house/room/main-light q0 'on',
|           | P publish house/room/side-light q0 'on',
|           | P publish house/garage/main-light q0 'on',
|           | P publish house/main-door q0 'on',
|           | P publish house q0 'on'
| 2         | P publish house/room/main-light q0 'off',
|           | P publish house/room/side-light q0 'off',
|           | P publish house/garage/main-light q0 'off',
|           | P publish house/main-door q0 'off',
|           | P publish house q0 'off'
