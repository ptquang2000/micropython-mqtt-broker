from paho.mqtt import client as mqtt_client
import time
import sys

broker = '172.17.0.2'
port = 1883

MSG_COUNT = 2 
topic1 = "python/mqtt"
topic2 = "java/mqtt"

def subscribe_basic():
  client_id = f'mqtt-client-0'
  client = mqtt_client.Client(client_id, protocol=5)
  client.on_log = on_log
  client.connect(broker, port)

  client.loop_start()
  time.sleep(1)
  msg = f"this is a new messages: 0"
  client.publish(topic1, msg)
  time.sleep(1)
  client.subscribe(topic1)
  time.sleep(1)
  client.loop_stop()

def subscribe_multi():
  client_id = f'mqtt-client-0'
  client = mqtt_client.Client(client_id, protocol=5)
  client.on_log = on_log
  client.connect(broker, port)

  client.loop_start()
  time.sleep(1)
  msg = f"this is a new messages: 0"
  client.publish(topic1, msg)
  time.sleep(1)
  client.publish(topic2, msg)
  time.sleep(1)
  client.subscribe([(topic1,0), (topic2,0)])
  time.sleep(1)
  client.loop_stop()

def on_log(client, userdata, level, buf):
  print('log:', buf)

if __name__ == '__main__':
    if sys.argv[1] == 'basic':
      subscribe_basic()
    if sys.argv[1] == 'multi':
      subscribe_multi()
