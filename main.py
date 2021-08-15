import network
import usocket
import _thread
from connect import connect

SSID = 'Computer Network'
password = '1921681251'
PORT = 1883

class Server():
  def __init__(self):
    self.wlan = self.wifi_conn()
    self.server = self.mqtt_server()

  def wifi_conn(self):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, password)
    while wlan.isconnected() == False:
      pass
    print('Connecting to Wifi Successfully')
    return wlan

  def mqtt_server(self):
    SERVER = self.wlan.ifconfig()[0]
    ADDR = usocket.getaddrinfo(SERVER, PORT)[0][-1]
    server = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
    server.bind(ADDR)
    print('[SERVER START]', SERVER, str(PORT))
    return server

  def start(self):
    self.server.settimeout(24*60*60.0)
    print('Listenning ... ')
    self.server.listen(1)
    while True:
      conn, addr = self.server.accept()
      _thread.start_new_thread(connect, (conn, addr))

if __name__ == '__main__':
  server = Server()
  server.start()