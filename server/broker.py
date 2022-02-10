from http import client
import socket
import _thread
import time
import re
import json
import btree
if __name__ == 'server.broker':
    import server.topic as tp
    import server.packet as pk
    from server.utility import MQTTProtocolError, variable_length_decode, current_time
elif __name__ == '__main__':
    import topic as tp
    import packet as pk
    from utility import MQTTProtocolError, variable_length_decode, current_time


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
        self._subscriptions = dict()
        self._sent_queue = dict()
        self._ack_queue = dict()
        self._pending_queue = dict()

        # Interval time
        self._interval_time = 0
        self._next_packet_time = 0


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


    def serialize(self):
        return json.dumps({
            '_client_id': self._client_id,
            '_packet_identifier': self._packet_identifier,
            '_subscriptions': self._subscriptions,
            '_sent_queue': {
                pk_id: packet.serialize() for pk_id, packet in 
                self._sent_queue
            },
            '_ack_queue': {
                pk_id: packet.serialize() 
                for pk_id, packet in self._ack_queue
            },
            '_pending_queue': {
                pk_id: packet.serialize() 
                for pk_id, packet in self._pending_queue
            },
        })


    def clean_session_handler(self, packet):
        if packet.clean_session == '0':
            if self._client_id not in Client.clean_sessions:
                Client.clean_sessions[self._client_id] = self
            else:
                old_session = Client.clean_sessions[self._client_id]
                self._subscriptions = old_session._subscriptions
                for topic_filter, qos in self._subscriptions.items():
                    topic = Client.topics[topic_filter]
                    topic.add(self, qos)
                for pk_id, sent in old_session._sent_queue.items():
                    self._conn.write(sent.publish)
                    self._sent_queue[pk_id] = sent
                for pk_id, pending in old_session._pending_queue.items():
                    self._conn.write(pending.pubrec)
                    self._pending_queue[pk_id] = pending
                for pk_id, ack in old_session._ack_queue.items():
                    self._conn.write(ack.pubrel)
                    self._ack_queue[pk_id] = ack
                Client.clean_sessions.pop(self._client_id)
                del old_session
                Client.clean_sessions[self._client_id] = self
                packet.variable_header.update({'session_present': '1'})
        else:
            Client.clean_sessions.pop(self._client_id, None)
            if self._client_id in Client.sessions:
                Client.sessions[self._client_id].disconnect('Duplicate ID')
            Client.sessions[self._client_id] = self

    
    def keep_alive_setup(self, packet):
        self._interval_time = packet.keep_alive


    def keep_alive(self):
        self._next_packet_time = int(1.5 * self._interval_time)
        self._next_packet_time += current_time()


    @property
    def remaining_time(self):
        return int(self._next_packet_time - current_time())


    def session_start(self):
        _thread.start_new_thread(self.worker, ())


    def log(self, packet):
        print('\n<----- Client ID:\t{} \t----->'.format(str(self.identifier, "utf-8")))
        print('{}'.format(str(packet)))
        print('===== SERVER LOGS =====')
        print('<------ Topics -->', end='')
        print('{}'.format(str(Client.topics)))
        print('<----- Clean Session --->')
        for client in Client.clean_sessions:
            print('{}'.format(str(client)))
        print('<----- Session --------->')
        for client in Client.sessions:
            print('{}'.format(str(client)))
        print('=======================')

    
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
        print('\n*** Closing Connection From {} ***'.format(self.identifier))
        print('Cause: {}'.format(cause))
        print('Remain Time: {0}'.format(self.remaining_time))
        print('Sent Queue')
        for _, packet in self._sent_queue.items():
            print(packet)
        print('Pending Queue')
        for _, packet in self._pending_queue.items():
            print(packet)
        print('Acknownledge Queue')
        for _, packet in self._ack_queue.items():
            print(packet)
        print('*********************************\n')
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
                if not buffer:
                    continue
                Client.s_lock.acquire()
                packet = pk.Packet(buffer)
                try:
                    self << packet
                    self.log(packet)
                except MQTTProtocolError as e:
                    self.error_handler(e, packet)
                    break
                else:
                    self >> packet
                    self.keep_alive()
                finally:
                    Client.s_lock.release()
            except OSError as e:
                self.disconnect(e)
                break
        else:
            self.disconnect('Timeout')
        _thread.exit()


    def store_message(self, packet, state):
        queue = getattr(self, '_{0}_queue'.format(state))
        queue[packet.packet_identifier] = packet


    def discard_message(self, packet_identifier, state):
        queue = getattr(self, '_{0}_queue'.format(state))
        queue.pop(packet_identifier)


    def __lshift__(self, packet):
        # Variable header and Payload Processing
        packet._remain_length = variable_length_decode(self.conn)
        request_handler = getattr(packet, 
            pk.PACKET_NAME[packet.packet_type].lower()+'_request')

        if packet._remain_length != 0:
            request_handler(self.conn.recv(packet._remain_length))
        else:
            request_handler(b'')

        if pk.CONNECT != packet.packet_type and not self.identifier:
            raise MQTTProtocolError('MQTT-3.1.0-1')

        # Actions
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

        elif pk.PUBLISH == packet.packet_type and pk.QOS_2 != packet.qos_level:
            Client.topics[packet.topic_name] = packet

        elif pk.PUBACK == packet.packet_type:
            self.discard_message(packet.packet_identifier, 'sent')

        elif pk.PUBLISH == packet.packet_type and pk.QOS_2 == packet.qos_level:
            self.store_message(packet, 'pending')

        elif pk.PUBREC == packet.packet_type:
            self.discard_message(packet.packet_identifier, 'sent')
            self.store_message(packet, 'ack')

        elif pk.PUBREL == packet.packet_type:
            publish_packet = self._pending_queue[packet.packet_identifier]
            Client.topics[publish_packet.topic_name] = publish_packet
            self.discard_message(packet.packet_identifier, 'pending')

        elif pk.PUBCOMP == packet.packet_type:
            self.discard_message(packet.packet_identifier, 'ack')

        elif pk.SUBSCRIBE == packet.packet_type:
            for topic_filter, qos in packet.topic_filters.items():
                self._subscriptions[topic_filter] = qos
                topic = Client.topics[topic_filter]
                topic.add(self, qos)

        elif pk.UNSUBSCRIBE == packet.packet_type:
            for topic_filter in packet.topic_filters:
                try:
                    self._subscriptions.pop(topic_filter)
                except KeyError:
                    pass
                else:
                    topic = Client.topics[topic_filter]
                    topic.pop(self)

        elif pk.DISCONNECT == packet.packet_type:
            raise MQTTProtocolError('Client Disconnect')


    # Response Packet
    def __rshift__(self, packet):
        packet_name = pk.PACKET_NAME[packet.packet_type] + getattr(packet, 'qos_level')
        try:
            reponse = getattr(packet, pk.PACKET_RESPONSE[packet_name].lower())
        except KeyError:
            pass
        else:
            self._conn.write(reponse)


class Broker():
    def __init__(self, ip, port='1883'):
        self._ip = ip
        self._port = port


    def load(self):
        try:
            with open('topic', 'r+b') as f:
                db = btree.open(f)
                for i in db:
                    topic_json = json.loads(db[i].decode('utf-8'))
                    topic = Client.topics[topic_json['topic_filter']]
                    topic._app_msg = topic_json['_app_msg']
                    topic._qos_level = topic_json['_qos_level']
        except OSError:
            pass
        try:
            with open('session', 'r+b') as f:
                db = btree.open(f)
                for cid in db:
                    client_json = json.loads(db[cid].decode('utf-8'))
                    client = Client(None, None)
                    client._client_id = client_json['_client_id']
                    client._subscriptions = client_json['_subscriptions']
                    for queue_type in ['_sent', 'pending', '_ack']:
                        queue = client_json['{}_queue'.format(queue_type)]
                        packets = dict()
                        for pid in queue:
                            packet = pk.Packet()
                            packet_json = json.loads(queue[pid])
                            for attr in packet_json:
                                setattr(packet, attr, packet_json[attr])
                            packets[pid] = packet
                        setattr(client, '{}_queue'.format(queue_type), packets)
                    Client.clean_sessions[client.identifier] = client
        except OSError:
            pass

    def start(self, timeout=None):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(socket.getaddrinfo(self._ip, self._port)[0][-1])
        self._socket.settimeout(timeout)
        self._socket.listen(5)
        print('[SERVER]', self._ip, str(self._port))
        print('... Listenning ... ')
        while True:
            conn, addr = self._socket.accept()
            client = Client(conn, addr)
            client.session_start()

    
    def stop(self):
        print('[\t\t BROKER CLOSING \t\t]')
        self._socket.close()
        with open('topic', 'w+b') as f:
            db = btree.open(f)
            topics = Client.topics.serialize()
            for i, topic in enumerate(topics):
                db[str(i).encode()] = topic.encode()
        with open('session', 'w+b') as f:
            db = btree.open(f)
            for cid, client in Client.clean_sessions().items():
                db[cid] = client.serialize().encode()


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        ip = sys.argv[1]
        print('Test Broker')
        server = Broker(ip)
        try:
            server.start()
        except KeyboardInterrupt:
            server.stop()
    else:
        print('Missing broker IP address')