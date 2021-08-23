import sys
import time
from paho.mqtt import client as mqtt_client
import random
import concurrent

broker = '172.17.0.2'
port = 1883

MSG_COUNT = 2 
topic = "/python/mqtt"
def publish_basic():
  client_id = f'mqtt-client-0'
  client = mqtt_client.Client(client_id, protocol=5)
  client.on_log = on_log
  client.connect(broker, port)

  client.loop_start()
  time.sleep(1)
  msg = f"this is a new messages: 0"
  client.publish(topic, msg)
  client.loop_stop()

def on_log(client, userdata, level, buf):
  print('log:', buf)

def connect_basic():
  client_id = f'mqtt-client-0'
  # Set Connecting Client ID
  client = mqtt_client.Client(client_id, protocol=5)
  client.on_log = on_log
  client.connect(broker, port)

  client.loop_start()
  time.sleep(1)
  client.loop_stop()

def connect_auth():
  client_id = f'mqtt-client-0'
  # Set Connecting Client ID
  client = mqtt_client.Client(client_id, protocol=5)
  client.username_pw_set(username='mqtt', password='pass')
  client.on_log = on_log
  client.connect(broker, port)
  client.loop_start()
  time.sleep(1)
  client.loop_stop()

def test_connect():
  connect_basic()
  connect_auth()

def test_publish():
  publish_basic()

def test_subscribe():
  publish_basic()
  subscibe_basic()

if __name__ == '__main__':
  test_connect()
