import usocket
import _thread
import time
from server.packet import *
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
        
        self._store_message = None


    @property
    def subscriptions(self):
        return self._subscriptions


    @property
    def identifier(self):
        return self._client_id


    @property
    def conn(self):
        return self._conn


    @property
    def topics(self):
        return self._topics

    
    def __eq__(self, other):
        return other._client_id == self._client_id


    def __hash__(self):
        return hash(self._client_id)


    def clean_session_handler(self, packet):
        self._client_id = packet.client_identifier
        if packet.clean_session == '0':
            # [MQTT-3.1.2-5]
            if self._client_id not in Client.all:
                Client.all[self._client_id] = self
            else:
                self = Client.all[self._client_id]
        else:
            # [MQTT-3.1.2-6]
            Client.all.pop(self._client_id, None)

    
    def keep_alive_setup(self, packet):
        self._interval_time = packet.keep_alive


    def keep_alive(self):
        self._next_packet_time = int(1.5 * self._interval_time)
        current_time = time.localtime()
        self._next_packet_time += int(current_time[3] * 3600 
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
            self << packet
            print(packet)

            self._lock.acquire()
            self >> packet
            self._lock.release()
            self.keep_alive()
        else:
            print('Disconnect From' + str(self._client_id, 'utf-8'))
            self._conn.close()
            _thread.exit()

    
    def store_message(self, packet):
        self._store_message = packet.publish


    def discard_message(self):
        self._store_message = None


    # Variable header and Payload Processing
    def __lshift__(self, packet):
        packet._remain_length = variable_length_decode(self.conn)
        request_handler = getattr(packet, 
            PACKET_NAME[packet.packet_type].lower()+'_request')
        request_handler(self.conn.recv(packet._remain_length))

        # Post Processing 
        if CONNECT == packet.packet_type:
            self.clean_session_handler(packet)
            self.keep_alive_setup(packet)
        elif PUBLISH == packet.packet_type:
            self.topics[packet.topic_name] = packet
            if packet.qos_level != QOS_0:
                self.store_message(packet)
        elif SUBSCRIBE == packet.packet_type:
            for topic_filter, qos in packet._payload.items():
                topic = self.topics[topic_filter]
                topic.add(self, qos)


    # Actions
    def __rshift__(self, packet):
        if CONNECT == packet.packet_type:
            self._conn.write(packet.connack)
        elif PUBLISH == packet.packet_type and packet.qos_level == QOS_1:
            self._conn.write(packet.puback)
        elif PUBLISH == packet.packet_type and packet.qos_level == QOS_2:
            self.store_message(packet)
            self._conn.write(packet.pubrec)
        elif PUBACK == packet.packet_type:
            self.discard_message()
        elif PUBREC == packet.packet_type:
            self.store_message = packet
            self._conn.write(packet.pubrel)
        elif PUBREL == packet.packet_type:
            self.discard_message()
            self._conn.write(packet.pubcomp)
        elif PUBCOMP == packet.packet_type:
            self.discard_message()
        elif SUBSCRIBE == packet.packet_type:
            self._conn.write(packet.suback)
        elif PINGREQ == packet.packet_type:
            self._conn.write(packet.pingresp)


class Server():
    _topics = Topic()

    def __init__(self, ip, port='1883'):
        self._ip = ip
        self._port = port

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
            print(Client.all)
            conn, addr = self._server.accept()
            client = Client(conn, addr, Server._topics)
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