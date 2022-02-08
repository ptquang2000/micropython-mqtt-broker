import socket
import _thread
import time
import re
import server.topic as tp
import server.packet as pk
from server.utility import MQTTProtocolError, variable_length_decode, current_time


SENT = 0
ACK = 1
PENDING = 2

class Client():
    clean_sessions = dict()
    sessions = dict()
    s_lock = _thread.allocate_lock()
    topics = tp.Topic()

    def __init__(self, conn, addr):
        self._conn = conn
        self._addr = addr

        # Session state
        self._client_id = None
        self._packet_identifier = 0
        self._subscriptions = set()
        self._sent_queue = dict()
        self._ack_queue = dict()
        self._pending_queue = dict()

        # Interval time
        self._interval_time = 0
        self._next_packet_time = 0
        self._resend_interval = 0


    @property
    def identifier(self):
        return self._client_id


    @property
    def conn(self):
        return self._conn


    def __str__(self):
        return self._client_id

    
    def __eq__(self, id):
        return id == self._client_id


    def __hash__(self):
        return hash(self._client_id)

    
    def new_packet_id(self):
        self._packet_identifier += 1
        return (self._packet_identifier
            if self._packet_identifier < 16 ** 2
            else 1).to_bytes(2, 'big')


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
                Client.sessions[self._client_id].disconnect('Duplicate ID')
            Client.sessions[self._client_id] = self

    
    def keep_alive_setup(self, packet):
        self._interval_time = packet.keep_alive
        self._resend_interval = int(packet.keep_alive * 1.5 / 10)


    def keep_alive(self):
        self._next_packet_time = int(1.5 * self._interval_time)
        self._next_packet_time += current_time()


    @property
    def remaining_time(self):
        return int(self._next_packet_time - current_time())


    def session_start(self):
        _thread.start_new_thread(self.worker, ())


    def log(self, packet):
        print(f'\n<----- Client ID:\t{str(self.identifier, "utf-8")} \t----->')
        # print(f'<----- Object at:\t{hex(id(self))} \t----->')
        # print(f'<----- Thread number:\t{_thread.get_ident()} \t----->')
        print(packet)

    
    def error_handler(self, e, packet):
        if e.value == 'MQTT-3.1.2-2':
            packet.variable_header.update(
                {'return_code': pk.UNACCECCEPTABLE_PROTOCOL})
            self._conn.write(packet.connack)

        elif e.value == 'MQTT-3.1.3-9':
            packet.variable_header.update(
                {'return_code': pk.IDENTIFIER_REJECTED})
            self._conn.write(packet.connack)

        self.disconnect(e)
        


    def disconnect(self, cause):
        print(f'\n*** Closing Connection From {self.identifier} ***')
        print(f'Cause: {cause}')
        print(f'Thread {_thread.get_ident()}')
        print(f'Remain Time: {self.remaining_time}')
        print('Sent Queue')
        for _, info in self._sent_queue.items():
            print(f'Last sent: {info["time"]}')
            print(info['packet'])
        print('Pending Queue')
        for _, info in self._pending_queue.items():
            print(f'Last pending: {info["time"]}')
            print(info['packet'])
        print('Acknownledge Queue')
        for _, info in self._ack_queue.items():
            print(f'Last ack: {info["time"]}')
            print(info['packet'])
        print(f'*********************************\n')
        for topic_filter in self._subscriptions:
            topic = Client.topics[topic_filter]
            topic.pop(self)
        Client.sessions.pop(self._client_id, None)
        self._conn.close()


    def worker(self):
        # [MQTT-3.1.2-24]
        while self._interval_time == 0 or self.remaining_time > 0:
            try:
                buffer = self._conn.recv(1)
                Client.s_lock.acquire()
                packet = pk.Packet(buffer)
                try:
                    self << packet
                except MQTTProtocolError as e:
                    self.error_handler(e, packet)
                    break
                else:
                    self.log(packet)
                    self >> packet
                    self.keep_alive()
                finally:
                    Client.s_lock.release()
            except OSError as e:
                if e.value == 104:
                    self.disconnect(e)
                break
        else:
            self.disconnect('Timeout')
        _thread.exit()


    def store_message(self, packet, state):
        queue = getattr(self, f'_{state}_queue')
        queue[packet.packet_identifier] = {
            'packet': packet,
            'time': current_time(),
        }


    def discard_message(self, packet_identifier, state):
        queue = getattr(self, f'_{state}_queue')
        queue.pop(packet_identifier)


    # Variable header and Payload Processing
    def __lshift__(self, packet):
        packet._remain_length = variable_length_decode(self.conn)
        request_handler = getattr(packet, 
            pk.PACKET_NAME[packet.packet_type].lower()+'_request')

        if packet._remain_length != 0:
            request_handler(self.conn.recv(packet._remain_length))
        else:
            request_handler(b'')

        if pk.CONNECT != packet.packet_type and not self.identifier:
            raise MQTTProtocolError('MQTT-3.1.0-1')

        # Post Processing 
        if pk.CONNECT == packet.packet_type:
            packet.variable_header.update({'session_present': '0'})
            packet.variable_header.update({'return_code': pk.CONNECTION_ACCEPTED})
            self._client_id = packet.client_identifier
            if packet.protocol_level != 4:
                raise MQTTProtocolError('MQTT-3.1.2-2')
            if (len(packet.client_identifier) > 23 or 
                not re.match('[0-9a-zA-Z]+$', 
                    packet.client_identifier.decode('UTF-8'))):
                raise MQTTProtocolError('MQTT-3.1.3-5')
            self.clean_session_handler(packet)
            self.keep_alive_setup(packet)

        elif pk.PUBLISH == packet.packet_type and pk.QOS_1 == packet.qos_level:
            Client.topics[packet.topic_name] = packet

        elif pk.PUBACK == packet.packet_type:
            self.discard_message(packet.packet_identifier, 'sent')

        elif pk.PUBLISH == packet.packet_type and pk.QOS_2 == packet.qos_level:
            self.store_message(packet, 'pending')

        elif pk.PUBREC == packet.packet_type:
            # override publish message in _ack_queue
            self.discard_message(packet.packet_identifier, 'sent')
            self.store_message(packet, 'ack')

        elif pk.PUBREL == packet.packet_type:
            publish_packet = self._pending_queue[packet.packet_identifier]['packet']
            Client.topics[publish_packet.topic_name] = publish_packet
            self.discard_message(packet.packet_identifier, 'pending')

        elif pk.PUBCOMP == packet.packet_type:
            self.discard_message(packet.packet_identifier, 'ack')

        elif pk.SUBSCRIBE == packet.packet_type:
            for topic_filter, qos in packet.topic_filters.items():
                self._subscriptions.add(topic_filter)
                topic = Client.topics[topic_filter]
                topic.add(self, qos)

        elif pk.UNSUBSCRIBE == packet.packet_type:
            for topic_filter in packet.topic_filters:
                try:
                    self._subscriptions.remove(topic_filter)
                except KeyError:
                    pass
                else:
                    topic = Client.topics[topic_filter]
                    topic.pop(self)

        elif pk.DISCONNECT == packet.packet_type:
            raise MQTTProtocolError('Client Disconnect')


    # Actions
    def __rshift__(self, packet):
        # Pre Processing
        packet_name = pk.PACKET_NAME[packet.packet_type] + getattr(packet, 'qos_level')
        try:
            reponse = getattr(packet, pk.PACKET_RESPONSE[packet_name].lower())
        except KeyError:
            pass
        else:
            self._conn.write(reponse)

        cur_time = current_time()
        # QoS 1,2
        for _, pk_info in self._sent_queue.items():
            if cur_time - pk_info['time'] < self._resend_interval:
                continue
            pk_info['time'] = cur_time
            self._conn.write(pk_info['packet'].publish)
        # QoS 2
        for _, pk_info in self._pending_queue.items():
            if cur_time - pk_info['time'] < self._resend_interval:
                continue
            pk_info['time'] = cur_time
            self._conn.write(pk_info['packet'].pubrec)
        # QoS 2
        for _, pk_info in self._ack_queue.items():
            if cur_time - pk_info['time'] < self._resend_interval:
                continue
            pk_info['time'] = cur_time
            self._conn.write(pk_info['packet'].pubrel)


class Server():
    def __init__(self, ip, port='1883'):
        self._ip = ip
        self._port = port

        ADDR = socket.getaddrinfo(self._ip, self._port)[0][-1]
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind(ADDR)
        print('[SERVER]', self._ip, str(self._port))
        print('... Listenning ... ')


    def loop_forever(self):
        self._server.settimeout(24*60*60.0)
        self._server.listen(1)

        while True:
            conn, addr = self._server.accept()
            client = Client(conn, addr)
            client.session_start()


    def log(self, period=10):
        def worker():
            while True:
                print('\n===== SERVER LOGS =====')
                print('<------ Topics -->', end='')
                print(Client.topics)
                print('<----- Clean Session --->')
                for client in Client.clean_sessions:
                    print(client)
                print('<----- Session --------->')
                for client in Client.sessions:
                    print(client)
                print('=======================')
                time.sleep(period)
        _thread.start_new_thread(worker, ())


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        ip = sys.argv[1]
        print(f'Test Broker')
        server = Server(ip)
        server.log(5)
        server.loop_forever()
        server._server.close()
        print('Server close')
    else:
        print(f'Missing broker IP address')