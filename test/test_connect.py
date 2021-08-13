
from paho.mqtt import client as mqtt_client
import random

broker = '192.168.0.110'
port = 1883
client_id = f'python-mqtt-java-cpp-{random.randint(0, 1000)}'

def connect_mqtt():
  def on_connect(client, userdata, flags, rc):
    if rc == 0:
      print("Connected to MQTT Broker!")
    else:
      print("Failed to connect, return code %d\n", rc)
  # Set Connecting Client ID
  client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv5)
  client.username_pw_set(username='mqtt', password='pass')
  client.on_connect = on_connect
  client.connect(broker, port)
  return client

def run():
  connect_mqtt()

if __name__ == '__main__':
  run()