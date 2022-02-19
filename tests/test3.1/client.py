from time import sleep
import unittest
from paho.mqtt import client as mqtt_client
from unittest.mock import Mock, call
from unittest import TestCase


broker = 'broker'
client_id = f'client1'

    
class TestDuplicateID(TestCase):

    def on_connect(client, userdata, flags, rc):
        print('flags:', flags, 'return code:', rc)
        TestDuplicateID._on_connect(flags, rc)


    def on_disconnect(cclient, userdata,  rc):
        print('return code:', rc)
        TestDuplicateID._on_disconnect(rc)


    def on_log(client, userdata, level, buf):
        print('log:', buf)
        TestDuplicateID._on_log(buf)


    @classmethod
    def setUpClass(cls):
        client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)
        
        cls._on_connect = Mock()
        cls._on_disconnect = Mock()
        cls._on_log = Mock()
        
        client.on_connect = cls.on_connect
        client.on_disconnect = cls.on_disconnect
        client.on_log = cls.on_log
        
        client.connect(broker, 1883, keepalive=1)
        client.loop_start()
        sleep(5)
        client.loop_stop()


    def test_on_connect(self):
        TestDuplicateID._on_connect.assert_has_calls([
            call({'session present': 0}, 0)
        ], any_order=True)


    def test_on_disconnect(self):
        TestDuplicateID._on_disconnect.assert_has_calls([
            call(7)
        ], any_order=True)


    def test_on_log(self):
        TestDuplicateID._on_log.assert_has_calls([
            call("Sending CONNECT (u0, p0, wr0, wq0, wf0, c1, k1) client_id=b'client1'"),
            call("Received CONNACK (0, 0)"),
            call("Sending PINGREQ"),
            call("failed to receive on socket: [Errno 104] Connection reset by peer")
        ], any_order=True)

    

if __name__ == '__main__':
    unittest.main()
