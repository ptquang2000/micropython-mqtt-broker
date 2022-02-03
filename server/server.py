import usocket
import _thread
import time
from server.packet import *

class Topic():
    def __init__(self, topics=dict()):
        self._topics = topics
        self.lock = _thread.allocate_lock()


    def __eq__(self, other):
        return self._topics == other


    # Readers
    def __getitem__(self, filters):
        filters = filters.split(b'/')
        value = None
        self.lock.acquire()
        try:
            topic = self._topics
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
        topic = self._topics
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
    clients = dict()

    def __init__(self, conn, addr, topics):
        self._conn = conn
        self._addr = addr
        self._topics = topics

        # Session state
        self._client_id = None
        self._subscriptions = dict()
        self._qos1 = {
            'sent': None,
            'pending': None,
        }
        self._qos2 = {
            'sent': None,
            'pending': None,
            'received': None
        }

        # Thread Lock
        self._lock = _thread.allocate_lock()

        # Interval time
        self._interval_time = 0
        self._next_packet_time = 0

    def clean_session_handler(self, packet):
        self._client_id = packet.client_identifier
        self._lock.acquire()
        if packet.clean_session == '0':
            # [MQTT-3.1.2-5]
            if self._client_id not in Session.clients:
                Session.clients[self._client_id] = self.session_state
            else:
                self.session_state = Session.clients[self._client_id]
        else:
            # [MQTT-3.1.2-6]
            Session.clients.pop(self._client_id, None)
        self._lock.release()

    
    @property
    def session_state(self):
        return {
            'client_identifier': self._client_id,
            'qos1': self._qos1,
            'qos2': self._qos2
        }


    @session_state.setter
    def session_state(self, state):
        self._client_id = state['client_identifier']
        self._qos1 = state['qos1']
        self._qos2 = state['qos2']

    
    def keep_alive_handler(self, packet):
        self._interval_time = packet.keep_alive
        self._next_packet_time = packet.keep_alive
        if packet.keep_alive != 0:
            self._next_packet_time += 0.5 * self._next_packet_time
            current_time = time.localtime()
            self._next_packet_time += current_time[3] * 3600 + current_time[4] * 60 + current_time[5]


    @property
    def remaining_time(self):
        current_time = time.localtime()
        remaining_time = current_time[3] * 3600 + current_time[4] * 60 + current_time[5]
        return int(self._next_packet_time - remaining_time)


    def session_start(self):
        _thread.start_new_thread(self.worker, (self._topics,))


    def worker(self, topics):
        # [MQTT-3.1.2-24]
        while self._interval_time == 0 or self.remaining_time > 0:
            buffer = self._conn.recv(1)
            if buffer == b'':
                continue
            packet = Packet(buffer, topics)
            packet << self._conn
            
            if CONNECT == packet._packet_type:
                self.clean_session_handler(packet)
                self.keep_alive_handler(packet)
            
            print(packet)
            packet >> self._conn
        else:
            # TODO
            print('disconnect')


    def test_session(self, packets, counter):
        for _ in range(counter):
            # [MQTT-3.1.2-24]
            if self._interval_time != 0 and self.remaining_time < 0:
                print('disconnect')
                # TODO

            buffer = self._conn.recv(1)
            packet = Packet(buffer, self._topics)
                        
            packet << self._conn

            if CONNECT == packet._packet_type:
                # [MQTT-3.1.4-3]
                self.clean_session_handler(packet)
                self.keep_alive_handler(packet)

            print(packet)
            packets.append(packet)
            packet >> self._conn


class Server():
    def __init__(self, ip, port='1883'):
        self._ip = ip
        self._port = port
        self._topics = Topic()

        ADDR = usocket.getaddrinfo(self._ip, self._port)[0][-1]
        self._server = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        self._server.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
        self._server.bind(ADDR)

        print('[SERVER]', self._ip, str(self._port))
        print('Listenning ... ')


    def loop_start(self, loop_counter):
        packets = list()
        self._server.settimeout(24*60*60.0)
        self._server.listen(1)
        conn, addr = self._server.accept()
        session = Session(conn, addr, self._topics)
        session.test_session(packets, loop_counter)
        return packets


    def loop_forever(self):
        self._server.settimeout(24*60*60.0)
        self._server.listen(1)

        while True:
            conn, addr = self._server.accept()
            session = Session(conn, addr, self._topics)
            session.session_start()


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        ip = sys.argv[1]
        print(f'Test Broker')
        server = Server(ip)
        server.loop_forever()
        server._server.close()
        print('Server close')
    else:
        print(f'Missing broker IP address')