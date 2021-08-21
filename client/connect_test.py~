
import time
from paho.mqtt import client as mqtt_client
import random

broker = '192.168.0.110'
port = 1883

MSG_COUNT = 2 
topic = "/python/mqtt"
def publish(client):
  msg_count = 0
  while True:
    time.sleep(1)
    msg = f"this is a new messages: {msg_count}"
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")
    msg_count += 1
    if msg_count == MSG_COUNT:
      break

def on_log(client, userdata, level, buf):
  print('log:', buf)

def connect_basic():
  client_id = f'mqtt-client-0'
  # Set Connecting Client ID
  client = mqtt_client.Client(client_id, protocol=5)
  client.on_log = on_log
  client.connect(broker, port)
  return client

def connect_auth():
  client_id = f'mqtt-client-0'
  # Set Connecting Client ID
  client = mqtt_client.Client(client_id, protocol=5)
  client.username_pw_set(username='mqtt', password='pass')
  client.on_log = on_log
  client.connect(broker, port)
  return client

def run():
  client = connect_basic()
  client.loop_start()
  time.sleep(2)
  client.loop_stop()
  client = connect_auth()
  client.loop_start()
  time.sleep(2)
  client.loop_stop()
  client.disconnect()

if __name__ == '__main__':
    run()
