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
    client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)
    client.on_log = on_log
    client.connect(broker, port)
    client.on_publish = on_publish
    msg = 'on'
    (rc, mid) = client.publish(
        'house/room', 
        msg, 
        qos=2)
    client._send_pingreq()
    sleep(3)
    client._send_pingreq()
    sleep(3)
    client._send_pingreq()

    client.loop_forever()

publish()