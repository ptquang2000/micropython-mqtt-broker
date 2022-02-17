import sys
from paho.mqtt import client as mqtt_client


broker = sys.argv[1]

def on_subscribe(client, userdata, mid, granted_qos):
    print(f"mid:{mid}, qos:{granted_qos}")

def on_log(client, userdata, level, buf):
    print('log:', buf)


def on_connect(client, userdata, flags, rc):
    print("Connected")


def on_disconnect(client, userdata,  rc):
    print("Disconnected")


def connect():
    client_id = f'client'
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)
    client.on_log = on_log
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_disconnect = on_disconnect
    client.connect(broker, 1883)
    client.subscribe([
        ('sport/tennis/player1',0), ('sport/tennis/player1/ranking', 1),
        ('sport/tennis/player1/score/wimbledon', 2), ('sport/#',0), 
        ('#', 1), ('sport/tennis/#', 2), 
        ('+', 2), ('+/tennis/#', 0), 
        ('sport/+/player1', 2), ('/finance', 0), 
        ('finance/', 1), ('/finance/', 2), ('/', 0), ('+/+', 1),
        ('/+', 2), ('+/', 0), ('/+/', 1),
        # Invalid
        # ('sport/tennis#', 0), ('sport/tennis/#/ranking',1), ('sport+', 1), ('', 2),
    ])
    client.loop_forever()


if __name__ == '__main__':
    connect()
