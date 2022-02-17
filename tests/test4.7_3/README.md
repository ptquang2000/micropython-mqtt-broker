# Tested usecase - WILDCARD '+'

| Time      | |
| ---       | --- |
| 0         | S1,S2,S3,S4,S5,S6,S7,P connect |
|           | S1 subscribe sport/tennis/+
|           | S2 subscribe +/tennis/#
|           | S3 subscribe sport/+/player1
|           | S4 subscribe +/+
|           | S5 subscribe /+
|           | S6 subscribe +
|           | S7 subsribe sport/+
| 2         | P publish sport/tennis/player1 'player1'
|           | P publish sport/tennis/player2 'player2'
|           | P publish sport/tennis/player1/ranking 'ranking'
|           | P publish sport 'sport'
|           | P publish sport/ 'sport/'
|           | P publish /sport '/sport'
|           | P publish finance/tennis 'tennis'
