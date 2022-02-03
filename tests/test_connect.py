from libs import unittest
from server.server import Server
import sys

class TestServer(unittest.TestCase):

    def test_basic_connect(self):
        p = server.loop_start(1)[0]
        self.assertEqual(p.packet_type, 1)
        self.assertEqual(p.flags, 0)
        self.assertEqual(p.protocol_name, b'MQTT')
        self.assertEqual(p.protocol_version, 5)
        self.assertEqual(p.username_flag, '0')
        self.assertEqual(p.password_flag, '0')
        self.assertEqual(p.will_retain, '0')
        self.assertEqual(p.will_QoS, '00')
        self.assertEqual(p.clean_start, '1')
        self.assertEqual(p.reserved, '0')
        self.assertEqual(p.keep_alive, 60)
        self.assertEqual(p.property_length, 0, msg='property_length')
        self.assertEqual(p.p_client_id, b'mqtt-client-0')

    def test_auth_connect(self):
        p = server.loop_start(1)[0]
        self.assertEqual(p.packet_type, 1)
        self.assertEqual(p.flags, 0)
        self.assertEqual(p.protocol_name, b'MQTT')
        self.assertEqual(p.username_flag, '1')
        self.assertEqual(p.password_flag, '1')
        self.assertEqual(p.will_retain, '0')
        self.assertEqual(p.will_QoS, '00')
        self.assertEqual(p.clean_start, '1')
        self.assertEqual(p.reserved, '0')
        self.assertEqual(p.keep_alive, 60)
        self.assertEqual(p.property_length, 0)
        self.assertEqual(p.p_client_id, b'mqtt-client-0')
        self.assertEqual(p.p_username, b'mqtt')
        self.assertEqual(p.p_password, b'pass')

SSID = 'Computer Network'
PASSWORD = '1921681251'
PORT = 1883

if __name__ == '__main__':
    if len(sys.argv) > 1:
        ip = sys.argv[1]
        print(f'broker ip address:{ip}')
        server = Server(ip, 1883)
        unittest.main()
        server._server.close()