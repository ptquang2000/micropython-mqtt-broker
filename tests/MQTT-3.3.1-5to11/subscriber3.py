import sys
from time import sleep
from paho.mqtt import client as mqtt_client


broker = sys.argv[1]

def on_log(client, userdata, level, buf):
    print('log:', buf)


def connect():
    client_id = f'subscriber3'
    # Set Connecting Client IDl
    client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)
    client.on_log = on_log
    client.connect(broker, 1883)
    client.loop_start()
    sleep(9)
    client.subscribe('house/garage',0)
    sleep(8)
    client.disconnect()
    sleep(1)
    client.loop_stop()


if __name__ == '__main__':
    connect()
