from time import sleep
from paho.mqtt import client as mqtt_client


broker = 'broker'
client_id = f'subscriber2'


def on_log(client, userdata, level, buf):
    print('log:', buf)


def connect():
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)
    client.on_log = on_log
    client.connect(broker, 1883)
    client.loop_start()
    sleep(4)
    client.subscribe('house/+/main-light',0)
    sleep(6)
    client.disconnect()
    sleep(1)
    client.loop_stop()


if __name__ == '__main__':
    connect()
