# Tested usecase - Save sessions, retain topic to db

main.py is used to start server

| Time    | |
| ---     | ---
| 0       | S1,S2,P1 connect clean_session=False
|         | S1 subscribe house/gargage q0, house/room/main-light q1, house/room/side-light q2 
|         | S2 subscribe house/room/main-light q1, house/room/side-light q2
|         | P1 publish house/gargage r1 q0 'on'
|         | P1 publish house/room/main-light r1 q1 'on'
|         | P1 publish house/room/side-light r1 q2 'on'
|         | P1 exit   
|         | S1,S2 disconnect
| 2*      | Server Close
|         | Server start
| 6       | S1,P1 connect clean_session=False
|         | S2 connect clean_session=True
| 8       | S2 subscribe house/gargage q2, house/room/main-light q0, house/room/side-light q1 
|         | P1 publish house/gargage r1 q2 'off'
|         | P1 publish house/room/main-light r1 q1 'off'
|         | P1 publish house/room/side-light r1 q0 'off'