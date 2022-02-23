from time import sleep
import unittest
from unittest import TestCase
from unittest.mock import Mock, call
from mpaho.mqtt import client as mqtt_client


broker = 'broker'
client_id = f'subscriber1'

class TestSubscriber1(TestCase):

    def on_disconnect(client, userdata, rc=0):
        client.loop_stop()

        print('rc:',rc)


    def on_log(client, userdata, level, buf):
        print('log:', buf)
        TestSubscriber1._on_log(buf)


    def on_subsribe(client, userdata, mid, granted_qos):
        print('mid:', mid, 'qos:', granted_qos)
        TestSubscriber1._on_subscribe(mid, granted_qos)


    def on_message(client, userdata, message):
        print('receive message:', str(message.payload.decode('utf8')), ', topic:', message.topic, ', retain:', message.retain)
        TestSubscriber1._on_message(str(message.payload.decode('utf8')), message.topic, message.retain)


    @classmethod
    def setUpClass(cls):
        TestSubscriber1._on_log = Mock()
        TestSubscriber1._on_subscribe = Mock()
        TestSubscriber1._on_message = Mock()

        client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311, clean_session=False)
        client.on_log = cls.on_log
        client.on_message = cls.on_message
        client.on_subscribe = cls.on_subsribe
        client.on_disconnect = cls.on_disconnect

        client.connect(broker, 1883)
        client.loop_start()

        sleep(1)
        client.subscribe('house/room1',1)

        sleep(1)
        client.disconnect()

        sleep(6)
        client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311, clean_session=False)
        client.on_log = cls.on_log
        client.on_message = cls.on_message
        client.on_subscribe = cls.on_subsribe
        client.on_disconnect = cls.on_disconnect
        client.connect(broker, 1883)
        client.loop_start()

        sleep(3)
        client.suppress_publish = True
        print('suppress publish')
        
        sleep(5)
        print('un-suppress puback')
        client.suppress_publish = False
        client.disconnect()
        
        sleep(1)
        client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311, clean_session=False)
        client.on_log = cls.on_log
        client.on_message = cls.on_message
        client.on_subscribe = cls.on_subsribe
        client.on_disconnect = cls.on_disconnect
        client.connect(broker, 1883)
        client.loop_start()

        sleep(3)
        client.loop_stop()

    
    def test_on_log(self):
        TestSubscriber1._on_log.assert_has_calls([
            call("Sending CONNECT (u0, p0, wr0, wq0, wf0, c0, k60) client_id=b'subscriber1'"), #3
            call('Received CONNACK (0, 0)'),
            call('Received CONNACK (1, 0)'), #2
            call("Sending SUBSCRIBE (d0, m1) [(b'house/room1', 1)]"),
            call("Received SUBACK"),
            call("Received PUBLISH (d0, q1, r1, m1), 'house/room1', ...  (7 bytes)"),
            call("Sending PUBACK (Mid: 1)"),
            call("Sending PUBACK (Mid: 2)"),
            call("Received PUBLISH (d0, q1, r0, m3), 'house/room1', ...  (0 bytes)"),
            call("Sending PUBACK (Mid: 3)"),
            call("Received PUBLISH (d1, q1, r0, m4), 'house/room1', ...  (5 bytes)"),
            call("Sending PUBACK (Mid: 4)"),
            call("Sending DISCONNECT") #2
        ],any_order=True)
        self.assertEqual(TestSubscriber1._on_log.call_count, 18)


    def test_on_subscribe(self):
        TestSubscriber1._on_subscribe.assert_has_calls([
            call(1, (1,)),
        ], any_order=False)
        self.assertEqual(self._on_subscribe.call_count, 1)

    
    def test_on_message(self):
        TestSubscriber1._on_message.assert_has_calls([
            call('room1-r', 'house/room1', 1),
            call('room1-r', 'house/room1', 1),
            call('', 'house/room1', 0),
        ], any_order=False)
        self.assertEqual(TestSubscriber1._on_message.call_count, 4)


if __name__ == '__main__':
    unittest.main()
