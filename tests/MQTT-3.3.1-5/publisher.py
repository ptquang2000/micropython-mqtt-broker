from asyncore import loop
from time import sleep
from paho.mqtt import client as mqtt_client
import sys

broker = sys.argv[1]
port = 1883

def on_log(client, userdata, level, buf):
    print('log:', buf)

def on_publish(client, userdata, mid):
    print("mid: "+str(mid))


def publish():
    client_id = f'publisher'
    client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)
    client.on_log = on_log
    # client.on_publish = on_publish
    client.connect(broker, port)
    msg = 'on'

    client.loop_start()
    (rc, mid) = client.publish(
        'house/garage', 
        msg, 
        qos=0,
        retain=True)
    sleep(10)
    client.disconnect()
    sleep(1)
    client.loop_stop()

publish()