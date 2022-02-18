from time import sleep
from paho.mqtt import client as mqtt_client

broker = 'broker'
port = 1883
client_id = f'publisher'

def on_log(client, userdata, level, buf):
    print('log:', buf)


def on_publish(client, userdata, mid):
    print("mid: "+str(mid))


def publish():
    client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)
    client.on_log = on_log
    client.connect(broker, port)

    client.loop_start()
    (rc, mid) = client.publish(
        'house/garage/main-light', 
        'garage', 
        qos=0,
        retain=True)
    (rc, mid) = client.publish(
        'house/room/main-light', 
        'room-main', 
        qos=0,
        retain=True)
    (rc, mid) = client.publish(
        'house/room/side-light', 
        'room-side', 
        qos=0,
        retain=True)
    (rc, mid) = client.publish(
        'house/room', 
        'room', 
        qos=0,
        retain=True)
    (rc, mid) = client.publish(
        'house', 
        'house', 
        qos=0,
        retain=True)
    sleep(10)
    client.disconnect()
    sleep(1)
    client.loop_stop()


publish()