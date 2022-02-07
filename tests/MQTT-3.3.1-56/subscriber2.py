import sys
from time import sleep
from paho.mqtt import client as mqtt_client


broker = sys.argv[1]

def on_log(client, userdata, level, buf):
    print('log:', buf)

def connect():
    client_id = f'subscriber2'
    # Set Connecting Client IDl
    client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)
    client.on_log = on_log
    client.connect(broker, 1883)
    client.subscribe('house/garage',0)
    client.loop_forever()


if __name__ == '__main__':
    connect()
