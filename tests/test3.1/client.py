from time import sleep
from paho.mqtt import client as mqtt_client

broker = 'broker'
client_id = f'client1'

def on_connect(client, userdata, flags, rc):
    print("Connected")


def on_disconnect(client, userdata,  rc):
    print("Disconnected")

def on_log(client, userdata, level, buf):
    print('log:', buf)

def connect():
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_log = on_log
    client.connect(broker, 1883)
    client.loop_forever()

if __name__ == '__main__':
    connect()
