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
        sleep(1)
        msg = 'temp'
        (rc, mid) = client.publish(
            'house/garage', 
            msg, 
            qos=0,
            retain=True)
        sleep(2)
        msg = 'on'
        (rc, mid) = client.publish(
            'house/garage', 
            msg, 
            qos=0,
            retain=True)
        sleep(3)
        msg = 'off'
        (rc, mid) = client.publish(
            'house/garage', 
            msg, 
            qos=0,
            retain=True)
        (rc, mid) = client.publish(
            'house/room', 
            msg, 
            qos=0,
            retain=True)
        sleep(3)
        msg = ''
        (rc, mid) = client.publish(
            'house/garage', 
            msg, 
            qos=0,
            retain=True)
        (rc, mid) = client.publish(
            'house/room', 
            msg, 
            qos=0,
            retain=True)


    def test_on_log(self):
        TestPublisher._on_log.assert_has_calls([
            call("Sending CONNECT (u0, p0, wr0, wq0, wf0, c1, k60) client_id=b'publisher'"),
            call("Sending PUBLISH (d0, q0, r1, m1), 'b'house/garage'', ... (4 bytes)"),
            call("Sending PUBLISH (d0, q0, r1, m2), 'b'house/garage'', ... (2 bytes)"),
            call("Sending PUBLISH (d0, q0, r1, m3), 'b'house/garage'', ... (3 bytes)"),
            call("Sending PUBLISH (d0, q0, r1, m4), 'b'house/room'', ... (3 bytes)"),
            call("Sending PUBLISH (d0, q0, r1, m5), 'b'house/garage'' (NULL payload)"),
            call("Sending PUBLISH (d0, q0, r1, m6), 'b'house/room'' (NULL payload)")
        ],any_order=True)


    def test_on_publish(self):
        TestPublisher._on_publish.assert_has_calls([
            call(1),
            call(2),
            call(3),
            call(4),
            call(5),
            call(6)
        ], any_order=False)

    
if __name__ == '__main__':
    unittest.main()