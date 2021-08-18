from server import Server

SSID = 'Computer Network'
password = '1921681251'
PORT = 1883

if __name__ == '__main__':
  server = Server(SSID, password, PORT)
  server.start()