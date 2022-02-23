from time import sleep
import unittest
from unittest import TestCase
from unittest.mock import Mock, call
from mpaho.mqtt import client as mqtt_client

broker = 'broker'
client_id = f'publisher1'


class TestPublisher1(TestCase):

    def on_disconnect(client, userdata, rc=0):
        client.loop_stop()
        print('rc:',rc)


    def on_log(client, userdata, level, buf):
        print('log:', buf)
        TestPublisher1._on_log(buf)

    
    def on_publish(client, userdata, result):
        print('result:', result)
        TestPublisher1._on_publish(result)


    @classmethod
    def setUpClass(cls):
        cls._on_log = Mock()
        cls._on_publish = Mock()

        client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311, clean_session=False)
        client.on_log = cls.on_log
        client.on_publish = cls.on_publish
        client.on_disconnect = cls.on_disconnect
        
        client.connect(broker, 1883)
        client.loop_start()
        (rc, mid) = client.publish(
            'house/room1', 
            'room1-r',
            retain=1,
            qos=1)
        
        sleep(2)
        client.disconnect()

        sleep(8)
        client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311, clean_session=False)
        client.on_log = cls.on_log
        client.on_publish = cls.on_publish
        client.on_disconnect = cls.on_disconnect
        client.connect(broker, 1883)
        client.loop_start()

        sleep(2)
        (rc, mid) = client.publish(
            'house/room1', 
            '', 
            retain=1,
            qos=1)

        sleep(2)
        client.suppress_puback = True
        print('suppress puback')

        sleep(2)
        (rc, mid) = client.publish(
            'house/room1',
            'room1', 
            qos=1)
            
        sleep(2)
        client.suppress_puback = False  
        print('un-suppress puback')
        client.disconnect()
        
        sleep(2)
        client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311, clean_session=False)
        client.on_log = cls.on_log
        client.on_publish = cls.on_publish
        client.on_disconnect = cls.on_disconnect
        client.connect(broker, 1883)
        client.loop_start()

        sleep(2)
        client.loop_stop()


    def test_on_log(self):
        TestPublisher1._on_log.assert_has_calls([
            call("Sending CONNECT (u0, p0, wr0, wq0, wf0, c0, k60) client_id=b'publisher1'"),
            call("Received CONNACK (0, 0)"),
            call("Received CONNACK (1, 0)"),
            call("Sending PUBLISH (d0, q1, r1, m1), 'b'house/room1'', ... (7 bytes)"),
            call("Received PUBACK (Mid: 1)"),
            call("Sending PUBLISH (d0, q1, r1, m1), 'b'house/room1'' (NULL payload)"),
            call("Received PUBACK (Mid: 1)"),
            call("Sending PUBLISH (d0, q1, r0, m1), 'b'house/room1'', ... (5 bytes)"),
        ],any_order=True)
        self.assertEqual(TestPublisher1._on_log.call_count, 12)


    def test_on_publish(self):
        TestPublisher1._on_publish.assert_has_calls([
            call(1),
        ], any_order=False)
        self.assertEqual(TestPublisher1._on_publish.call_count, 2)

    
if __name__ == '__main__':
    unittest.main()