import json


if __name__ == 'packet':
    import topic as tp
    from utility import variable_length_encode, utf8_encoded_string, MQTTProtocolError
elif __name__ == 'server.packet':
    import server.topic as tp
    from server.utility import variable_length_encode, utf8_encoded_string, MQTTProtocolError


# MQTT version
MQTTv311 = b'\x04'


# Packet type
RESERVED = 0
CONNECT = 1
CONNACK = 2 
PUBLISH = 3
PUBACK = 4
PUBREC = 5
PUBREL = 6
PUBCOMP = 7
SUBSCRIBE = 8
SUBACK = 9
UNSUBSCRIBE = 10
UNSUBACK = 11
PINGREQ = 12
PINGRESP = 13
DISCONNECT = 14


# QoS Value
QOS_0 = '00'
QOS_1 = '01'
QOS_2 = '10'


# Return Code
CONNECTION_ACCEPTED = b'\x00'
UNACCECCEPTABLE_PROTOCOL = b'\x01'
IDENTIFIER_REJECTED = b'\x02'
SERVER_UNAVAILABEL = b'\x03'
BAD_USERNAME_PASSWORD = b'\x04'
NOT_AUTHORIZED = b'\x05'


MAXIMUM_QOS0 = b'\x00'
MAXIMUM_QOS1 = b'\x01'
MAXIMUM_QOS2 = b'\x02'
FAILURE = b'\x80'
QOS_CODE = {
    QOS_0: MAXIMUM_QOS0,
    QOS_1: MAXIMUM_QOS1,
    QOS_2: MAXIMUM_QOS2,
}


# Packet type translator
PACKET_NAME = {
    RESERVED: 'RESERVED',
    CONNECT: 'CONNECT',
    CONNACK: 'CONNACK',
    PUBLISH: 'PUBLISH',
    PUBACK: 'PUBACK',
    PUBREC: 'PUBREC',
    PUBREL: 'PUBREL',
    PUBCOMP: 'PUBCOMP',
    SUBSCRIBE: 'SUBSCRIBE',
    SUBACK: 'SUBACK',
    UNSUBSCRIBE: 'UNSUBSCRIBE',
    UNSUBACK: 'UNSUBACK',
    PINGREQ: 'PINGREQ',
    PINGRESP: 'PINGRESP',
    DISCONNECT: 'DISCONNECT',
}

PACKET_RESPONSE = {
    'CONNECT': 'CONNACK',
    'PUBLISH01': 'PUBACK',
    'PUBLISH10': 'PUBREC',
    'PUBREC': 'PUBREL',
    'PUBREL': 'PUBCOMP',
    'SUBSCRIBE': 'SUBACK',
    'UNSUBSCRIBE': 'UNSUBACK',
    'PINGREQ': 'PINGRESP',
}



class Packet():

    def __init__(self, buffer=b'\x00'):
        # Fixed Header
        self._packet_type = int.from_bytes(buffer, 'big') >> 4
        self._flag_bits = int.from_bytes(buffer, 'big') & 0x0f

        # Flag bits
        if self._packet_type in (SUBSCRIBE, UNSUBSCRIBE, PUBREL) and self._flag_bits != 2:
            raise MQTTProtocolError('MQTT-2.2.2-2')
        elif self._packet_type != PUBLISH and self._flag_bits != RESERVED:
            raise MQTTProtocolError('MQTT-2.2.2-2')
        self._remain_length = 0
        self._variable_header = dict()
        self._payload = dict()


    @property
    def packet_type(self):
        return self._packet_type


    @packet_type.setter
    def packet_type(self, value):
        self._packet_type = value


    @property
    def variable_header(self):
        return self._variable_header


    @property
    def payload(self):
        return self._payload


    @property
    def flag_bits(self):
        return self._flag_bits

    
    @flag_bits.setter
    def flag_bits(self, value):
        self._flag_bits = value


    def __str__(self):
        out = '\n[{0}]'.format(PACKET_NAME[self._packet_type])
        out += '\n[Fixed Header]'
        out += '\n\tpacket type: {0}\n\tflags: {1:04b}'.format(
                self._packet_type , self._flag_bits)
        out += '\n[Variable Header]'
        for key, val in self._variable_header.items():
            out += '\n\t{0}: \t{1}'.format(key.replace('_', ' '), val)    
        out += '\n[Payload]'
        for key, val in self._payload.items():
            if isinstance(val, dict):
                out += '\n\t{0}:'.format(str(key, 'utf-8').replace('_', ' '))
                for key0, val0 in val.items():
                    out += '\n\t\t{0} : {1}'.format(str(key0, 'utf-8'), str(val0, 'utf-8'))
            elif isinstance(val, list):
                out += '\n\t{0}:'.format(str(key, 'utf-8').replace('_', ' '))
                for e in val:
                    out += '\n\t\t{0}'.format(str(e, 'utf-8'))
            else:
                out += '\n\t{0}: \t{1}'.format(str(key, 'utf-8').replace('_', ' '), str(val, 'utf-8'))
        return out


    def serialize(self):
        return json.dumps({
            '_packet_type': self._packet_type,
            '_flag_bits': self._flag_bits,
            '_remain_length': self._remain_length,
            '_variable_header': self._variable_header,
            '_payload': self._payload   
        })


    def __getattr__(self, attr):
        try:
            return self._variable_header[str(attr)]
        except KeyError:
            pass
        try:
            return self._payload[str(attr)]
        except KeyError:
            pass

        if self._packet_type == PUBLISH:
            flag_bits = '{0:04b}'.format(self._flag_bits)
            attr = str(attr)
            if attr == 'dup_flag':
                return flag_bits[0]
            elif attr == 'qos_level':
                return flag_bits[1:3]
            elif attr == 'retain':
                return flag_bits[3]
        elif str(attr) == 'qos_level':
            return ''

        raise AttributeError(
            'Packet {0} - {1:04b} does not have "{2}" attribute'.format(PACKET_NAME[self._packet_type], self._flag_bits, attr))


    def connect_request(self, buffer):
        # Variable header
        protocol_name, buffer = utf8_encoded_string(buffer)
        self._variable_header.update({'protocol_name': protocol_name.decode('utf-8')})

        protocol_level, buffer = buffer[0], buffer[1:]
        self._variable_header.update({'protocol_level': protocol_level})


        connect_flag_bits, buffer = '{0:08b}'.format(buffer[0]), buffer[1:]
        self._variable_header.update({
            'username_flag': connect_flag_bits[0],
            'password_flag': connect_flag_bits[1],
            'will_retain': connect_flag_bits[2],
            'will_qos': connect_flag_bits[3:5],
            'will_flag': connect_flag_bits[5],
            'clean_session': connect_flag_bits[6],
            'reserved': connect_flag_bits[7]
        })

        keep_alive, buffer = buffer[0:2], buffer[2:]
        self._variable_header.update({
            'keep_alive': int.from_bytes(keep_alive, 'big')
        })

        # Payload
        client_identifier, buffer = utf8_encoded_string(buffer)
        self._payload.update({'client_identifier': client_identifier.decode('utf-8')})

        if self.will_flag == 1:
            will_topic, buffer = utf8_encoded_string(buffer)
            self._payload.update({'will_topic': will_topic.decode('utf-8')})

            will_message, buffer = utf8_encoded_string(buffer)
            self._payload.update({'will_message': will_message.decode('utf-8')})

        if self.username_flag == '1':
            username, buffer = utf8_encoded_string(buffer)
            self._payload.update({'username': username.decode('utf-8')})

            if self.password_flag == '1':
                password, buffer = utf8_encoded_string(buffer)
                self._payload.update({'password': password.decode('utf-8')})
        return True


    def publish_request(self, buffer):
        # Variable Header
        topic_name, buffer = utf8_encoded_string(buffer)
        self._variable_header.update({'topic_name': topic_name.decode('utf-8')})

        if self.qos_level != QOS_0:
            packet_identifier, buffer = buffer[0:2], buffer[2:]
            self._variable_header.update({
                'packet_identifier': int.from_bytes(packet_identifier, 'big')})

        # Payload
        self._payload.update({'application_message': buffer.decode('utf-8')})


    def puback_request(self, buffer):
        # Variable Header
        packet_identifier, buffer = buffer[0:2], buffer[2:]
        self._variable_header.update({
            'packet_identifier': int.from_bytes(packet_identifier, 'big')})

    
    def pubrel_request(self, buffer):
        # Variable Header
        packet_identifier, buffer = buffer[0:2], buffer[2:]
        self._variable_header.update({
            'packet_identifier': int.from_bytes(packet_identifier, 'big')})


    def pubrec_request(self, buffer):
        # Variable Header
        packet_identifier, buffer = buffer[0:2], buffer[2:]
        self._variable_header.update({
            'packet_identifier': int.from_bytes(packet_identifier, 'big')})


    def pubcomp_request(self, buffer):
        # Variable Header
        packet_identifier, buffer = buffer[0:2], buffer[2:]
        self._variable_header.update({
            'packet_identifier': int.from_bytes(packet_identifier, 'big')})


    def subscribe_request(self, buffer):
        # Variable Header
        packet_identifier, buffer = buffer[0:2], buffer[2:]
        self._variable_header.update({
            'packet_identifier': int.from_bytes(packet_identifier, 'big')})

        # Payload
        while buffer:
            topic_filter, buffer = utf8_encoded_string(buffer)
            requested_qos, buffer = '{0:08b}'.format(buffer[0]), buffer[1:]
            try:
                self._payload['topic_filters'].update(
                    {topic_filter.decode('utf-8'):  requested_qos[6:]}
                )
            except KeyError:
                self._payload.update({'topic_filters': 
                    {topic_filter.decode('utf-8'):  requested_qos[6:]}
                })


    def unsubscribe_request(self, buffer):
        # Variable Header
        packet_identifier, buffer = buffer[0:2], buffer[2:]
        self._variable_header.update({'packet_identifier': int.from_bytes(packet_identifier, 'big')})

        # Payload
        while buffer:
            topic_filter, buffer = utf8_encoded_string(buffer)
            try:
                self._payload['topic_filters'].append(topic_filter.decode('utf-8'))
            except KeyError:
                self._payload.update({'topic_filters': [topic_filter.decode('utf-8')]})

    
    def pingreq_request(self, buffer):
        pass


    def disconnect_request(self, buffer):
        pass


    @property
    def connack(self):
        # Fixed header
        fixed_header = (CONNACK << 4 | RESERVED).to_bytes(1, 'big')
        remain_length = variable_length_encode(2).to_bytes(1, 'big')
        acknowledge_flags = RESERVED

        # Varaible Header
        if self.session_present == '1':
            acknowledge_flags = acknowledge_flags | 0x0001
        if self.return_code != CONNECTION_ACCEPTED:
            acknowledge_flags = acknowledge_flags | 0x0000

        buffer = acknowledge_flags.to_bytes(1, 'big')
        buffer += self.return_code

        return fixed_header + remain_length + buffer


    @property
    def puback(self):
        # Fixed Header
        fixed_header = (PUBACK << 4 | RESERVED).to_bytes(1, 'big')
        remain_length = variable_length_encode(2).to_bytes(1, 'big')
        packet_identifier = self.packet_identifier.to_bytes(2, 'big')
        return fixed_header + remain_length + packet_identifier


    @property
    def pubrec(self):
        # Fixed Header
        fixed_header = (PUBREC << 4 | RESERVED).to_bytes(1, 'big')
        remain_length = variable_length_encode(2).to_bytes(1, 'big')
        packet_identifier = self.packet_identifier.to_bytes(2, 'big')
        return fixed_header + remain_length + packet_identifier


    @property
    def pubrel(self):
        # Fixed Header
        fixed_header = (PUBREL << 4 | RESERVED).to_bytes(1, 'big')
        remain_length = variable_length_encode(2).to_bytes(1, 'big')
        packet_identifier = self.packet_identifier.to_bytes(2, 'big')
        return fixed_header + remain_length + packet_identifier


    @property
    def pubcomp(self):
        # Fixed Header
        fixed_header = (PUBCOMP << 4 | RESERVED).to_bytes(1, 'big')
        remain_length = variable_length_encode(2).to_bytes(1, 'big')
        packet_identifier = self.packet_identifier.to_bytes(2, 'big')
        return fixed_header + remain_length + packet_identifier


    @property
    def suback(self):
        # Fixed Header
        fixed_header = (SUBACK << 4 | RESERVED).to_bytes(1, 'big')
        # Variable Header
        packet_identifier = self.packet_identifier.to_bytes(2, 'big')
        # Payload
        return_code = b''
        for _, qos_level in self.topic_filters.items():
            return_code += QOS_CODE[min(qos_level, tp.Topic._max_qos)]
        remain_length = variable_length_encode(2 + len(return_code)).to_bytes(1, 'big')
        return fixed_header + remain_length + packet_identifier + return_code

    
    @property 
    def publish(self):
        # Fixed Header
        fixed_header = (PUBLISH << 4 | self._flag_bits)
        if self.qos_level == QOS_0:
            fixed_header &= 0xf7
        fixed_header = fixed_header.to_bytes(1, 'big')
        # Variable Header
        topic_name = self.topic_name.encode()
        variable_header = len(topic_name).to_bytes(2, 'big') + topic_name
        if self.qos_level != QOS_0:
            variable_header += self.packet_identifier.to_bytes(2, 'big')
        # Payload
        payload = self.application_message.encode()

        remain_length = variable_length_encode(
            len(variable_header + payload)).to_bytes(1, 'big')
        return fixed_header + remain_length + variable_header + payload


    @property
    def unsuback(self):
         # Fixed Header
        fixed_header = (UNSUBACK << 4 | RESERVED).to_bytes(1, 'big')
        remain_length = variable_length_encode(2).to_bytes(1, 'big')
        # Variable Header
        packet_identifier = self.packet_identifier.to_bytes(2, 'big')
        return fixed_header + remain_length + packet_identifier

    
    @property
    def pingresp(self):
        # Fixed Header
        fixed_header = (PINGRESP << 4 | RESERVED).to_bytes(1, 'big')
        remain_length = variable_length_encode(0).to_bytes(1, 'big')
        return fixed_header + remain_length

    
    @property
    def disconnect(self):
        # Fixed Header
        fixed_header = (DISCONNECT << 4 | RESERVED).to_bytes(1, 'big')
        remain_length = variable_length_encode(0).to_bytes(1, 'big')
        return fixed_header + remain_length