from server.format import *
from server.property import *

# Packet type
RESERVED = 0
CONNECT = 1
CONNACK = 2 
PUBLISH = 3
PUBREL = 6
SUBSCRIBE = 8
SUBPACK = 9
UNSUBSCRIBE = 10
PINGREQ = 12
PINGRESP = 13
DISCONNECT = 14

# Reason Code
SUCCESS = b'\x00'
NORMAL_DISCONNECT = b'\x00' 
UNSPECIFIED_ERROR = b'\x80'
MALFORMED_PACKET = b'\x81'
PROTOCOL_ERROR = b'\x82'
IMPLEMENT_SPECIFIC_ERROR = b'\x83'
UNSUPPORTED_PROTOCOL_VERSION = b'\x84'

GRANTED_QOS0 = b'\x00'
GRANTED_QOS1 = b'\x01'
GRANTED_QOS2 = b'\x02'
UNSPECIFIED_ERROR = b'\x80'
NOT_AUTHORIZED = b'\x87'
TOPIC_FILTER_INVALID = b'\x8f'
PACKET_IDENTIFIER_IN_USE = b'\x91'
QUOTA_EXCEEDED = b'\x97'
SHARED_SUBSCRIPTION_NOT_SUPPORTED = b'\x9e'
SUBSCRIPTION_IDENTIFIER_NOT_SUPPORTED = b'\xa1'
WILDCARD_SUBSCRIPTION_NOT_SUPPORTED = b'\xa2'

# Packet type translator
PACKET_TRANS = {
        RESERVED: 'RESERVED',
        CONNECT: 'CONNECT',
        CONNACK: 'CONNACK',
        PUBLISH: 'PUBLISH',
        SUBSCRIBE: 'SUBSCRIBE',
        SUBPACK: 'SUBPACK',
        PINGREQ: 'PINGREQ',
        PINGRESP: 'PINGRESP',
        DISCONNECT: 'DISCONNECT',
        }

class Packet():
    def __init__(self, buf, topics):
        self.packet_type = buf[0] >> 4
        self.flags = buf[0] & 15
        self.checkflags()

        self.remain_length = 0 
        self.topic_storage = topics
        self.variable_header = dict()
        self.payload = dict()
        self.property = dict()

    def checkflags(self):
        if self.packet_type in (SUBSCRIBE, UNSUBSCRIBE, PUBREL):
            assert self.flags == 2, 'Flags for subscribe packet must be 2'
        elif self.packet_type != PUBLISH:
            assert self.flags == RESERVED, 'Flags for packet 0'

    def __str__(self):
        out = '\n-- [{0}]'.format(PACKET_TRANS[self.packet_type])
        out += '\n-- [Fixed Header]'
        out += '\n\tpacket type: {0} \tflags: {1:04b}'.format(
                self.packet_type , self.flags)
        out += '\n-- [Variable Header]'
        for key, val in self.variable_header.items():
            out += '\n\t{0}: \t{1}'.format(key.replace('_', ' '), val)    
        out += '\n-- [Payload]'
        for key, val in self.payload.items():
            out += '\n\t{0}: \t{1}'.format(key.replace('_', ' '), val)    
        return out

    def __getattr__(self, attr):
        try:
            if str(attr)[0:3] == 'pl_':
                return self.payload[str(attr)[3:]]
            if str(attr)[0:5] == 'prop_':
                return self.property[str(attr)[5:]]
            return self.variable_header[str(attr)]
        except KeyError:
            if self.packet_type == PUBLISH:
                flags = '{0:04b}'.format(self.flags)
                attr = str(attr)
                if attr == 'DUP_flag':
                    return flags[0]
                if attr == 'QoS_level':
                    return flags[1:3]
                if attr == 'retain':
                    return flags[3]
            else:
                raise AttributeError('Packet does not have "{0}" attribute'.format(attr))

    def connect_request(self, buf):
        # Variable header
        name, buf = utf8_encoded_string(buf)
        self.variable_header.update({'protocol_name': name})

        ver, buf = buf[0], buf[1:]
        self.variable_header.update({'protocol_version': ver})

        flags, buf = '{0:08b}'.format(buf[0]), buf[1:]
        self.variable_header.update({
            'username_flag': flags[0],
            'password_flag': flags[1],
            'will_retain': flags[2],
            'will_QoS': flags[3:5],
            'will_flag': flags[5],
            'clean_start': flags[6],
            'reserved': flags[7]
            })

        keep_alive, buf = buf[0:2], buf[2:]
        self.variable_header.update({'keep_alive': int.from_bytes(keep_alive, 'big')})

        property_length, buf = variable_byte_integer(buf)
        self.variable_header.update({'property_length': property_length})
        if property_length != 0:
            pass

        # Payload
        client_id, buf = utf8_encoded_string(buf)
        self.payload.update({'client_id': client_id})

        if self.will_flag == 1:
            property_length, buf = variable_byte_integer(buf)
            self.payload.update({'property_length': property_length})

            properties = Properties(buf=buf, max_length=property_length)
            self.payload.update(properties.will_properties)

            will_topic, buf = utf8_encoded_string(buf)
            self.payload.update({'will_topic': will_topic})

            will_payload, buf = utf8_encoded_string(buf)
            self.payload.update({'will_payload': will_payload})

        if self.username_flag == '1':
            username, buf = utf8_encoded_string(buf)
            self.payload.update({'username': username})
        if self.password_flag == '1':
            password, buf = utf8_encoded_string(buf)
            self.payload.update({'password': password})

    @property
    def connack_response(self):
        fixed_header = (CONNACK << 4 | RESERVED).to_bytes(1, 'big')

        conn_ack_flags = RESERVED
        reason_code = SUCCESS

        property_length = variable_byte_integer(0)
        if self.clean_start == 0 and reason_code == SUCCESS:
            conn_ack_flags |= 1
        buf = conn_ack_flags.to_bytes(1, 'big')
        buf += reason_code
        buf += property_length

        remain_length = variable_byte_integer(len(buf))

        return fixed_header + remain_length + buf

    def publish_request(self, buf):
        topic, buf = utf8_encoded_string(buf)
        self.variable_header.update({'topic': topic})

        if self.QoS_level == 0:
            self_id, buf = buf[0:2], buf[2:]

        property_length, buf = variable_byte_integer(buf)
        self.variable_header.update({'property_length': property_length})
        if property_length != 0:
            pass

        self.payload.update({'application_message': buf})
        self.topic_storage[self.topic] = self.pl_application_message

    @property 
    def publish_response(self):
        fixed_header = (PUBLISH << 4 | RESERVED).to_bytes(1, 'big')
        
        buf = b''
        for i, topic_filter in enumerate(self.pl_topic_filters):
            topic_name = topic_filter
            property_length = 0
            payload = self.topic_storage[topic_filter]
            remain_length = 2 + len(topic_name) + 1 + property_length + len(payload)

            buf += fixed_header 
            buf += remain_length.to_bytes(1, 'big')
            buf += b'\x00' + len(topic_name).to_bytes(1, 'big')
            buf += topic_name
            buf += variable_byte_integer(property_length)
            buf += payload
        
        return buf

    def subscribe_request(self, buf):
        identifier, buf = buf[0:2], buf[2:]
        self.variable_header.update({'packet_identifier': identifier})

        property_length, buf = variable_byte_integer(buf)
        self.variable_header.update({'property_length': property_length})
        if property_length != 0:
            pass
        assert len(buf) != 0, 'Protocol Error'

        while len(buf) != 0:
            topic_length, buf = int.from_bytes(buf[0:2], 'big'), buf[2:] 
            topic_filter, topic_option, buf = buf[0:topic_length], buf[topic_length], buf[topic_length+1:] 
            try:
                self.payload['topic_filters'].append(topic_filter)
                self.payload['topic_options'].append(topic_option)
            except KeyError:
                self.payload.update({'topic_filters':[topic_filter]})
                self.payload.update({'topic_options':[topic_option]})

    @property
    def subpack_response(self):
        fixed_header = (SUBPACK << 4 | RESERVED).to_bytes(1, 'big')

        identifier = self.packet_identifier

        property_length = variable_byte_integer(0)
        reason_code = b''
        for i in range(len(self.pl_topic_filters)):
            reason_code += GRANTED_QOS0

        buf = identifier
        buf += property_length
        buf += reason_code
        
        remain_length = variable_byte_integer(len(buf))
        return fixed_header + remain_length + buf

    def disconnect_request(self, buf):
        if len(buf) < 1:
            rc = NORMAL_DISCONNECT
            self.variable_header.update({'reason_code': rc})
        elif len(buf) < 2:
            rc = buf[1]
            self.variable_header.update({'reason_code': rc})
        else:
            properties, buf = buf[1], buf[2:]
            i = 0
            try:
                if property[i] == SESSION_EXPIRY_INTERVAL:
                    i += 1
                    self._session_expiry_interval = property[i:i+4]
                    i += 4
                    if self._session_expiry_interval.from_bytes('big') == 0:
                        pass
                    if property[i] == REASON_STRING:
                        i += 1
                    if property[i] == REASON_STRING:
                        pass
                    if property[i] == USER_PROPERTY:
                        i += 1
                        remain = property[i:]
                        while remain[0] != SERVER_REFERENCE:
                            name, remain = utf8_encoded_string(remain)
                            i += 2 + len(name)
                            value, remain = utf8_encoded_string(remain)
                            i += 2 + len(value)

                    if property[i] == SERVER_REFERENCE:
                        i += 1
                    if property[i] == SERVER_REFERENCE:
                        pass
            except IndexError:
                pass
        self.payload.update({'': None})

    @property
    def process_request(self):
        if CONNECT == self.packet_type:
            return self.connect_request
        elif PUBLISH == self.packet_type:
            return self.publish_request
        elif SUBSCRIBE == self.packet_type:
            return self.subscribe_request
        elif DISCONNECT == self.packet_type:
            return self.disconnect_request
        else:
            raise AttributeError('Packet type strategy not available')

    @property
    def response_packet(self):
        if CONNECT == self.packet_type:
            return self.connack_response
        elif SUBSCRIBE == self.packet_type:
            return self.publish_response + self.subpack_response
        return None

    def __lshift__(self, conn):
        self.remain_length, buf = variable_byte_integer(conn)
        self.process_request(buf)
        return self.response_packet
