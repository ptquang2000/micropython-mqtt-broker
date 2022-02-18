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
    # client.on_publish = on_publish
    client.connect(broker, port)
    sleep(2)

    (rc, mid) = client.publish(
        'sport/tennis/player1', 
        'player1 ', 
        qos=0)
    (rc, mid) = client.publish(
        'sport/tennis/player2', 
        'player2', 
        qos=0)
    (rc, mid) = client.publish(
        'sport/tennis/player1/ranking', 
        'ranking', 
        qos=0)
    (rc, mid) = client.publish(
        'sport', 
        'sport', 
        qos=0)
    (rc, mid) = client.publish(
        'sport/', 
        'sport/', 
        qos=0)
    (rc, mid) = client.publish(
        '/sport', 
        '/sport', 
        qos=0)
    (rc, mid) = client.publish(
        'finance/tennis', 
        'tennis', 
        qos=0)
    client.loop_forever()

publish()