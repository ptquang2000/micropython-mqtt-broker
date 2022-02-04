from server.format import *
import re
import _thread


# MQTT version
MQTTv311 = b'\x01'


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
SUBPACK = 9
UNSUBSCRIBE = 10
PINGREQ = 12
PINGRESP = 13
DISCONNECT = 14


# QoS Value
QOS_0 = '00'
QOS_1 = '01'
QOS_2 = '10'


# Return Code
CONNECTION_ACCEPTED = b'\x00'
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
    SUBSCRIBE: 'SUBSCRIBE',
    SUBPACK: 'SUBPACK',
    PINGREQ: 'PINGREQ',
    PINGRESP: 'PINGRESP',
    DISCONNECT: 'DISCONNECT',
}


class Packet():
    def __init__(self, buffer, max_qos=QOS_2):
        # Fixed Header
        self._packet_type = buffer[0] >> 4
        self._flag_bits = buffer[0] & 15

        # [MQTT-3.1.0-1] [MQTT-3.1.0-2]
        # TODO

        # Flag bits
        if self._packet_type in (SUBSCRIBE, UNSUBSCRIBE, PUBREL):
            assert self._flag_bits == 2, 'Flags for subscribe packet must be 2'
        elif self._packet_type != PUBLISH:
            assert self._flag_bits == RESERVED, 'Flags for packet 0'
        self._remain_length = 0
        self._variable_header = dict()
        self._payload = dict()
        self._property = dict()

        # Propeties
        self._max_qos = max_qos
        self._topics = None


    @property
    def topics(self):
        return self._topics

    
    @topics.setter
    def topics(self, topics):
        self._topics = topics


    def __str__(self):
        out = '\n----------\n[{0}]'.format(PACKET_NAME[self._packet_type])
        out += '\n[Fixed Header]'
        out += '\n\tpacket type: {0} \tflags: {1:04b}'.format(
                self._packet_type , self._flag_bits)
        out += '\n[Variable Header]'
        for key, val in self._variable_header.items():
            out += '\n\t{0}: \t{1}'.format(key.replace('_', ' '), val)    
        out += '\n[Payload]'
        for key, val in self._payload.items():
            out += '\n\t{0}: \t{1}'.format(str(key, 'utf-8').replace('_', ' '), str(val, 'utf-8'))
        return out


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

        raise AttributeError(
            'Packet does not have "{0}" attribute'.format(attr))


    # Variable header and Payload Processing
    def __lshift__(self, conn):
        self._remain_length = variable_length_decode(conn)
        request_handler = getattr(self, 
            PACKET_NAME[self._packet_type].lower()+'_request')
        request_handler(conn.recv(self._remain_length))


    def connect_request(self, buffer):
        # Variable header
        protocol_name, buffer = utf8_encoded_string(buffer)
        self._variable_header.update({'protocol_name': protocol_name})

        verion, buffer = buffer[0], buffer[1:]
        self._variable_header.update({'protocol_version': verion})


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
        self._payload.update({'client_identifier': client_identifier})
        if (len(client_identifier) > 23 or 
            not re.match('[0-9a-zA-Z]+$', client_identifier.decode('UTF-8'))):
            # TODO
            print('reject')

        if self.will_flag == 1:
            #  [MQTT-3.1.2-8] - [MQTT-3.1.2-12]
            will_topic, buffer = utf8_encoded_string(buffer)
            self._payload.update({'will_topic': will_topic})

            will_message, buffer = utf8_encoded_string(buffer)
            self._payload.update({'will_message': will_message})

        if self.username_flag == '1':
            username, buffer = utf8_encoded_string(buffer)
            self._payload.update({'username': username})

            if self.password_flag == '1':
                password, buffer = utf8_encoded_string(buffer)
                self._payload.update({'password': password})
        return True


    def publish_request(self, buffer):
        # Variable Header
        topic_name, buffer = utf8_encoded_string(buffer)
        self._variable_header.update({'topic_name': topic_name})

        if self.qos_level != QOS_0:
            packet_identifier, buffer = buffer[0:2], buffer[2:]
            self._variable_header.update({'packet_identifier': packet_identifier})

        # Payload
        self._payload.update({'application_message': buffer})

    
    def pubrel_request(self, buffer):
        # Variable Header
        packet_identifier, buffer = buffer[0:2], buffer[2:]
        self._variable_header.update({'packet_identifier': packet_identifier})


    def subscribe_request(self, buffer):
        # Variable Header
        packet_identifier, buffer = buffer[0:2], buffer[2:]
        self._variable_header.update({'packet_identifier': packet_identifier})

        # Payload
        while buffer:
            topic_filter, buffer = utf8_encoded_string(buffer)
            requested_qos, buffer = '{0:08b}'.format(buffer[0]), buffer[1:]
            self._payload[topic_filter] = requested_qos[6:]

    
    def pingreq_request(self, buffer):
        pass


    def disconnect_request(self, buffer):
        if len(buffer) < 1:
            rc = CONNECTION_ACCEPTED
            self._variable_header.update({'reason_code': rc})
        elif len(buffer) < 2:
            rc = buffer[1]
            self._variable_header.update({'reason_code': rc})
        else:
            properties, buffer = buffer[1], buffer[2:]
            i = 0
            try:
                if properties[i] == SESSION_EXPIRY_INTERVAL:
                    i += 1
                    self._session_expiry_interval = properties[i:i+4]
                    i += 4
                    if self._session_expiry_interval.from_bytes('big') == 0:
                        pass
                    if properties[i] == REASON_STRING:
                        i += 1
                    if properties[i] == REASON_STRING:
                        pass
                    if properties[i] == USER_PROPERTY:
                        i += 1
                        remain = properties[i:]
                        while remain[0] != SERVER_REFERENCE:
                            name, remain = utf8_encoded_string(remain)
                            i += 2 + len(name)
                            value, remain = utf8_encoded_string(remain)
                            i += 2 + len(value)

                    if properties[i] == SERVER_REFERENCE:
                        i += 1
                    if properties[i] == SERVER_REFERENCE:
                        pass
            except IndexError:
                pass
        self._payload.update({'': None})


    # Actions
    def __rshift__(self, conn):
        if CONNECT == self._packet_type:
            conn.write(self.connack)
        elif PUBLISH == self._packet_type and self.qos_level == QOS_1:
            conn.write(self.puback)
        elif PUBLISH == self._packet_type and self.qos_level == QOS_2:
            conn.write(self.pubrec)
        elif PUBREL == self._packet_type:
            conn.write(self.pubcomp)
        elif SUBSCRIBE == self._packet_type:
            conn.write(self.publish + self.subpack)
        elif PINGREQ == self._packet_type:
            conn.write(self.pingresp)

    
    @property
    def connack(self):
        # fixed header
        fixed_header = (CONNACK << 4 | RESERVED).to_bytes(1, 'big')
        remain_length = variable_length_encode(2).to_bytes(1, 'big')
        acknowledge_flags = RESERVED
        return_code = CONNECTION_ACCEPTED

        # [MQTT-3.2.2-1]
        if self.clean_session == '1':
            pass
        # [MQTT-3.2.2-3]
        elif self.clean_session == '0':
            # TODO
            pass
        elif  return_code == CONNECTION_ACCEPTED:
            acknowledge_flags = RESERVED

        buffer = acknowledge_flags.to_bytes(1, 'big')
        buffer += return_code

        return fixed_header + remain_length + buffer


    @property
    def puback(self):
        # Fixed Header
        fixed_header = (PUBACK << 4 | RESERVED).to_bytes(1, 'big')
        remain_length = variable_length_encode(2).to_bytes(1, 'big')
        packet_identifier = self.packet_identifier
        return fixed_header + remain_length + packet_identifier


    @property
    def pubrec(self):
        # Fixed Header
        fixed_header = (PUBREC << 4 | RESERVED).to_bytes(1, 'big')
        remain_length = variable_length_encode(2).to_bytes(1, 'big')
        packet_identifier = self.packet_identifier
        return fixed_header + remain_length + packet_identifier


    @property
    def pubcomp(self):
        # Fixed Header
        fixed_header = (PUBCOMP << 4 | RESERVED).to_bytes(1, 'big')
        remain_length = variable_length_encode(2).to_bytes(1, 'big')
        packet_identifier = self.packet_identifier
        return fixed_header + remain_length + packet_identifier


    @property
    def subpack(self):
        # Fixed Header
        fixed_header = (SUBPACK << 4 | RESERVED).to_bytes(1, 'big')
        remain_length = 2

        # Variable Header
        packet_identifier = self.packet_identifier

        # Payload
        return_code = b''
        for topic_name, qos_level in self._payload.items():
            return_code += QOS_CODE[self.send_qos_level(topic_name, qos_level)]

        remain_length = variable_length_encode(len(return_code)).to_bytes(1, 'big')
        return fixed_header + remain_length + packet_identifier + return_code

    
    @property 
    def publish(self):
        packets = b''
        for topic_name, qos_level in self._payload.items():
            buffer = b''
            # Fixed Header
            fixed_header = (PUBLISH << 4 | RESERVED)
            send_qos_level = self.send_qos_level(topic_name, qos_level)
            if send_qos_level == QOS_0:
                fixed_header &= 0x08
            elif send_qos_level == QOS_1:
                fixed_header |= 0x02
            elif send_qos_level == QOS_2:
                fixed_header |= 0x04
            fixed_header = fixed_header.to_bytes(1, 'big')
            
            # Variable Header
            variable_header = len(topic_name).to_bytes(2, 'big') + topic_name
            # TODO packet identifier

            # Payload
            app_msg = self.topics[topic_name].application_message
            payload = len(app_msg).to_bytes(2, 'big') + app_msg

            packets += fixed_header + variable_header + payload
        
        return packets

 
    def send_qos_level(self, topic_name, qos_level):
        min_qos_level = (self._max_qos 
            if self._max_qos < self.topics[topic_name].qos_level 
            else self.topics[topic_name].qos_level)
        return qos_level if qos_level <= min_qos_level else min_qos_level


    @property
    def pingresp(self):
        # Fixed Header
        fixed_header = (PINGRESP << 4 | RESERVED).to_bytes(1, 'big')
        remain_length = variable_length_encode(0).to_bytes(1, 'big')

        return fixed_header + remain_length
