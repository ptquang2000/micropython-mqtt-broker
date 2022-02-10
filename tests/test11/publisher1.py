from asyncore import loop
from pydoc import cli
from time import sleep
from paho.mqtt import client as mqtt_client
import sys

broker = sys.argv[1]
port = 1883

def on_log(client, userdata, level, buf):
    print('log:', buf)

def on_publish(client, userdata, mid):
    while True:
        pass

def publish():
    client_id = f'publisher1'
    client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311, clean_session=False)
    client.on_log = on_log
    client.connect(broker, port)
    client.loop_start()
    msg = 'on'
    (rc, mid) = client.publish(
        'house/garage', 
        msg, 
        retain=True,
        qos=0)
    (rc, mid) = client.publish(
        'house/room/main-light', 
        msg, 
        retain=True,
        qos=1)
    (rc, mid) = client.publish(
        'house/room/side-light', 
        msg, 
        retain=True,
        qos=2)
    client.loop_stop()
    client.loop_start()
    sleep(6)
    print('after 6')
    client.connect(broker, port)
    sleep(2)
    msg = 'off'
    (rc, mid) = client.publish(
        'house/garage', 
        msg, 
        retain=True,
        qos=2)
    (rc, mid) = client.publish(
        'house/room/main-light',
        msg, 
        retain=True,
        qos=1)
    (rc, mid) = client.publish(
        'house/room/side-light ', 
        msg, 
        retain=True,
        qos=0)
    sleep(5)
    client.loop_stop()

publish()