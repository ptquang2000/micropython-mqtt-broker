
import time
from paho.mqtt import client as mqtt_client
import random
import concurrent.futures

broker = '192.168.0.110'
port = 1883

def on_connect(client, userdata, flags, rc, properties):
  print("Connected with result code "+str(rc))
  if rc == 0:
    print("Connected to MQTT Broker!")
  else:
    print("Failed to connect, return code %d\n", rc)


def connect_mqtt():
  client_id = f'python-mqtt-java-cpp-{random.randint(0, 10)}'
  # Set Connecting Client ID
  client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv5)
  # client.username_pw_set(username='mqtt', password='pass')
  client.on_connect = on_connect
  client.connect(broker, port)
  return client

def run():
  # with concurrent.futures.ThreadPoolExecutor() as e:
  #   clients = [e.submit(connect_mqtt) for _ in range(10)]
  #   for f in concurrent.futures.as_completed(clients):
  #     f.result().loop_start()
  client = connect_mqtt()
  client.loop_start()
  while True:
    print('waiting in loop')
    time.sleep(1)
if __name__ == '__main__':
  run()