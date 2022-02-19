from time import sleep
from paho.mqtt import client as mqtt_client
from unittest.mock import Mock, call
from unittest import TestCase


broker = 'broker'
client_id = f'client1'

connects = []
disconnect = []
logs = []


def on_connect(client, userdata, flags, rc):
    print(flags, rc)


def on_disconnect(client, userdata,  rc):
    print(rc)


def on_log(client, userdata, level, buf):
    print(buf)
    


def connect():
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_log = on_log
    client.connect(broker, 1883, keepalive=2)
    client.loop_start()
    for _ in range(10):
        sleep(1)
    client.loop_stop()


class TestConnect(TestCase):

    def test_connect(self):
        pass



if __name__ == '__main__':
    connect()
