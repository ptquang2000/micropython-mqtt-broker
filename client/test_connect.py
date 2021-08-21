
import time
from paho.mqtt import client as mqtt_client
import random
import concurrent.futures

broker = '192.168.0.110'
port = 1883

MSG_COUNT = 5 
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

def on_connect(client, userdata, flags, rc, properties):
  if rc == 0:
    print("Connected to MQTT Broker!")
  else:
    print("Failed to connect, return code %d\n", rc)

def on_log(client, userdata, level, buf):
  print('log:', buf)

def connect_mqtt():
  client_id = f'mqtt-client-{random.randint(0, 10)}'
  # Set Connecting Client ID
  client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv5)
  # client.username_pw_set(username='mqtt', password='pass')
  #client.on_connect = on_connect
  client.on_log = on_log
  client.connect(broker, port)
  return client

def run():
  client = connect_mqtt()
  client.loop_start()
  publish(client)
  client.loop_stop()
  client.disconnect()

if __name__ == '__main__':
  with concurrent.futures.ThreadPoolExecutor() as e:
    clients = [e.submit(run) for _ in range(1)]
    for f in concurrent.futures.as_completed(clients):
      print('done  thread')
