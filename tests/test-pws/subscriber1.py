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
    client.loop_start()
    client.subscribe([('house/gargage',0),('house/room/main-light',1),('house/room/side-light',2)])
    sleep(3)
    client.loop_stop()
    sleep(3)
    client.disconnect()
    sleep(20)
    print('after 23 seconds')
    client.connect(broker, 1883)
    client.loop_start()
    sleep(5)
    client.loop_stop()
    sleep(5)
    client.disconnect()
    sleep(1)


if __name__ == '__main__':
    main()

