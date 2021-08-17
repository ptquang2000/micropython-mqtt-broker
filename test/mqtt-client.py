from paho.mqtt import client as mqtt_client
import random
import time

broker = '192.168.0.110'
port = 1883
topic = "/python/mqtt"
client_id = f'python-mqtt-{random.randint(0, 1000)}'

def connect_mqtt():
  def on_connect(client, userdata, flags, rc, proprties):
    if rc == 0:
      print("Connected to MQTT Broker!")
    else:
      print("Failed to connect, return code %d\n", rc)
  # Set Connecting Client ID
  client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv5)
  client.on_connect = on_connect
  client.connect(broker, port)
  return client

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
    if msg_count == 10:
      return

def run():
  client = connect_mqtt()
  client.loop_start()
  publish(client)
  client.loop_stop()
  client.disconnect()


if __name__ == '__main__':
  run()