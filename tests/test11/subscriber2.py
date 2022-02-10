import sys
from time import sleep
from paho.mqtt import client as mqtt_client


broker = sys.argv[1]

def on_log(client, userdata, level, buf):
    print('log:', buf)

def main():
    client_id = f'subscriber2'
    # Set Connecting Client IDl
    client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311, clean_session=False)
    client.on_log = on_log
    client.connect(broker, 1883)
    client.loop_start()
    client.subscribe([('house/room/main-light',1),('house/room/side-light',2)])
    client.disconnect()
    sleep(6)
    print('after 6')
    client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311, clean_session=True)
    client.on_log = on_log
    client.connect(broker, 1883)
    sleep(2)
    print('after 8')
    client.subscribe([('house/gargage',2),('house/room/main-light',1),('house/room/side-light',0)])
    sleep(5) 
    client.disconnect()
    client.loop_stop()


if __name__ == '__main__':
    main()
    
