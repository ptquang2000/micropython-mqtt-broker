from asyncore import loop
from time import sleep
from paho.mqtt import client as mqtt_client
import sys

broker = sys.argv[1]
port = 1883

def on_log(client, userdata, level, buf):
    print('log:', buf)


def publish():
    client_id = f'publisher1'
    client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)
    client.on_log = on_log
    client.connect(broker, port)
    client.loop_start()
    sleep(2)
    msg = 'on'
    (rc, mid) = client.publish(
        'house/room', 
        msg, 
        qos=1)
    sleep(3)
    client.disconnect()
    sleep(1)
    client.loop_stop()

publish()