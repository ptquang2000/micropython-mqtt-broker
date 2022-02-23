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
        client.loop_start()
        sleep(2)
        (rc, mid) = client.publish(
            'sport/tennis/player1', 
            'player1', 
            qos=0)
        (rc, mid) = client.publish(
            'sport/tennis/player2', 
            'player2', 
            qos=0)
        (rc, mid) = client.publish(
            'sport/tennis/player1/ranking', 
            'ranking', 
            qos=0)
        (rc, mid) = client.publish(
            'sport', 
            'sport', 
            qos=0)
        (rc, mid) = client.publish(
            'sport/', 
            'sport/', 
            qos=0)
        (rc, mid) = client.publish(
            '/sport', 
            '/sport', 
            qos=0)
        (rc, mid) = client.publish(
            'finance/tennis', 
            'tennis', 
            qos=0)
        client.loop_stop()


    def test_on_log(self):
        TestPublisher._on_log.assert_has_calls([
            call("Sending CONNECT (u0, p0, wr0, wq0, wf0, c1, k60) client_id=b'publisher'"),
            call("Received CONNACK (0, 0)"),
            call("Sending PUBLISH (d0, q0, r0, m1), 'b'sport/tennis/player1'', ... (7 bytes)"),
            call("Sending PUBLISH (d0, q0, r0, m2), 'b'sport/tennis/player2'', ... (7 bytes)"),
            call("Sending PUBLISH (d0, q0, r0, m3), 'b'sport/tennis/player1/ranking'', ... (7 bytes)"),
            call("Sending PUBLISH (d0, q0, r0, m4), 'b'sport'', ... (5 bytes)"),
            call("Sending PUBLISH (d0, q0, r0, m5), 'b'sport/'', ... (6 bytes)"),
            call("Sending PUBLISH (d0, q0, r0, m6), 'b'/sport'', ... (6 bytes)"),
            call("Sending PUBLISH (d0, q0, r0, m7), 'b'finance/tennis'', ... (6 bytes)"),
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
        ], any_order=False)

    
if __name__ == '__main__':
    unittest.main()