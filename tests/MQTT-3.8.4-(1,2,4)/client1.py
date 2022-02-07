import sys
from time import sleep
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
    client_id = f'client1'
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)
    client.on_log = on_log
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_disconnect = on_disconnect
    client.connect(broker, 1883)
    client.subscribe('house',0)
    client.subscribe([('house/room/main-light',0), ('house/room/side-light', 0)])
    client.loop_forever()


if __name__ == '__main__':
    connect()
