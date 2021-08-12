import network
import usocket
import _thread

HEADER = 2
VARIABLE_HEADER = 10

def wifiConnection():
  wlan = network.WLAN(network.STA_IF)
  wlan.active(True)

  wlan.connect('Computer Network', '1921681251')
  while wlan.isconnected() == False:
    pass
  print('Connected')
  return wlan

def serverConfig(wlan):
  SERVER = wlan.ifconfig()[0]
  PORT = 1883
  ADDR = usocket.getaddrinfo(SERVER, PORT)[0][-1]
  server = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
  server.bind(ADDR)
  print('SERVER START ' + SERVER + ' ' + str(PORT))
  server.settimeout(30.0)
  server.listen(1)
  return server

def handle_client(conn, addr):
  print('[NEW CONNECTION] ' + str(addr[0]) + ' ' + str(addr[1]))
  connected = True
  while connected == True:
    header = conn.recv(HEADER)
    print('Packet type:', header[0] >> 4, 'Flag:', header[0] & 15)
    if header[0] >> 4 == 14:
      connected = False
    else:
      variable_header = conn.recv(VARIABLE_HEADER)
      # print('VARIABLE HEADER: ',variable_header)
      payload = conn.recv(header[1] - 10)
      print('PAYLOAD: ', payload)
  conn.close()
  
def run():
  wlan = wifiConnection()
  server = serverConfig(wlan)
  while True:
    try:
      print('Listening')
      conn, addr = server.accept()
      _thread.start_new_thread(handle_client, (conn, addr))
    except OSError:
      print('SERVER CLOSE')
      server.close()

run()