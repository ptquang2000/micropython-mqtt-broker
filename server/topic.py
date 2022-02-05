from server.packet import Packet, QOS_CODE, PUBLISH


class Topic():
    def __init__(self, parent=None, children={}):
        self._name = None
        self._app_msg = None
        self._qos_level = '00'
        self._subscription = []
        self._parent = parent
        self._children = children


    @property
    def qos_level(self):
        return self._qos_level


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


    def add(self, client):
        self._subscription.append(client)
        #  [MQTT-3.3.1-6]
        if self.retain:
            for subscriber in self._subscription:
                # [MQTT-3.3.1-8]
                packet = self.publish_packet
                packet.flag_bits = packet.flag_bits | 1
                subscriber.conn.write(packet)


    @property
    def topic_filter(self):
        if not self._parent: return b''
        else:
            topic_filter = self.topic_filter
            if topic_filter:
                return topic_filter + '/' + self._name
            return topic_filter + self._name


    @property
    def publish_packet(self):
        packet = Packet()
        packet.packet_type = PUBLISH
        # [MQTT-3.3.1-9]
        packet.flag_bits = QOS_CODE[self._qos_level] << 1
        packet.variable_header.update({'topic_name': self.topic_filter})
        packet.payload.update({'application_message': self._app_msg})
        return packet


    def __getitem__(self, topic_filter):
        topic_levels = self.separator(topic_filter)
        if not self._name and self._parent:
            self._name = topic_levels[0]

        if topic_levels[1:]:
            if topic_levels[0] not in self._children:
                self._children[topic_levels[0]] = Topic(parent=self)
            return self._children[topic_levels[0]][b'/'.join(topic_levels[1:])]
        else:
            return self


    def __setitem__(self, topic_name, packet):
        topic_levels = self.separator(topic_name)
        if not self._name and self._parent:
            self._name = topic_levels[0]

        if topic_levels[1:]:
            if topic_levels[0] not in self._children and packet.retain == '1':
                self._children[topic_levels[0]] = Topic(parent=self)
            try:
                self._children[topic_levels[0]][b'/'.join(topic_levels[1:])] = packet
            except KeyError:
                pass
        else:
            # [MQTT-3.3.1-5]
            if packet.retain == '1':
                self._app_msg = packet.application_message
                self._qos_level = packet.qos_level
            for subscriber in self._subscription:
                if self.retain:
                    subscriber.conn.write(self.publish_packet)
                # [MQTT-3.3.1-12]
                else:
                    subscriber.conn.write(packet)


    @staticmethod
    def separator(topic):
        levels = topic.split(b'/')
        if topic[0] == b'/':
            levels[0] = b'/' + levels[0]
        if topic[-1] == b'/':
            levels[-1] = b'/' + levels[-1]
        return levels