import unittest
from server import Server

class TestSubscribe(unittest.TestCase):

  def check_subscribe_default(self,
      pt=8, pl=0, f=2, pi=b'\x00\x02',
      tf = [b'python/mqtt'], to=[0]):
    self.assertEqual(self.p.packet_type, pt)
    self.assertEqual(self.p.flags, f)
    self.assertEqual(self.p.property_length, pl)
    self.assertEqual(self.p.packet_identifier, pi)
    self.assertEqual(self.p.pl_topic_filters, tf)
    self.assertEqual(self.p.pl_topic_options, to)

  def test_basic_subscribe(self):
    self.p = server.loop_start(3)[2]
    self.check_subscribe_default(pi=b'\x00\x02')

  def test_multiple_subscribe(self):
    self.p = server.loop_start(4)[3]
    self.check_subscribe_default(
        tf=[b'python/mqtt', b'java/mqtt'],
        pi=b'\x00\x03',
        to=[0,0])

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
  unittest.main()
  server._server.close()
else:
  import network
  server = Server(wifi_conn().ifconfig()[0], PORT)
  unittest.main()
  server._server.close()

