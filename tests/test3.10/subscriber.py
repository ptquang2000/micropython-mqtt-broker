from time import sleep
import unittest
from unittest import TestCase
from unittest.mock import Mock, call
from paho.mqtt import client as mqtt_client


broker = 'broker'
client_id = f'subscriber'

class TestSubscriber(TestCase):

    def on_log(client, userdata, level, buf):
        print('log:', buf)
        TestSubscriber._on_log(buf)


    def on_subsribe(client, userdata, mid, granted_qos):
        print('mid:', mid, 'qos:', granted_qos)
        TestSubscriber._on_subscribe(mid, granted_qos)

    
    def on_unsubscribe(client, userdata, mid):
        print('mid:', mid)
        TestSubscriber._on_unsubscribe(mid)


    @classmethod
    def setUpClass(self):
        client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)
        
        TestSubscriber._on_log = Mock()
        TestSubscriber._on_subscribe = Mock()
        TestSubscriber._on_unsubscribe = Mock()

        client.on_log = TestSubscriber.on_log
        client.on_subscribe = TestSubscriber.on_subsribe
        client.on_unsubscribe = TestSubscriber.on_unsubscribe

        client.connect(broker, 1883)
        client.loop_start()
        client.subscribe([('house/room1/main-light',0), 
            ('house/room1/side-light', 0), ('house/garage',0)
        ])
        sleep(2)
        client.unsubscribe('house')
        sleep(2)
        client.unsubscribe('house/room1/main-light')
        sleep(2)
        client.unsubscribe(['house/room1/side-light', 'house/garage'])
        sleep(2)
        client.subscribe('house/room1/side-light', 0)
        sleep(2)
        client.unsubscribe(['house/room1/side-light', 'house/garage'])
        sleep(2)
        client.loop_stop()

    
    def test_on_log(self):
        TestSubscriber._on_log.assert_has_calls([
            call("Sending CONNECT (u0, p0, wr0, wq0, wf0, c1, k60) client_id=b'subscriber'"),
            call("Sending SUBSCRIBE (d0, m1) [(b'house/room1/main-light', 0), (b'house/room1/side-light', 0), (b'house/garage', 0)]"),
            call("Sending UNSUBSCRIBE (d0, m2) [b'house']"),
            call("Sending UNSUBSCRIBE (d0, m3) [b'house/room1/main-light']"),
            call("Sending UNSUBSCRIBE (d0, m4) [b'house/room1/side-light', b'house/garage']"),
            call("Sending SUBSCRIBE (d0, m5) [(b'house/room1/side-light', 0)]"),
            call("Sending UNSUBSCRIBE (d0, m6) [b'house/room1/side-light', b'house/garage']"),
            call('Received CONNACK (0, 0)'),
            call("Received SUBACK"),
            call("Received UNSUBACK (Mid: 2)"),
            call("Received UNSUBACK (Mid: 3)"),
            call("Received UNSUBACK (Mid: 4)"),
            call("Received UNSUBACK (Mid: 6)"),
        ],any_order=True)


    def test_on_subscribe(self):
        TestSubscriber._on_subscribe.assert_has_calls([
            call(1, (0, 0, 0)),
            call(5, (0,))
        ], any_order=False)


    def test_on_unsubscribe(self):
        TestSubscriber._on_unsubscribe.assert_has_calls([
            call(2),
            call(3),
            call(4),
        ], any_order=False)

    
if __name__ == '__main__':
    unittest.main()
