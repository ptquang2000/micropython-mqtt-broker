from time import sleep
import unittest
from unittest import TestCase
from unittest.mock import Mock, call
from paho.mqtt import client as mqtt_client


broker = 'broker'
client_id = f'subscriber2'
    

class TestSubscriber2(TestCase):

    def on_log(client, userdata, level, buf):
        print('log:', buf)
        TestSubscriber2._on_log(buf)


    def on_subsribe(client, userdata, mid, granted_qos):
        print('mid:', mid, 'qos:', granted_qos)
        TestSubscriber2._on_subscribe(mid, granted_qos)


    @classmethod
    def setUpClass(self):
        client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)
        
        TestSubscriber2._on_log = Mock()
        TestSubscriber2._on_subscribe = Mock()

        client.on_log = TestSubscriber2.on_log
        client.on_subscribe = TestSubscriber2.on_subsribe

        client.connect(broker, 1883)
        client.loop_start()
        client.subscribe([
            ('house/room/main-light',0), ('house/room/side-light', 0),
            ('house/room1/alarm', 0), ('house/room1/main-light',0), 
            ('house/room1/side-light', 0), ('house/room2/main-light', 0), 
            ('house/main-door', 0), ('house/garage/main-light',0),
            ('house/room2/side-light', 0)
        ])
        sleep(2)
        client.loop_stop()

    
    def test_on_log(self):
        TestSubscriber2._on_log.assert_has_calls([
            call("Sending CONNECT (u0, p0, wr0, wq0, wf0, c1, k60) client_id=b'subscriber2'"),
            call('Received CONNACK (0, 0)'),
            call("Sending SUBSCRIBE (d0, m1) [(b'house/room/main-light', 0), (b'house/room/side-light', 0), (b'house/room1/alarm', 0), (b'house/room1/main-light', 0), (b'house/room1/side-light', 0), (b'house/room2/main-light', 0), (b'house/main-door', 0), (b'house/garage/main-light', 0), (b'house/room2/side-light', 0)]"),
            call("Received SUBACK"),
        ],any_order=True)


    def test_on_subscribe(self):
        TestSubscriber2._on_subscribe.assert_has_calls([
            call(1, (0,0,0,0,0,0,0,0,0)),
        ], any_order=False)
        self.assertEqual(self._on_subscribe.call_count, 1)

    
if __name__ == '__main__':
    unittest.main()
