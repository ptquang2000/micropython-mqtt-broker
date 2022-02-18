from time import sleep
from paho.mqtt import client as mqtt_client

broker = 'broker'
port = 1883

def on_log(client, userdata, level, buf):
    print('log:', buf)


def on_publish(client, userdata, mid):
    print("mid: "+str(mid))


def publish():
    client_id = f'publisher'
    client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)
    client.on_log = on_log
    client.connect(broker, port)

    client.loop_start()
    sleep(2)
    msg = 'on'
    (rc, mid) = client.publish(
        'house/room', 
        msg, 
        qos=0,
        retain=True)
    sleep(2)
    msg = 'off'
    (rc, mid) = client.publish(
        'house/room', 
        msg, 
        qos=0,
        retain=False)
    sleep(2)
    client.disconnect()
    sleep(1)
    client.loop_stop()


publish()