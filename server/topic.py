from server.packet import *
import _thread


class Topic():
    _max_qos = '10'
    _lock = _thread.allocate_lock()

    def __init__(self, topic_name=None, parent=None):
        self._name = topic_name
        self._app_msg = None
        self._qos_level = '00'
        # [MQTT-3.8.4-3]
        self._subscription = set()
        self._subscriber_qos = dict()
        self._parent = parent
        self._children = dict()


    @property
    def qos_level(self):
        return self._qos_level


    @property
    def subscriber_qos(self):
        return self._subscriber_qos


    @property
    def name(self):
        return self._name


    @name.setter
    def name(self, value):
        self._name = value

    # [MQTT-3.3.1-10]
    @property
    def retain(self):
        return self._app_msg


    def add(self, client, qos):
        # [MQTT-3.3.1-8]
        self._subscription.add(client)
        self._subscriber_qos.update({
            client.identifier: min([self._qos_level, Topic._max_qos, qos])
        })
        if self.retain:
            client._lock.acquire()
            client.conn.write(
                self.publish_packet(client.identifier, retain_bit=True))
            client._lock.release()

    
    def pop(self, client):
        self._subscription.remove(client)
        self._subscriber_qos.pop(client.identifier)


    @property
    def topic_filter(self):
        if self._parent:
            buffer = self._parent.topic_filter
            if buffer:
                buffer += '/'
            buffer += self._name.decode('utf-8')
            return buffer
        else:
            return ''


    def publish_packet(self, identifier, retain_bit=False):
        packet = Packet()
        packet.packet_type = PUBLISH
        packet.flag_bits = QOS_CODE[self._subscriber_qos[identifier]] << 1
        if retain_bit:
            packet.flag_bits |= 1
        packet.variable_header.update({'topic_name': self.topic_filter})
        packet.payload.update({'application_message': self._app_msg})
        return packet.publish


    def __getitem__(self, topic_filter):
        Topic._lock.acquire()
        topic_levels = self.separator(topic_filter)
        if topic_levels[1:]:
            if topic_levels[0] not in self._children:
                self._children[topic_levels[0]] = Topic(topic_name=topic_levels[0], parent=self)
            Topic._lock.release()
            return self._children[topic_levels[0]][b'/'.join(topic_levels[1:])]
        else:
            self._children[topic_levels[0]] = Topic(topic_name=topic_levels[0], parent=self)
            Topic._lock.release()
            return self._children[topic_levels[0]]


    def __setitem__(self, topic_name, packet):
        topic_levels = self.separator(topic_name)
        if topic_levels[1:]:
            if topic_levels[0] not in self._children and packet.retain == '1':
                self._children[topic_levels[0]][b'/'.join(topic_levels[1:])] = Topic(topic_name=topic_levels[0], parent=self)
            try:
                self._children[topic_levels[0]][b'/'.join(topic_levels[1:])] = packet
            except KeyError:
                pass

            #  [MQTT-4.7.1-2]
            try:
                self._children[topic_levels[0]][b'#'] = packet
            except KeyError:
                pass
            
            #  [MQTT-4.7.1-3]
            try:
                self._children[b'+'][b'/'.join(topic_levels[1:])] = packet
            except KeyError:
                pass

        else:
            # [MQTT-3.3.1-5]
            if packet.retain == '1':
                self._app_msg = packet.application_message
                self._qos_level = packet.qos_level

            for subscriber in self._subscription:
                subscriber._lock.acquire()
                if self.retain:
                    subscriber.conn.write(self.publish_packet(subscriber.identifier))
                # [MQTT-3.3.1-12]
                else:
                    subscriber.conn.write(packet.publish)
                subscriber._lock.release()


    @staticmethod
    def separator(topic):
        levels = topic.split(b'/')
        if topic[0] == b'/':
            levels[0] = b'/' + levels[0]
        if topic[-1] == b'/':
            levels[-1] = b'/' + levels[-1]
        return levels


    def __str__(self):
        buffer = ''
        if self._subscription:
            buffer += f'\n[ {self.topic_filter} ]'
            for subscriber in self._subscription:
                buffer += f'\n\t> {subscriber} : {self._subscriber_qos[subscriber.identifier]}'
        for _, topic in self._children.items():
            buffer += str(topic)
        return buffer