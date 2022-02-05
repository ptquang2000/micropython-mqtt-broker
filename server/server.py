import usocket
import _thread
import time
from server.packet import Packet
from server.topic import Topic


class Client():
    all = dict()
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


    @property
    def conn(self):
        return self._conn


    @property
    def topics(self):
        return self._topics


    def clean_session_handler(self, packet):
        self._client_id = packet.client_identifier
        self._lock.acquire()
        if packet.clean_session == '0':
            # [MQTT-3.1.2-5]
            if self._client_id not in Client.clients:
                Client.all[self._client_id] = self
            else:
                self = Client.all[self._client_id]
        else:
            # [MQTT-3.1.2-6]
            Client.all.pop(self._client_id, None)
        self._lock.release()

    
    def keep_alive_handler(self, packet):
        self._interval_time = packet.keep_alive
        self._next_packet_time = packet.keep_alive
        if packet.keep_alive != 0:
            self._next_packet_time += 0.5 * self._next_packet_time
            current_time = time.localtime()
            self._next_packet_time += (current_time[3] * 3600 
                + current_time[4] * 60 
                + current_time[5])


    @property
    def remaining_time(self):
        current_time = time.localtime()
        remaining_time = (current_time[3] * 3600 
            + current_time[4] * 60 
            + current_time[5])
        return int(self._next_packet_time - remaining_time)


    def session_start(self):
        _thread.start_new_thread(self.worker, ())

    
    def worker(self):
        # [MQTT-3.1.2-24]
        while self._interval_time == 0 or self.remaining_time > 0:
            buffer = self._conn.recv(1)
            if buffer == b'':
                continue
            packet = Packet(buffer)
            packet << self
            print(packet)         
            packet >> self
        else:
            # TODO
            print('Disconnect From' + str(self._client_id, 'utf-8'))


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


    def loop_forever(self):
        self._server.settimeout(24*60*60.0)
        self._server.listen(2)

        while True:
            print('Listenning ... ')
            conn, addr = self._server.accept()
            client = Client(conn, addr, self._topics)
            client.session_start()


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