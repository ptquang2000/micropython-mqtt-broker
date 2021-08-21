import usocket
import _thread
from server import Packet

class Session():
  def __init__(self, conn, addr):
    self.conn = conn
    self.addr = addr
    self.LOCK = _thread.allocate_lock()
    self.client_id = None

  def loop_start(self, sessions):
    _thread.start_new_thread(self.worker, (sessions,))

  def loop_count(self, packets, counter):
    for i in range(counter):
      buf = self.conn.recv(1)
      p = Packet(buf)
      response = p << self.conn
      packets.append(p)
      if response:
        self.conn.write(response)

  def worker(self, sessions):
    while (buf:=self.conn.recv(1)) != b'':
      p = Packet(buf)
      response = p << self.conn
      self.LOCK.acquire()
      self.LOCK.release()
      if response:
        self.conn.write(response)
      print(p)

class Server():
  def __init__(self, ip, port):
    self._ip = ip
    self._port = port
    self.sessions = dict()

    ADDR = usocket.getaddrinfo(self._ip, self._port)[0][-1]
    self._server = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
    self._server.bind(ADDR)

  def loop_start(self, loop_counter):
    packets = list()
    self._server.settimeout(24*60*60.0)
    self._server.listen(1)
    conn, addr = self._server.accept()
    session = Session(conn, addr)
    session.loop_count(packets, loop_counter)
    return packets

  def loop_forever(self):
    self._server.settimeout(24*60*60.0)
    self._server.listen(1)
    print('[SERVER]', self._ip, str(self._port))
    print('Listenning ... ')
    while True:
      conn, addr = self._server.accept()
      session = Session(conn, addr)
      session.loop_start(self.sessions)

