import network
import usocket
import _thread
import control_packet

def wifi_conn():
  wlan = network.WLAN(network.STA_IF)
  wlan.active(True)

  wlan.connect('Computer Network', '1921681251')
  while wlan.isconnected() == False:
    pass
  print('Connecting to Wifi Successfully')
  return wlan

def mqtt_server(wlan):
  SERVER = wlan.ifconfig()[0]
  PORT = 1883
  ADDR = usocket.getaddrinfo(SERVER, PORT)[0][-1]
  server = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
  server.bind(ADDR)
  print('SERVER START', SERVER, str(PORT))
  server.settimeout(3600.0)
  server.listen(1)
  return server

  
def run():
  wlan = wifi_conn()
  server = mqtt_server(wlan)
  while True:
    print('Listening ...')
    conn, addr = server.accept()
    _thread.start_new_thread(control_packet.connect, (conn, addr))

run()