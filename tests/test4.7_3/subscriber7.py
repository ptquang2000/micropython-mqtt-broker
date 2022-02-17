import sys
from paho.mqtt import client as mqtt_client


broker = sys.argv[1]

def on_log(client, userdata, level, buf):
    print('log:', buf)

def on_message(client, userdata, message):
    print("received message =",str(message.payload.decode("utf-8")))

def connect():
    client_id = f'subscriber7'
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)
    client.on_log = on_log
    client.on_message = on_message
    client.connect(broker, 1883)
    client.subscribe('sport/+',0)
    client.loop_forever()


if __name__ == '__main__':
    connect()
