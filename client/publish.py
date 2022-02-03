from paho.mqtt import client as mqtt_client
import time
import sys

broker = sys.argv[1]
port = 1883

def publish():
    client_id = f'mqttclient'
    client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)
    client.on_log = on_log
    client.connect(broker, port)

    client.loop_start()
    temperature = 0
    while True:
        temperature += 10
        (rc, mid) = client.publish('encyclopedia/temperature', str(temperature), qos=0)
        time.sleep(5)

def on_log(client, userdata, level, buf):
    print('log:', buf)

def on_publish(client, userdata, mid):
    print("mid: "+str(mid))

publish()