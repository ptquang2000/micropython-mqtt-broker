import unittest
from server import Server

class TestSubscribe(unittest.TestCase):
  def setUp(self):
    self.p = server.loop_start(3)[2]

  def check_subscribe_default(self,
      tp=8, pl=0, fl=2, pi=b'\x00\x02',
      tf = [b'python/mqtt'], to=[0]):
    self.assertEqual(self.p.packet_type, tp)
    self.assertEqual(self.p.flags, fl)
    self.assertEqual(self.p.property_length, pl)
    self.assertEqual(self.p.packet_identifier, pi)
    self.assertEqual(self.p.p_topic_filters, tf)
    self.assertEqual(self.p.p_topic_options, to)

  def check_subscribe_topic(self):
    topics = {b'python':{b'mqtt':b'this is a new messages: 0'}}
    self.assertEqual(self.p.topic_storage.topics, topics)
    self.assertIs(self.p.topic_storage, server.topics)

  def test_basic_subscribe(self):
    self.check_subscribe_default()
    self.check_subscribe_topic()

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

try:
  if __name__ == '__main__':
    server = Server('172.17.0.2', 1883)
    unittest.main()
    server._server.close()
  else:
    import network
    server = Server(wifi_conn().ifconfig()[0], PORT)
    unittest.main()
    server._server.close()
except AssertionError as e:
  print(e)
  server._server.close()

