from server.packet import *


class Topic():
    _max_qos = '10'

    def __init__(self, topic_name=None, parent=None):
        self._name = topic_name
        self._app_msg = None
        self._qos_level = '00'
        self._parent = parent
        self._children = dict()
        self._subscription = dict()
        self._subscriber_qos = dict()


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
        self._subscription[client.identifier] = client
        self._subscriber_qos[client.identifier] = min([self._qos_level, Topic._max_qos, qos])
        if self.retain:
            client.conn.write(
                self.publish_packet(client.identifier, retain_bit=True))

    
    def pop(self, client):
        self._subscription.pop(client.identifier)
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
        topic_levels = self.separator(topic_filter)
        if topic_levels[1:]:
            if topic_levels[0] not in self._children:
                self._children[topic_levels[0]] = Topic(topic_name=topic_levels[0], parent=self)
            return self._children[topic_levels[0]][b'/'.join(topic_levels[1:])]
        else:
            try:
                return self._children[topic_levels[0]]
            except KeyError:
                self._children[topic_levels[0]] = Topic(topic_name=topic_levels[0], parent=self)
                return self._children[topic_levels[0]]

    def __setitem__(self, topic_name, packet):
        topic_levels = self.separator(topic_name)
        if topic_levels[1:]:
            if topic_levels[0] not in self._children and packet.retain == '1':
                self._children[topic_levels[0]] = Topic(topic_name=topic_levels[0], parent=self)
            try:
                self._children[topic_levels[0]][b'/'.join(topic_levels[1:])] = packet
            except KeyError:
                pass
            try:
                self._children[topic_levels[0]][b'#'] = packet
            except KeyError:
                pass
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
                if self.retain:
                    subscriber.conn.write(self.publish_packet(subscriber.identifier))
                # [MQTT-3.3.1-12]
                else:
                    subscriber.conn.write(packet.publish)


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
            for id, subscriber in self._subscription.items():
                buffer += f'\n\t> {subscriber} : {self._subscriber_qos[id]}'
        for _, topic in self._children.items():
            buffer += str(topic)
        return buffer