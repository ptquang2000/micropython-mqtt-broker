from paho.mqtt import client as mqtt_client
import sys

broker = sys.argv[1]
port = 1883

def subscribe():
    client_id = f'mqttclient0'
    client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)
    client.on_log = on_log
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.connect(broker, port)

    client.subscribe('encyclopedia/temperature', qos=0)
    client.loop_forever()


def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))  

def on_log(client, userdata, level, buf):
    print('log:', buf)

subscribe()
