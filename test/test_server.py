import unittest
from server import Server

class TestConnect(unittest.TestCase):

  def setUp(self):
    self.p = server.loop_start(1)[0]

  def check_connect_default(self,
      tp=1, fl=0, nm=b'MQTT',pv=5, ka=60):
    self.assertEqual(self.p.packet_type, tp)
    self.assertEqual(self.p.flags, fl)
    self.assertEqual(self.p.protocol_name, nm)
    self.assertEqual(self.p.protocol_version, pv)
    self.assertEqual(self.p.keep_alive, ka)

  def check_connect_flag(self,
      usr='0', pss='0', wr='0', qos='00', cs='1', r='0'):
    self.assertEqual(self.p.username_flag, usr)
    self.assertEqual(self.p.password_flag, pss)
    self.assertEqual(self.p.will_retain, wr)
    self.assertEqual(self.p.will_QoS, qos)
    self.assertEqual(self.p.clean_start, cs)
    self.assertEqual(self.p.reserved, r)

  def test_basic_connect(self):
    self.check_connect_default()
    self.check_connect_flag()
    # payload
    self.assertEqual(self.p.property_length, 0)
    self.assertEqual(self.p.p_client_id, b'mqtt-client-0')

  def test_auth_connect(self):
    self.check_connect_default()
    self.check_connect_flag(usr='1',pss='1')
    # payload
    self.assertEqual(self.p.property_length, 0)
    self.assertEqual(self.p.p_client_id, b'mqtt-client-0')
    self.assertEqual(self.p.p_username, b'mqtt')
    self.assertEqual(self.p.p_password, b'pass')

class TestPublic(unittest.TestCase):
  def setUp(self):
    self.p = server.loop_start(2)[1]

  def check_publish_default(self,
      tp=3, dup='0', qos='00', r='0',
      top=b'/python/mqtt', pl=0,
      am=b'this is a new messages: 0'):
    self.assertEqual(self.p.packet_type, tp)
    self.assertEqual(self.p.DUP_flag, dup)
    self.assertEqual(self.p.QoS_level, qos)
    self.assertEqual(self.p.retain, r)
    self.assertEqual(self.p.topic, top)
    self.assertEqual(self.p.property_length, pl)
    self.assertEqual(self.p.p_application_message, am)

  def check_save_topic(self):
    topics = {'python':{'mqtt':('this is a new messages: 0',)}}
    self.assertEqual(self.topics, topics)

  def test_basic_publish(self):
    self.check_publish_default()
    self.check_save_topic(self)

SSID = 'Computer Network'
PASSWORD = '1921681251'
PORT = 1883

def wifi_conn():
  wlan = network.WLAN(network.STA_IF)
  wlan.active(True)
  wlan.connect(SSID, PASSWORD)
  while wlan.isconnected() == False:
    pass
  return wlan

if __name__ == '__main__':
  server = Server('172.17.0.2', 1883)
else:
  import network
  server = Server(wifi_conn().ifconfig()[0], PORT)
unittest.main()
server._server.close()
