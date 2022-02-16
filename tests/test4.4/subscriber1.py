import sys
from time import sleep
from paho.mqtt import client as mqtt_client


broker = sys.argv[1]

def on_log(client, userdata, level, buf):
    print('log:', buf)

def main():
    client_id = f'subscriber1'
    # Set Connecting Client IDl
    client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311, clean_session=False)
    client.on_log = on_log
    client.connect(broker, 1883)
    sleep(1)
    client.subscribe('house/room',0)
    client.subscribe('house/gargage',1)
    client.subscribe('house/room/main-light',2)
    sleep(1)
    client.disconnect()
    sleep(4)
    client.connect(broker, 1883)
    client.loop_forever()


if __name__ == '__main__':
    main()
