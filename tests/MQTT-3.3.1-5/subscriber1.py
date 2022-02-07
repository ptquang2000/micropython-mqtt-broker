import sys
from time import sleep
from paho.mqtt import client as mqtt_client


broker = sys.argv[1]

def on_subscribe(client, userdata, mid, granted_qos):
    print(f"mid:{mid}, qos:{granted_qos}")

def on_log(client, userdata, level, buf):
    print('log:', buf)


def on_connect(client, userdata, flags, rc):
    print("Connected")


def on_disconnect(client, userdata,  rc):
    print("Disconnected")


def on_message(client, userdata, message):
    print("received message =",str(message.payload.decode("utf-8")))


def connect():
    client_id = f'subscriber1'
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)
    client.on_log = on_log
    # client.on_connect = on_connect
    # client.on_subscribe = on_subscribe
    # client.on_message = on_message
    # client.on_disconnect = on_disconnect
    client.connect(broker, 1883)
    client.subscribe([('house', 0), ('house/garage',0)])
    sleep(10)
    client.disconnect()
    sleep(1)
    client.loop_stop()


if __name__ == '__main__':
    connect()
