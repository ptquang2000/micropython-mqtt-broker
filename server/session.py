import _thread

PACKET_TYPE = {
    1: 'CONNECT',
    2: 'CONNACK',
    3: 'PUBLISH',
    12: 'PINGREQ'.
    13: 'PINGRESP'
    14: 'DISCONNECT',
}

def process_utf8(payload):
  OFFSET = 2
  LSB = payload[0]
  MSB = payload[1]
  return payload[LSB+OFFSET:MSB+OFFSET], payload[MSB+OFFSET:] 

def variable_byte_integer(conn):
    multiplier = 1
    value = 0
    try:
        encoded_byte = conn.recv(1)[0]
        value += multiplier * (encoded_byte & 127)
        while 128 & encoded_byte != 0:
            encoded_byte = conn.recv(1)[0]
            value += multiplier * (encoded_byte & 127)
            if multiplier > 3 ** 128:
               return
            mutiplier *= 128
        return value, conn.recv(value)
    except AttributeError:
        try:
            buf = conn
            i = 0
            while 128 & (encoded_byte:=buf[i]) != 0:
                i += 1
                if multiplier > 3 ** 128:
                    return
                value += multiplier * (encoded_byte & 127)
                mutiplier *= 128
            return value, buf[value:]
        except TypeError:
            X = int(conn / 128)
            encoded_byte = conn % 128 
            i = 1
            while X > 0:
                if X > 0:
                    i += 1
                    encoded_byte = encoded_byte | 128
                encoded_byte = X % 128 
                X = int(X / 128)
            return encoded_byte.to_bytes(i, 'big')

def connect_strategy(packet, buf):
    name, buf = process_utf8(buf)
    packet.variable_header.update({'protocol_name': name})
    
    ver, buf = buf[0], buf[1:]
    packet.variable_header.update({'protocol_version': ver})

    flags, buf = '{0:08b}'.format(buf[0]), buf[1:]
    packet.variable_header.update({
        'username_flag': flags[0],
        'password_flag': flags[1],
        'will_retain': flags[2],
        'will_QoS': flags[3:5],
        'will_flag': flags[5],
        'clean_start': flags[6],
        'reserved': flags[7]
        })

    keep_alive, buf = buf[0:2], buf[2:]
    packet.variable_header.update({'keep_alive': int.from_bytes(keep_alive, 'big')})

    property_length, buf = variable_byte_integer(buf)
    packet.variable_header.update({'property_length': property_length})
    if property_length != 0:
        pass

    return buf

def connack_strategy(packet):
    conn_ack_flags = Packet.RESERVED
    reason_code = Packet.SUCCESS

    property_length = variable_byte_integer(0)
    if packet.clean_start == 0 and reason_code == Packet.SUCCESS:
        conn_ack_flags |= 1

    buf = conn_ack_flags.to_bytes(1, 'big')
    buf += reason_code
    buf += property_length
    return buf

def publish_strategy(packet, buf):
    topic, buf = process_utf8(buf)
    packet.variable_header.update({'topic': topic})

    if packet.QoS_level == 0:
        packet_id, buf = buf[0:2], buf[2:]

    property_length, buf = variable_byte_integer(buf)
    packet.variable_header.update({'property_length': property_length})
    if property_length != 0:
        pass
    return buf

def disconnect_strategy(packet, buf):
    if len(buf) < 1:
        rc = Packet.NORMAL_DISCONNECT
        packet.variable_header.update({'reason_code': rc})
    elif len(buf) < 2:
        rc = buf[1]
        packet.variable_header.update({'reason_code': rc})
    else:
        properties, buf = buf[1], buf[2:]
        i = 0
        try:
            if property[i] == Packet.SESSION_EXPIRY_INTERVAL:
                i += 1
                self._session_expiry_interval = property[i:i+4]
                i += 4
            if self._session_expiry_interval.from_bytes('big') == 0:
                pass
            if property[i] == Packet.REASON_STRING:
                i += 1
            if property[i] == Packet.REASON_STRING:
                pass
            if property[i] == Packet.USER_PROPERTY:
                i += 1
                remain = property[i:]
                while remain[0] != Packet.SERVER_REFERENCE:
                    name, remain = process_utf8(remain)
                    i += 2 + len(name)
                    value, remain = process_utf8(remain)
                    i += 2 + len(value)

            if property[i] == Packet.SERVER_REFERENCE:
                i += 1
            if property[i] == Packet.SERVER_REFERENCE:
                pass
        except IndexError:
            pass
    return '' 

class Packet():
    # Packet type
    RESERVED = 0
    CONNECT = 1
    CONNACK = 2 
    PUBLISH = 3
    DISCONNECT = 14

    # Reason Code
    SUCCESS = b'\x00'
    NORMAL_DISCONNECT = b'\x00' 
    UNSPECIFIED_ERROR = b'\x80'
    MALFORMED_PACKET = b'\x81'
    PROTOCOL_ERROR = b'\x82'
    IMPLEMENT_SPECIFIC_ERROR = b'\x83'
    UNSUPPORTED_PROTOCOL_VERSION = b'\x84'

    # Identifier
    PAYLOAD_FORMAT_INDICATOR = b'\x01'
    MESSAGE_EXPIRY_INTERVAL = b'\x02'
    CONTENT_TYPE = b'\x03'
    RESPONSE_TOPIC = b'\x08'
    CORRELATION_DATA = b'\x09'
    SESSION_EXPIRY_INTERVAL = b'\x11' 
    SUBSCRIPTION_IDENTIFIER = b'\x0b'
    SERVER_REFERENCE = b'\x1c'
    REASON_STRING = b'\x1f'
    TOPIC_ALIAS = b'\x23'
    USER_PROPERTY = b'\x26'

    def __init__(self, buf):
        self.packet_type = buf[0] >> 4
        self.flags = buf[0] & 15
        self.remain_length = 0 
        self.variable_header = dict()
        self.payload = b''

    def __str__(self):
        out = '\n[{0}]'.format(PACKET_TYPE[self.packet_type])
        out += '\npacket type: {0} flags: {1:04b}'.format(
               self.packet_type , self.flags)
        for key, val in self.variable_header.items():
            out += '\n{0}: {1}'.format(key.replace('_', ' '), val)    
        return out

    def __getattr__(self, attr):
        try:
            return self.variable_header[str(attr)]
        except KeyError:
            if self.packet_type == Packet.PUBLISH:
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

    @property
    def strategy(self):
        if Packet.CONNECT == self.packet_type:
            return connect_strategy
        elif Packet.PUBLISH == self.packet_type:
            return publish_strategy
        elif Packet.DISCONNECT == self.packet_type:
            return disconnect_strategy
        else:
            raise AttributeError('Packet type strategy not available')

    @property
    def response_strategy(self):
        if Packet.CONNECT == self.packet_type:
            return connack_strategy(self), Packet.CONNACK, Packet.RESERVED
        else:
            raise ValueError('Response action not available')

    @property
    def response_packet(self):
        try:
            response, packet_type, flags = self.response_strategy
        except ValueError:
            return None
        byte1 = (packet_type << 4 | flags).to_bytes(1, 'big')
        remain_length = len(response)
        byte2 = variable_byte_integer(remain_length)
        return byte1 + byte2 + response

    def __lshift__(self, conn):
        self.remain_length, buf = variable_byte_integer(conn)
        self.payload = self.strategy(self, buf)
        return self.response_packet

class Session():
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.start()

    def start(self):
        _thread.start_new_thread(self.worker, ())

    def worker(self):
        while (buf:=self.conn.recv(1)) != b'':
            p = Packet(buf)
            response = p << self.conn
            if response:
                self.conn.write(response)
            print(p)
