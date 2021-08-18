import network
import usocket
from message import Message

class Server():
  def __init__(self, ssid, password, port):
    self._ssid = ssid
    self._password = password
    self._port = port
    self.wlan = self.wifi_conn()
    self.server = self.mqtt_server()

  def wifi_conn(self):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(self._ssid, self._password)
    while wlan.isconnected() == False:
      pass
    print('Connecting to Wifi Successfully')
    return wlan

  def mqtt_server(self):
    SERVER = self.wlan.ifconfig()[0]
    ADDR = usocket.getaddrinfo(SERVER, self._port)[0][-1]
    server = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
    server.bind(ADDR)
    print('[SERVER START]', SERVER, str(self._port))
    return server

  def start(self):
    self.server.settimeout(24*60*60.0)
    print('Listenning ... ')
    self.server.listen(1)
    while True:
      conn, addr = self.server.accept()
      message = Message(conn, addr)
      message()
