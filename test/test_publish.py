import unittest
from server import Server

class TestPublish(unittest.TestCase):
  def setUp(self):
    self.p = server.loop_start(2)[1]

  def check_publish_default(self,
      tp=3, dup='0', qos='00', r='0',
      top=b'python/mqtt', pl=0,
      am=b'this is a new messages: 0'):
    self.assertEqual(self.p.packet_type, tp)
    self.assertEqual(self.p.DUP_flag, dup)
    self.assertEqual(self.p.QoS_level, qos)
    self.assertEqual(self.p.retain, r)
    self.assertEqual(self.p.topic, top)
    self.assertEqual(self.p.property_length, pl)
    self.assertEqual(self.p.p_application_message, am)

  def check_save_topic(self):
    topics = {b'python':{b'mqtt':b'this is a new messages: 0'}}
    self.assertEqual(self.p.topic_storage.topics, topics)
    self.assertIs(self.p.topic_storage, server.topics)

  def test_basic_publish(self):
    self.check_publish_default()
    self.check_save_topic()

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

