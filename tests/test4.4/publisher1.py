from time import sleep
from paho.mqtt import client as mqtt_client

broker = 'broker'
port = 1883
client_id = f'publisher1'

def on_log(client, userdata, level, buf):
    print('log:', buf)

def on_publish(client, userdata, mid):
    while True:
        pass

def publish():
    client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311, clean_session=False)
    client.on_log = on_log
    client.connect(broker, port)
    client.loop_start
    sleep(10)
    msg = 'on'
    (rc, mid) = client.publish(
        'house/room', 
        msg, 
        qos=0)
    (rc, mid) = client.publish(
        'house/garage', 
        msg, 
        qos=1)
    (rc, mid) = client.publish(
        'house/room/main-light', 
        msg, 
        qos=2)
    sleep(1)
    msg = 'off'
    (rc, mid) = client.publish(
        'house/room', 
        msg, 
        qos=0)
    (rc, mid) = client.publish(
        'house/garage', 
        msg, 
        qos=1)
    client.loop_stop()
    client.connect(broker, port)
    (rc, mid) = client.publish(
        'house/room/main-light', 
        msg, 
        qos=2)
    sleep(1)
    msg = 'off'
    (rc, mid) = client.publish(
        'house/room', 
        msg, 
        qos=0)
    (rc, mid) = client.publish(
        'house/garage', 
        msg, 
        qos=1)
    (rc, mid) = client.publish(
        'house/room/main-light', 
        msg, 
        qos=2)
    client.loop_stop()
    client.connect(broker, port)
    client.loop_forever()

publish()