from time import sleep
import unittest
from unittest import TestCase
from unittest.mock import Mock, call
from paho.mqtt import client as mqtt_client


broker = 'broker'
client_id = f'subscriber1'
    

class TestSubscriber1(TestCase):

    def on_log(client, userdata, level, buf):
        print('log:', buf)
        TestSubscriber1._on_log(buf)


    def on_subsribe(client, userdata, mid, granted_qos):
        print('mid:', mid, 'qos:', granted_qos)
        TestSubscriber1._on_subscribe(mid, granted_qos)


    @classmethod
    def setUpClass(self):
        client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)
        
        TestSubscriber1._on_log = Mock()
        TestSubscriber1._on_subscribe = Mock()

        client.on_log = TestSubscriber1.on_log
        client.on_subscribe = TestSubscriber1.on_subsribe

        client.connect(broker, 1883)
        client.loop_start()
        client.subscribe('house',0)
        client.subscribe([('house/room/main-light',0), ('house/room/side-light', 0)])
        sleep(2)
        client.loop_stop()

    
    def test_on_log(self):
        TestSubscriber1._on_log.assert_has_calls([
            call("Sending CONNECT (u0, p0, wr0, wq0, wf0, c1, k60) client_id=b'subscriber1'"),
            call('Received CONNACK (0, 0)'),
            call("Sending SUBSCRIBE (d0, m1) [(b'house', 0)]"),
            call("Sending SUBSCRIBE (d0, m2) [(b'house/room/main-light', 0), (b'house/room/side-light', 0)]"),
            call("Received SUBACK"),
        ],any_order=True)


    def test_on_subscribe(self):
        TestSubscriber1._on_subscribe.assert_has_calls([
            call(1, (0,)),
            call(2, (0,0)),
        ], any_order=False)
        self.assertEqual(self._on_subscribe.call_count, 2)

    
if __name__ == '__main__':
    unittest.main()
