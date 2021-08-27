from paho.mqtt import client as mqtt_client
import time

broker = '172.17.0.2'
port = 1883

MSG_COUNT = 2 
topic = "python/mqtt"

def subscribe_basic():
  client_id = f'mqtt-client-0'
  client = mqtt_client.Client(client_id, protocol=5)
  client.on_log = on_log
  client.connect(broker, port)

  client.loop_start()
  time.sleep(1)
  msg = f"this is a new messages: 0"
  client.publish(topic, msg)
  time.sleep(1)
  client.subscribe(topic)
  time.sleep(2)
  client.loop_stop()

def on_log(client, userdata, level, buf):
  print('log:', buf)

if __name__ == '__main__':
  subscribe_basic()
