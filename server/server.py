import gc
import socket
import _thread
import time
import re
from server.packet import *
from server.topic import Topic


class Client():
    clean_sessions = dict()
    sessions = dict()
    s_lock = _thread.allocate_lock()

    def __init__(self, conn, addr, topics):
        self._conn = conn
        self._addr = addr
        self._topics = topics

        # Session state
        self._client_id = None
        self._subscriptions = set()
        self._qos1 = {
            'sent': None,
            'pending': None,
        }
        self._qos2 = {
            'sent': None,
            'pending': None,
            'received': None
        }

        # Interval time
        self._interval_time = 0
        self._next_packet_time = 0
        
        self._store_message = None


    @property
    def identifier(self):
        return self._client_id


    @property
    def conn(self):
        return self._conn


    @property
    def topics(self):
        return self._topics


    def __str__(self):
        return self.identifier

    
    def __eq__(self, other):
        return other._client_id == self._client_id


    def __hash__(self):
        return hash(self._client_id)


    def clean_session_handler(self, packet):
        if packet.clean_session == '0':
            # [MQTT-3.1.2-5]
            if self._client_id not in Client.clean_sessions:
                Client.clean_sessions[self._client_id] = self
            else:
                self = Client.clean_sessions[self._client_id]
                packet.variable_header.update({'session_present': '1'})
        else:
            # [MQTT-3.1.2-6]
            Client.clean_sessions.pop(self._client_id, None)
            if self._client_id in Client.sessions:
                Client.sessions[self._client_id].disconnect()
                gc.collect()
            Client.sessions[self._client_id] = self

    
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


    def log(self, packet):
        print(f'\n<---- Client ID:\t{str(self.identifier, "utf-8")} ----->')
        print(f'<---- Thread number:\t{_thread.get_ident()} ----->')
        print(packet)

    
    def error_handler(self, e, packet):
        print(e)
        if e.value == 'MQTT-3.1.2-2':
            packet.variable_header.update({'return_code': UNACCECCEPTABLE_PROTOCOL})
            self._conn.write(packet.connack)

        elif e.value == 'MQTT-3.1.3-9':
            packet.variable_header.update({'return_code': IDENTIFIER_REJECTED})
            self._conn.write(packet.connack)

        self.disconnect()
        


    def disconnect(self):
        print(f'\n*** Closing Connection From {self.identifier} ***')
        print(f'Thread {_thread.get_ident()}')
        print(f'Remain Time: {self.remaining_time}')
        for topic_filter in self._subscriptions:
            topic = self.topics[topic_filter]
            topic.pop(self)
        Client.sessions.pop(self._client_id, None)
        self._conn.close()
        gc.collect()

    
    def worker(self):
        # [MQTT-3.1.2-24]
        while self._interval_time == 0 or self.remaining_time > 0:
            try:
                buffer = self._conn.recv(1)
                if buffer == b'':
                    continue
                packet = Packet(buffer)

                try:
                    Client.s_lock.acquire()
                    self << packet
                except MQTTProtocolError as e:
                    self.error_handler(e, packet)
                    break
                else:
                    self >> packet
                    self.log(packet)
                    self.keep_alive()
                finally:
                    Client.s_lock.release()
            except OSError as e:
                if e.value == 104:
                    self.disconnect()
                break
        else:
            self.disconnect()
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

        if CONNECT != packet.packet_type and not self.identifier:
            raise MQTTProtocolError('MQTT-3.1.0-1')

        # Post Processing 
        if CONNECT == packet.packet_type:
            packet.variable_header.update({'session_present': '0'})
            packet.variable_header.update({'return_code': CONNECTION_ACCEPTED})
            self._client_id = packet.client_identifier
            
            if packet.protocol_level != 4:
                raise MQTTProtocolError('MQTT-3.1.2-2')

            if (len(packet.client_identifier) > 23 or 
                not re.match('[0-9a-zA-Z]+$', 
                    packet.client_identifier.decode('UTF-8'))):
                raise MQTTProtocolError('MQTT-3.1.3-5')

            self.clean_session_handler(packet)
            self.keep_alive_setup(packet)

        elif PUBLISH == packet.packet_type:
            self.topics[packet.topic_name] = packet
            if packet.qos_level != QOS_0:
                self.store_message(packet)
        elif SUBSCRIBE == packet.packet_type:
            for topic_filter, qos in packet.topic_filters.items():
                self._subscriptions.add(topic_filter)
                topic = self.topics[topic_filter]
                topic.add(self, qos)
        elif UNSUBSCRIBE == packet.packet_type:
            for topic_filter in packet.topic_filtes:
                self._subscriptions.remove(topic_filter)
                topic = self.topics[topic_filter]
                topic.pop(self)


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
        elif UNSUBSCRIBE == packet.packet_type:
            self._conn.write(packet.unsuback)
        elif PINGREQ == packet.packet_type:
            self._conn.write(packet.pingresp)


class Server():
    _topics = Topic()
    _clean_sessions = dict()
    _sessions = dict()

    def __init__(self, ip, port='1883'):
        self._ip = ip
        self._port = port

        ADDR = socket.getaddrinfo(self._ip, self._port)[0][-1]
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind(ADDR)
        print('[SERVER]', self._ip, str(self._port))
        print('Listenning ... ')


    def loop_forever(self):
        self._server.settimeout(24*60*60.0)
        self._server.listen(1)

        while True:
            conn, addr = self._server.accept()
            client = Client(conn, addr, Server._topics)
            client.session_start()
            self.log()


    def log(self):
        print('\n===== SERVER LOGS =====')
        print('<-- Topics -->')
        print(self._topics)
        print('<-- Clean Session -->')
        for client in Client.clean_sessions:
            print(client)
        print('<-- Session -->')
        for client in Client.sessions:
            print(client)
        print('=======================')


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