from time import sleep
import unittest
from unittest import TestCase
from unittest.mock import Mock, call
from paho.mqtt import client as mqtt_client

broker = 'broker'
client_id = f'publisher'


class TestPublisher(TestCase):

    def on_log(client, userdata, level, buf):
        print('log:', buf)
        TestPublisher._on_log(buf)

    
    def on_publish(client, userdata, mid):
        print('mid:', mid)
        TestPublisher._on_publish(mid)


    @classmethod
    def setUpClass(cls):
        client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)

        cls._on_log = Mock()
        cls._on_publish = Mock()

        client.on_log = cls.on_log
        client.on_publish = cls.on_publish
        
        client.connect(broker, 1883)
        sleep(2)
        msg = 'on'
        (rc, mid) = client.publish(
            'house/room', 
            msg, 
            qos=0,
            retain=True)
        sleep(2)
        msg = 'off'
        (rc, mid) = client.publish(
            'house/room', 
            msg, 
            qos=0,
            retain=False)


    def test_on_log(self):
        TestPublisher._on_log.assert_has_calls([
            call("Sending CONNECT (u0, p0, wr0, wq0, wf0, c1, k60) client_id=b'publisher'"),
            call("Sending PUBLISH (d0, q0, r1, m1), 'b'house/room'', ... (2 bytes)"),
            call("Sending PUBLISH (d0, q0, r0, m2), 'b'house/room'', ... (3 bytes)")
        ],any_order=False)


    def test_on_publish(self):
        TestPublisher._on_publish.assert_has_calls([
            call(1),
            call(2),
        ], any_order=False)

    
if __name__ == '__main__':
    unittest.main()