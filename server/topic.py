import server.packet as pk

class Topic():
    _max_qos = pk.QOS_2

    def __init__(self, topic_name=None, app_msg=None, qos=pk.QOS_2, parent=None):
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


    def retain_message(self, identifier):
        packet = pk.Packet()
        packet.packet_type = pk.PUBLISH
        qos_level = min(
            self._qos_level, 
            self._subscriber_qos[identifier],
            Topic._max_qos
        )
        packet.flag_bits = int.from_bytes(pk.QOS_CODE[qos_level], 'big') << 1
        packet.flag_bits = packet.flag_bits | 1
        packet.variable_header.update({'topic_name': self.topic_filter})
        packet.payload.update({'application_message': self._app_msg})
        return packet


    def add(self, client, qos):
        # [MQTT-3.3.1-8]
        self._subscription.add(client)
        try:
            qos = max(self._subscriber_qos[client.identifier], qos)
        except KeyError:
            pass
        finally:
            self._subscriber_qos[client.identifier] =  min([
                self._qos_level, 
                Topic._max_qos, 
                qos])
        if self.retain:
            packet = self.retain_message(client.identifier)
            if packet.qos_level != pk.QOS_0:
                packet.variable_header.update({'packet_identifier': client.new_packet_id()})
            client.conn.write(packet.publish)
            if packet.qos_level != pk.QOS_0:
                packet.flag_bits = packet.flag_bits | 0x08
                client.store_message(packet, 'sent')

        if self.name == b'#':
            self._parent._subscription.add(client)
            try:
                qos = max(self._parent._subscriber_qos[client.identifier], qos)
            except KeyError:
                pass
            finally:
                self._parent._subscriber_qos[client.identifier] =  min([
                    self._parent._qos_level, 
                    Topic._max_qos, 
                    qos])
            if self._parent.retain:
                packet = self._parent.retain_message(client.identifier)
                if packet.qos_level != pk.QOS_0:
                    packet.variable_header.update({'packet_identifier': client.new_packet_id()})
                client.conn.write(packet.publish)
                if packet.qos_level != pk.QOS_0:
                    packet.flag_bits = packet.flag_bits | 0x08
                    client.store_message(packet, 'sent')
    

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


    def __getitem__(self, topic_filter):
        if not isinstance(topic_filter, bytes):
            raise KeyError

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
                if b'#' in self._children[topic_levels[0]]:
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
                    self.clean_up()
            else:
                if packet.retain == '1':
                    topic._app_msg = packet.application_message
                    topic._qos_level = packet.qos_level

                # Save origin
                origin_flag_bits = packet.flag_bits
                try:
                    origin_pk_id = packet.packet_identifier
                except AttributeError:
                    pass
                for subscriber in topic._subscription:
                    qos_level = min(packet.qos_level, 
                        topic._subscriber_qos[subscriber.identifier])
                    packet.flag_bits = int.from_bytes(
                        pk.QOS_CODE[qos_level], 'big'
                    ) << 1
                    if qos_level != pk.QOS_0:
                        packet.variable_header.update(
                            {'packet_identifier': subscriber.new_packet_id()})
                    subscriber.conn.write(packet.publish)
                    if qos_level != pk.QOS_0:
                        # Set DUP for re-send
                        packet.flag_bits = packet.flag_bits | 0x08
                        subscriber.store_message(packet, 'sent')
                # Reset packet
                packet.flag_bits = origin_flag_bits
                if packet.qos_level != pk.QOS_0:
                    packet.variable_header.update({'packet_identifier': origin_pk_id})


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
            buffer += f'\n\t> retain msg: {self._app_msg}, QoS: {self._qos_level}'
        for _, topic in self._children.items():
            buffer += str(topic)
        return buffer