from time import sleep
import unittest
from unittest import TestCase
from unittest.mock import Mock, call
from paho.mqtt import client as mqtt_client


broker = 'broker'
client_id = f'publisher1'


class TestPublisher1(TestCase):

    def on_log(client, userdata, level, buf):
        print('log:', buf)
        TestPublisher1._on_log(buf)

    
    def on_publish(client, userdata, mid):
        print('mid:', mid)
        TestPublisher1._on_publish(mid)


    @classmethod
    def setUpClass(cls):
        client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)

        cls._on_log = Mock()
        cls._on_publish = Mock()

        client.on_log = cls.on_log
        client.on_publish = cls.on_publish
        
        client.connect(broker, 1883)
        client.loop_start()
        sleep(2)
        (rc, mid) = client.publish(
            'house/room', 
            'on', 
            qos=1)
        sleep(4)
        client.loop_stop()


    def test_on_log(self):
        TestPublisher1._on_log.assert_has_calls([
            call("Sending CONNECT (u0, p0, wr0, wq0, wf0, c1, k60) client_id=b'publisher1'"),
            call("Received CONNACK (0, 0)"),
            call("Sending PUBLISH (d0, q1, r0, m1), 'b'house/room'', ... (2 bytes)"),
            call("Received PUBACK (Mid: 1)"),
        ],any_order=True)


    def test_on_publish(self):
        TestPublisher1._on_publish.assert_has_calls([
            call(1),
        ], any_order=False)

    
if __name__ == '__main__':
    unittest.main()