import server.packet as pkg

class Topic():
    _max_qos = '10'

    def __init__(self, topic_name=None, app_msg=None, qos='00', parent=None):
        self._name = topic_name
        self._app_msg = app_msg
        self._qos_level = qos
        self._parent = parent
        self._children = dict()
        self._subscription = set()
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


    @property
    def retain(self):
        return self._app_msg


    def add(self, client, qos):
        # [MQTT-3.3.1-8]
        self._subscription.add(client)
        self._subscriber_qos[client.identifier] = min([
            self._qos_level, Topic._max_qos, qos])
        if self.retain:
            client.conn.write(self.retain_message(client.identifier))

        if self.name == b'#':
            self._parent._subscription.add(client)
            self._parent._subscriber_qos[client.identifier] = min(
                [self._parent._qos_level, Topic._max_qos, qos])
            if self._parent.retain:
                client.conn.write(self._parent.retain_message(client.identifier))
    

    def pop(self, client):
        if  self._parent and self.name == b'#':
            self._parent._subscription.remove(client.identifier)
            self._parent._subscriber_qos.pop(client.identifier)

        self._subscription.remove(client.identifier)
        self._subscriber_qos.pop(client.identifier)
        self.clean_up()

    
    def clean_up(self):
        if self._parent and not self.retain and not self._subscription and not self._children:
            self._parent._children.pop(self._name)
            self._parent.clean_up()


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


    def retain_message(self, identifier):
        packet = pkg.Packet()
        packet.packet_type = pkg.PUBLISH
        packet.flag_bits = int.from_bytes(
            pkg.QOS_CODE[self._subscriber_qos[identifier]], 'big') << 1
        packet.flag_bits = packet.flag_bits + 1
        packet.variable_header.update({'topic_name': self.topic_filter})
        packet.payload.update({'application_message': self._app_msg})
        return packet.publish


    def __getitem__(self, topic_filter):
        topic_levels = self.separator(topic_filter)
        if topic_levels[1:]:
            if topic_levels[0] not in self._children:
                self._children[topic_levels[0]] = Topic(
                    topic_name=topic_levels[0], parent=self)
            return self._children[topic_levels[0]][b'/'.join(topic_levels[1:])]
        else:
            try:
                return self._children[topic_levels[0]]
            except KeyError:
                self._children[topic_levels[0]] = Topic(
                    topic_name=topic_levels[0], parent=self)
                return self._children[topic_levels[0]]
                

    def __setitem__(self, topic_name, packet):
        topic_levels = self.separator(topic_name)
        if topic_levels[1:]:
            if topic_levels[0] not in self._children and packet.retain == '1':
                self._children[topic_levels[0]] = Topic(
                    topic_name=topic_levels[0], parent=self)
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
            try:
                topic = self._children[topic_levels[0]]
            except KeyError:
                if packet.retain == '1':
                    self._children[topic_levels[0]] = Topic(
                        topic_name=topic_levels[0], 
                        app_msg=packet.application_message,
                        qos=packet.qos_level,
                        parent=self)
            else:
                if packet.retain == '1':
                    topic._app_msg = packet.application_message
                    topic._qos_level = packet.qos_level
                for subscriber in topic._subscription:
                    qos_level = min(
                        packet.qos_level, 
                        topic._subscriber_qos[subscriber.identifier])
                    packet.flag_bits = int.from_bytes(
                        pkg.QOS_CODE[qos_level], 'big') << 1
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
        buffer = f'\n[ {self.topic_filter} ]'
        if self._subscription:
            for subscriber in self._subscription:
                buffer += f'\n\t> {subscriber} : {self._subscriber_qos[subscriber.identifier]}'
            if self.retain:
                buffer += f'\nRetaine msg: {self._app_msg}, QoS: {self._qos_level}'
        for _, topic in self._children.items():
            buffer += str(topic)
        return buffer