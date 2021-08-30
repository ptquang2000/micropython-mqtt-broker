import usocket
import _thread
from server import Packet

class Topic():

    def __init__(self, topics=dict()):
        self.topics = topics
        self.lock = _thread.allocate_lock()

    def __eq__(self, other):
        return self.topics == other

    # Readers
    def __getitem__(self, filters):
        filters = filters.split(b'/')
        value = None
        self.lock.acquire()
        try:
            topic = self.topics
            while filters and isinstance(topic[filters[0]], dict):
                topic = topic[filters[0]]
                filters = filters[1:]
            else:
                value = topic[filters[0]]
        except (KeyError, IndexError):
            pass
        self.lock.release()
        return value

    # Writers 
    def __setitem__(self, filters, app_msg):
        self.lock.acquire()
        filters = filters.split(b'/')
        topic = self.topics
        for topic_name in filters[:-1]:
            try:
                if not isinstance(topic[topic_name], dict):
                    raise KeyError
                topic = topic[topic_name]
            except KeyError:
                topic.update({topic_name: dict()})
                topic = topic[topic_name]
        topic.update({filters[-1]: app_msg})
        self.lock.release()

class Session():
    def __init__(self, conn, addr, topics):
        self.conn = conn
        self.addr = addr
        self.client_id = None
        self.topics = topics

    def loop_start(self, sessions):
        _thread.start_new_thread(self.worker, (sessions, self.topics))

    def loop_count(self, packets, counter):
        for i in range(counter):
            buf = self.conn.recv(1)
            p = Packet(buf, self.topics)
            response = p << self.conn
            packets.append(p)
            if response:
                self.conn.write(response)

    def worker(self, sessions, topics):
        while (buf:=self.conn.recv(1)) != b'':
            p = Packet(buf, topics)
            response = p << self.conn
            if response:
                self.conn.write(response)
            print(p)

class Server():
    def __init__(self, ip, port):
        self._ip = ip
        self._port = port
        self.sessions = dict()
        self.topics = Topic()

        ADDR = usocket.getaddrinfo(self._ip, self._port)[0][-1]
        self._server = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        self._server.bind(ADDR)

    def loop_start(self, loop_counter):
        packets = list()
        self._server.settimeout(24*60*60.0)
        self._server.listen(1)
        conn, addr = self._server.accept()
        session = Session(conn, addr, self.topics)
        session.loop_count(packets, loop_counter)
        return packets

    def loop_forever(self):
        self._server.settimeout(24*60*60.0)
        self._server.listen(1)
        print('[SERVER]', self._ip, str(self._port))
        print('Listenning ... ')
        while True:
            conn, addr = self._server.accept()
            session = Session(conn, addr, self.topics)
            session.loop_start(self.sessions)
