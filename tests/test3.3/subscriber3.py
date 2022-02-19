from time import sleep
import unittest
from unittest import TestCase
from unittest.mock import Mock, call
from paho.mqtt import client as mqtt_client


broker = 'broker'
client_id = f'subscriber3'


class TestSubscriber3(TestCase):

    def on_log(client, userdata, level, buf):
        print('log:', buf)
        TestSubscriber3._on_log(buf)

    
    def on_subsribe(client, userdata, mid, granted_qos):
        print('mid:', mid, 'qos:', granted_qos)
        TestSubscriber3._on_subscribe(mid, granted_qos)


    def on_message(client, userdata, message):
        print('receive message:', str(message.payload.decode('utf8')), ', topic:', message.topic, ', retain:', message.retain)
        TestSubscriber3._on_message(str(message.payload.decode('utf8')), message.topic, message.retain)


    @classmethod
    def setUpClass(cls):
        # Set Connecting Client IDl
        client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)

        cls._on_log = Mock()
        cls._on_subscribe = Mock()
        cls._on_message = Mock()

        client.on_log = cls.on_log
        client.on_message = cls.on_message
        client.on_subscribe = cls.on_subsribe
        
        client.connect(broker, 1883)
        client.loop_start()
        sleep(8)
        client.subscribe([('house/garage',0),('house/room',0)])
        sleep(2)
        client.loop_stop()


    def test_on_log(self):
        TestSubscriber3._on_log.assert_has_calls([
            call("Sending CONNECT (u0, p0, wr0, wq0, wf0, c1, k60) client_id=b'subscriber3'"),
            call('Received CONNACK (0, 0)'),
            call("Sending SUBSCRIBE (d0, m1) [(b'house/garage', 0), (b'house/room', 0)]"),
            call("Received PUBLISH (d0, q0, r1, m0), 'house/room', ...  (3 bytes)"),
            call("Received PUBLISH (d0, q0, r1, m0), 'house/garage', ...  (3 bytes)"),
            call('Received SUBACK'),
            call("Received PUBLISH (d0, q0, r0, m0), 'house/garage', ...  (0 bytes)"),
            call("Received PUBLISH (d0, q0, r0, m0), 'house/room', ...  (0 bytes)")
        ],any_order=True)


    def test_on_subscribe(self):
        TestSubscriber3._on_subscribe.assert_has_calls([
            call(1, (0,0)),
        ], any_order=False)
        self.assertEqual(self._on_subscribe.call_count, 1)

    
    def test_on_message(self):
        TestSubscriber3._on_message.assert_has_calls([
            call('', 'house/garage', 0),
            call('', 'house/room', 0)
        ], any_order=False)


if __name__ == '__main__':
    unittest.main()
