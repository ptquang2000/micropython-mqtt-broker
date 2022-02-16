import json

if __name__ == 'topic':
    import packet as pk
elif __name__ == 'server.topic':
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


    def add(self, client, qos):
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

        if self._name == '#':
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


    def pop(self, client):
        if  self._parent and self.name == '#':
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
            buffer += self._name
            return buffer
        else:
            return ''

    
    def send_retain(self, client, qos):
        packet = pk.Packet()
        packet.packet_type = pk.PUBLISH
        try:
            qos_level = min(
                self._qos_level, 
                self._subscriber_qos[client.identifier],
                Topic._max_qos
            )
        except KeyError:
            qos_level = min(
                self._qos_level, 
                qos,
                Topic._max_qos
            )
        packet.flag_bits = int.from_bytes(pk.QOS_CODE[qos_level], 'big') << 1
        packet.flag_bits = packet.flag_bits | 1
        packet.variable_header.update({'topic_name': self.topic_filter})
        packet.payload.update({'application_message': self._app_msg})
        if packet.qos_level != pk.QOS_0:
            packet.variable_header.update({'packet_identifier': client.new_packet_id()})
        client.conn.write(packet.publish)
        if packet.qos_level != pk.QOS_0:
            packet.flag_bits = packet.flag_bits | 0x08
            client.store_message(packet, 'sent')

    
    def number_sign_retain(self, client, qos):
        if self.retain:
            self.send_retain(client, qos)
        for _, topic in self._children.items():
            topic.number_sign_retain(client, qos)


    def plus_sign_retain(self, topic_levels, client, qos):
        if len(topic_levels) == 1:
            if topic_levels[0] == '+':
                for name, sibling in self._children.items():
                    if name == '+' or not self.retain: continue
                    sibling.send_retain(client, qos)
            else:
                try:
                    self._children[topic_levels[0]].send_retain(client, qos)
                except KeyError:
                    pass
        elif topic_levels[0] != '+':
            try:
                self._children[topic_levels[0]].plus_sign_retain(topic_levels[1:], client, qos)
            except KeyError:
                pass
        else:
            for name, sibling in self._children.items():
                if name == '+': continue
                sibling.plus_sign_retain(topic_levels[1:], client, qos)
            

    def get_topic(self, topic_filter, client=None, qos=None):
        topic_levels = topic_filter.split('/')
        if topic_levels[1:]:
            if topic_levels[0] not in self._children:
                self._children[topic_levels[0]] = Topic(topic_name=topic_levels[0], parent=self)
            topic = self._children[topic_levels[0]].get_topic('/'.join(topic_levels[1:]), client, qos)
            if client and topic_levels[0] == '+':
                for name, sibling in self._children.items():
                    if name == '+': continue
                    sibling.plus_sign_retain(topic_levels[1:], client, qos)
            return topic
        else:
            if topic_levels[0] not in self._children:
                self._children[topic_levels[0]] = Topic(topic_name=topic_levels[0], parent=self)
            if client and self._children[topic_levels[0]].retain:
                self._children[topic_levels[0]].send_retain(client, qos)
            if client and topic_levels[0] == '#':
                self._children[topic_levels[0]]._parent.number_sign_retain(client, qos)
            if client and topic_levels[0] == '+':
                self.plus_sign_retain(topic_levels, client, qos)
            return self._children[topic_levels[0]]


    def send_publish(self, topic_name, packet, retain):
        topic_levels = topic_name.split('/')
        if topic_levels[1:]:
            if retain == '1' and topic_levels[0] not in self._children:
                self._children[topic_levels[0]] = Topic(topic_name=topic_levels[0], parent=self)
            try:
                self._children[topic_levels[0]].send_publish('/'.join(topic_levels[1:]), packet, retain)
            except KeyError:
                pass
            try:
                self._children['+'].send_publish('/'.join(topic_levels[1:]), packet, '0')
            except KeyError:
                pass
            try:
                self._children['#'].send_publish('/'.join(topic_levels[1:]), packet, '0')
            except KeyError:
                pass
        else:
            try:
                topic = self._children[topic_levels[0]]
            except KeyError:
                if retain == '1':
                    self._children[topic_levels[0]] = Topic(
                        topic_name=topic_levels[0], 
                        app_msg=packet.application_message,
                        qos=packet.qos_level,
                        parent=self)
                    self.clean_up()
            else:
                if retain == '1':
                    topic._app_msg = packet.application_message
                    topic._qos_level = packet.qos_level

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
                        packet.variable_header.update({'packet_identifier': subscriber.new_packet_id()})
                    subscriber.conn.write(packet.publish)
                    if qos_level != pk.QOS_0:
                        # Set DUP for re-send
                        packet.flag_bits = packet.flag_bits | 0x08
                        subscriber.store_message(packet, 'sent')
                # Reset packet
                packet.flag_bits = origin_flag_bits
                if packet.qos_level != pk.QOS_0:
                    packet.variable_header.update({'packet_identifier': origin_pk_id})


    def __str__(self):
        buffer = '\n[ {} ]'.format(self.topic_filter)
        if self._subscription:
            for subscriber in self._subscription:
                buffer += '\n\t> {} : {}'.format(subscriber, self._subscriber_qos[subscriber.identifier])
        if self.retain:
            buffer += '\n\t> retain msg: {}, QoS: {}'.format(self._app_msg, self._qos_level)
        for _, topic in self._children.items():
            buffer += str(topic)
        return buffer


    def serialize(self):
        topics = list()
        if self.retain:
            _dict = {
                'topic_filter': self.topic_filter,
                '_app_msg': self._app_msg,
                '_qos_level': self._qos_level
            }
            topics.append(json.dumps(_dict))
        for _, topic in self._children.items():
            topics += topic.serialize()
        return topics