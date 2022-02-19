from time import sleep
import unittest
from unittest import TestCase
from unittest.mock import Mock, call
from paho.mqtt import client as mqtt_client


broker = 'broker'
port = 1883
client_id = f'publisher'


class TestPublisher(TestCase):

    def on_log(client, userdata, level, buf):
        print('log:', buf)
        TestPublisher._on_log(buf)

    
    def on_publish(client, userdata, result):
        print('result:', result)
        TestPublisher._on_publish(result)


    @classmethod
    def setUpClass(cls):
        client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)

        cls._on_log = Mock()
        cls._on_publish = Mock()

        client.on_log = cls.on_log
        client.on_publish = cls.on_publish
        
        client.connect(broker, 1883)
        client.loop_start()
        msg = 'on'
        for _ in range(2):
            sleep(2)
            (rc, mid) = client.publish(
                'house/room1/main-light', 
                msg, 
                qos=0)
            (rc, mid) = client.publish(
                'house/room2/main-light', 
                msg, 
                qos=0)
            (rc, mid) = client.publish(
                'house/room1/side-light', 
                msg, 
                qos=0)
            (rc, mid) = client.publish(
                'house/room2/side-light', 
                msg, 
                qos=0)
            (rc, mid) = client.publish(
                'house/garage', 
                msg, 
                qos=0)
            (rc, mid) = client.publish(
                'house', 
                msg, 
                qos=0)
            msg = 'off'
        client.loop_stop()


    def test_on_log(self):
        TestPublisher._on_log.assert_has_calls([
            call("Sending CONNECT (u0, p0, wr0, wq0, wf0, c1, k60) client_id=b'publisher'"),
            call("Received CONNACK (0, 0)"),
            call("Sending PUBLISH (d0, q0, r0, m1), 'b'house/room1/main-light'', ... (2 bytes)"),
            call("Sending PUBLISH (d0, q0, r0, m2), 'b'house/room2/main-light'', ... (2 bytes)"),
            call("Sending PUBLISH (d0, q0, r0, m3), 'b'house/room1/side-light'', ... (2 bytes)"),
            call("Sending PUBLISH (d0, q0, r0, m4), 'b'house/room2/side-light'', ... (2 bytes)"),
            call("Sending PUBLISH (d0, q0, r0, m5), 'b'house/garage'', ... (2 bytes)"),
            call("Sending PUBLISH (d0, q0, r0, m6), 'b'house'', ... (2 bytes)"),
            call("Sending PUBLISH (d0, q0, r0, m7), 'b'house/room1/main-light'', ... (3 bytes)"),
            call("Sending PUBLISH (d0, q0, r0, m8), 'b'house/room2/main-light'', ... (3 bytes)"),
            call("Sending PUBLISH (d0, q0, r0, m9), 'b'house/room1/side-light'', ... (3 bytes)"),
            call("Sending PUBLISH (d0, q0, r0, m10), 'b'house/room2/side-light'', ... (3 bytes)"),
            call("Sending PUBLISH (d0, q0, r0, m11), 'b'house/garage'', ... (3 bytes)"),
            call("Sending PUBLISH (d0, q0, r0, m12), 'b'house'', ... (3 bytes)"),
        ],any_order=True)


    def test_on_publish(self):
        TestPublisher._on_publish.assert_has_calls([
            call(1),
            call(2),
            call(3),
            call(4),
            call(5),
            call(6),
            call(7),
            call(8),
            call(9),
            call(10.),
            call(11.),
            call(12.),
        ], any_order=False)

    
if __name__ == '__main__':
    unittest.main()