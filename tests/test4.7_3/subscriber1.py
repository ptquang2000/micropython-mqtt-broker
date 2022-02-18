from paho.mqtt import client as mqtt_client


broker = 'broker'
client_id = f'subscriber1'

def on_log(client, userdata, level, buf):
    print('log:', buf)

def on_message(client, userdata, message):
    print("received message =",str(message.payload.decode("utf-8")))

def connect():
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)
    client.on_log = on_log
    client.on_message = on_message
    client.connect(broker, 1883)
    client.subscribe('sport/tennis/+',0)
    client.loop_forever()


if __name__ == '__main__':
    connect()
