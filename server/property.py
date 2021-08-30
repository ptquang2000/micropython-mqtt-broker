from server.format import *

# Identifier
PAYLOAD_FORMAT_INDICATOR = b'\x01'
MESSAGE_EXPIRY_INTERVAL = b'\x02'
CONTENT_TYPE = b'\x03'
RESPONSE_TOPIC = b'\x08'
CORRELATION_DATA = b'\x09'
SUBSCRIPTION_IDENTIFIER = b'\x0b'
SESSION_EXPIRY_INTERVAL = b'\x11' 
ASSIGNED_CLIENT_IDENTIFIER = b'\x12'
SERVER_KEEP_ALIVE = b'\x13'
AUTHENTICATION_METHOD = b'\x15'
AUTHENTICATION_DATA = b'\x16'
REQUEST_PROBLEM_INFORMATION = b'\x17'
WILL_DELAY_INTERVAL = b'\x18'
REQUEST_RESPONSE_INFORMATION = b'\x19'
RESPONSE_INFORMATION = b'\x1a'
SERVER_REFERENCE = b'\x1c'
REASON_STRING = b'\x1f'
RECEIVE_MAXIMUM = b'\x21'
TOPIC_ALIAS_MAXIMUM = b'\x22'
TOPIC_ALIAS = b'\x23'
MAXIMUM_QOS = b'\x24'
RETAIN_AVAILABLE = b'\x25'
USER_PROPERTY = b'\x26'
MAXIMUM_PACKET_SIZE = b'\x27'
WILDCARD_SUBCRIPTION_AVAILABLE = b'\x28'
SUBCRIPTION_IDENTIFIER_AVAILABLE = b'\x29'
SHARED_SUBCRIPTION_AVAILABLE = b'\x2a'

WILL_PROPERTIES = [
    WILL_DELAY_INTERVAL,
    PAYLOAD_FORMAT_INDICATOR,
    MESSAGE_EXPIRY_INTERVAL,
    CONTENT_TYPE,
    RESPONSE_TOPIC,
    CORRELATION_DATA,
    USER_PROPERTY
]

PROPERTY_DICT = {
    'will_properties': WILL_PROPERTIES
}

PROPERTY_TRANS = {
    PAYLOAD_FORMAT_INDICATOR : 'payload_format_indicator',
    MESSAGE_EXPIRY_INTERVAL : 'message_expiry_interval',
    CONTENT_TYPE : 'content_type',
    RESPONSE_TOPIC : 'response_topic',
    CORRELATION_DATA : 'correlation_data',
    SUBSCRIPTION_IDENTIFIER : 'subcription_identifier',
    SESSION_EXPIRY_INTERVAL : 'session_expiry_interval',
    ASSIGNED_CLIENT_IDENTIFIER : 'assigned_client_identifier',
    SERVER_KEEP_ALIVE : 'server_keep_alive',
    AUTHENTICATION_METHOD : 'authentication_method',
    AUTHENTICATION_DATA : 'authentication_data',
    REQUEST_PROBLEM_INFORMATION : 'request_problem_information',
    WILL_DELAY_INTERVAL : 'will_delay_interval',
    REQUEST_RESPONSE_INFORMATION : 'request_response_information',
    RESPONSE_INFORMATION : 'response_information',
    SERVER_REFERENCE : 'server_reference',
    REASON_STRING : 'reasion_string',
    RECEIVE_MAXIMUM : 'receive_maximum',
    TOPIC_ALIAS : 'topic_alias',
    MAXIMUM_QOS : 'maximum_QoS',
    RETAIN_AVAILABLE : 'retain_availabel',
    USER_PROPERTY : 'user_property',
    MAXIMUM_PACKET_SIZE : 'maximum_packet_size',
    WILDCARD_SUBCRIPTION_AVAILABLE : 'wildcard_subcription_available',
    SUBCRIPTION_IDENTIFIER_AVAILABLE : 'subcription_identifier_available',
    SHARED_SUBCRIPTION_AVAILABLE : 'shared_subcription_available'
}

class Properties():

    # Type
    BYTE = {
        PAYLOAD_FORMAT_INDICATOR,
        REQUEST_PROBLEM_INFORMATION,
        REQUEST_RESPONSE_INFORMATION,
        MAXIMUM_QOS,
        RETAIN_AVAILABLE,
        WILDCARD_SUBCRIPTION_AVAILABLE,
        SUBCRIPTION_IDENTIFIER_AVAILABLE,
        SHARED_SUBCRIPTION_AVAILABLE
    }
    BINARY_DATA = {
        CORRELATION_DATA,
        AUTHENTICATION_DATA
    }
    TWO_BYTE_INTEGER = {
        SERVER_KEEP_ALIVE,
        RECEIVE_MAXIMUM,
        TOPIC_ALIAS_MAXIMUM,
        TOPIC_ALIAS
    }
    FOUR_BYTE_INTEGER = {
        MESSAGE_EXPIRY_INTERVAL,
        SESSION_EXPIRY_INTERVAL,
        WILL_DELAY_INTERVAL,
        MAXIMUM_PACKET_SIZE
    }
    UTF8_ENCODED_STRING = {
        CONTENT_TYPE,
        RESPONSE_TOPIC,
        REASON_STRING,
        SERVER_REFERENCE,
        RESPONSE_INFORMATION,
        AUTHENTICATION_METHOD,
        ASSIGNED_CLIENT_IDENTIFIER
    }
    UTF8_STRING_PAIR = {
        USER_PROPERTY
    }

    def __init__(self, buf, max_length):
        self.buf = buf
        self.properties = dict()
        self.max_length = max_length
        self.length = 0

    def process_property(self):
        identifier, self.buf = PROPERTYE_TRANS[buf[0]], buf[1:]

        if identifier in Identifier.UTF8_STRING_PAIR:
            name, self.buf = utf8_encoded_string(buf)
            self.length += 2 + len(name)
            value, self.buf = utf8_encoded_string(buf)
            self.length += 2 + len(value)
            try:
                self.properties[identifier].append((name,value))
            except KeyError:
                self.properties.update({identifier: [(name, value)]})

        if identifier in self.properties.keys():
            raise ValueError('Protocol Error')

        if identifier in Identifier.BYTE:
            value, self.buf = self.buf[0], self.buf[1:]
            self.properties.update({identifier: value}) 
            self.length += 2

        if identifier in Indetifier.TWO_BYTE_INTEGER:
            value, self.buf = int.from_bytes(self.buf[0:2], 'big'), self.buf[2:]
            self.properties.update({identifier: value}) 
            self.length += 3

        if identifier in Indetifier.FOUR_BYTE_INTEGER:
            value, self.buf = int.from_bytes(self.buf[0:4], 'big'), self.buf[4:]
            self.properties.update({identifier: value}) 
            self.length += 5

        if indentifier in Identifier.UTF8_ENCODED_STRING:
            value, self.buf = utf8_encoded_string(buf)
            self.properties.update({identifier: value}) 
            self.length += 1 + len(string)

        raise ValueError('Identifier {0} not available'.format(identifier))

    def __getattr__(self, name):
        name = str(name)
        if name == 'will_properties':
            while self.length < self.max_length:
                self.process_property()
        else:
            raise AttributeError('Attribute {0} not available'.format(name))
        return self.properties 


