from time import sleep
import unittest
from paho.mqtt import client as mqtt_client
from unittest.mock import Mock, call
from unittest import TestCase


broker = 'broker'
client_id = f'client1'

    
class TestDuplicateID(TestCase):

    def on_connect(self, client, userdata, flags, rc):
        print(flags, rc)
        self._on_connect(flags, rc)


    def on_disconnect(self, client, userdata,  rc):
        print(rc)
        self._on_disconnect(rc)


    def on_log(self, client, userdata, level, buf):
        print(buf)
        self._on_log(buf)


    def setUp(self):
        client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)
        self._on_connect = Mock()
        self._on_disconnect = Mock()
        self._on_log = Mock()
        client.on_connect = self.on_connect
        client.on_disconnect = self.on_disconnect
        client.on_log = self.on_log
        client.connect(broker, 1883, keepalive=1)
        client.loop_start()
        for _ in range(5):
            sleep(1)
        client.loop_stop()


    def test_on_connect(self):
        self._on_connect.assert_has_calls([
            call({'session present': 0}, 0)
        ], any_order=True)


    def test_on_disconnect(self):
        self._on_disconnect.assert_has_calls([
            call(7)
        ], any_order=True)


    def test_on_log(self):
        self._on_log.assert_has_calls([
            call("Sending CONNECT (u0, p0, wr0, wq0, wf0, c1, k1) client_id=b'client1'"),
            call("Received CONNACK (0, 0)"),
            call("Sending PINGREQ"),
            call("failed to receive on socket: [Errno 104] Connection reset by peer")
        ], any_order=True)

    

if __name__ == '__main__':
    unittest.main()
