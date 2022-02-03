import sys
import time
from paho.mqtt import client as mqtt_client

broker = sys.argv[1]
port = 1883

def on_log(client, userdata, level, buf):
    print('log:', buf)

def connect_basic():
    client_id = f'MqttClient0'
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)
    client.on_log = on_log
    client.connect(broker, port)

    client.loop_start()
    time.sleep(1)
    client.loop_stop()

def connect_auth():
    client_id = f'MqttClient0'
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)
    client.username_pw_set(username='mqtt', password='pass')
    client.on_log = on_log
    client.connect(broker, port)
    client.loop_start()
    time.sleep(1)
    client.loop_stop()

def test_connect():
    connect_basic()
    #connect_auth()

if __name__ == '__main__':
    test_connect()
