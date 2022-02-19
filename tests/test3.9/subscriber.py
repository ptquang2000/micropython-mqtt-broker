from time import sleep
import unittest
from unittest import TestCase
from unittest.mock import Mock, call
from paho.mqtt import client as mqtt_client


broker = 'broker'
client_id = f'subscriber'


class TestSubscriber(TestCase):

    def on_log(client, userdata, level, buf):
        print('log:', buf)
        TestSubscriber._on_log(buf)


    def on_subsribe(client, userdata, mid, granted_qos):
        print('mid:', mid, 'qos:', granted_qos)
        TestSubscriber._on_subscribe(mid, granted_qos)


    @classmethod
    def setUpClass(self):
        client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)
        
        TestSubscriber._on_log = Mock()
        TestSubscriber._on_subscribe = Mock()

        client.on_log = TestSubscriber.on_log
        client.on_subscribe = TestSubscriber.on_subsribe

        client.connect(broker, 1883)
        client.loop_start()
        client.subscribe([
        ('sport/tennis/player1',0), ('sport/tennis/player1/ranking', 1), ('sport/tennis/player1/score/wimbledon', 2),
        ('sport/#',0), ('#', 1), ('sport/tennis/#', 2), 
        ('+/tennis/#', 0), ('+', 1), ('sport/+/player1', 2),
        ('/finance', 0), ('finance/', 1), ('/finance/', 2),
        ('/', 0), ('+/+', 1), ('/+', 2), ('+/', 0), ('/+/', 1),
        # Invalid
        # ('sport/tennis#', 0), ('sport/tennis/#/ranking',1), ('sport+', 1), ('', 2),
    ])
        sleep(2)
        client.loop_stop()

    
    def test_on_log(self):
        TestSubscriber._on_log.assert_has_calls([
            call("Sending CONNECT (u0, p0, wr0, wq0, wf0, c1, k60) client_id=b'subscriber'"),
            call('Received CONNACK (0, 0)'),
            call("Sending SUBSCRIBE (d0, m1) [(b'sport/tennis/player1', 0), (b'sport/tennis/player1/ranking', 1), (b'sport/tennis/player1/score/wimbledon', 2), (b'sport/#', 0), (b'#', 1), (b'sport/tennis/#', 2), (b'+/tennis/#', 0), (b'+', 1), (b'sport/+/player1', 2), (b'/finance', 0), (b'finance/', 1), (b'/finance/', 2), (b'/', 0), (b'+/+', 1), (b'/+', 2), (b'+/', 0), (b'/+/', 1)]"),
            call("Received SUBACK"),
        ],any_order=True)


    def test_on_subscribe(self):
        TestSubscriber._on_subscribe.assert_has_calls([
            call(1, (0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1)),
        ], any_order=False)
        self.assertEqual(self._on_subscribe.call_count, 1)

    
if __name__ == '__main__':
    unittest.main()
